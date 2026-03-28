"""
Pipecat Voice Pipeline - orchestrates STT -> LLM -> TTS
with Silero VAD for turn detection and barge-in support.
"""
import asyncio
import json
import io
import logging
import struct
import numpy as np
import httpx
from fastapi import WebSocket, WebSocketDisconnect

from app.api.config import settings
from app.api.services.character import build_system_message
from app.pipeline.transport import WebSocketAudioTransport

logger = logging.getLogger(__name__)


class SentenceAccumulator:
    """Accumulates LLM tokens into complete sentences for TTS."""

    def __init__(self, min_chars: int = 15):
        self._buffer = ""
        self._min_chars = min_chars

    def add(self, token: str) -> str | None:
        self._buffer += token
        if len(self._buffer) >= self._min_chars:
            for end in [".", "!", "?", "...", "\n"]:
                idx = self._buffer.rfind(end)
                if idx >= 0:
                    sentence = self._buffer[: idx + len(end)].strip()
                    self._buffer = self._buffer[idx + len(end):]
                    if sentence:
                        return sentence
        return None

    def flush(self) -> str | None:
        text = self._buffer.strip()
        self._buffer = ""
        return text if text else None


async def _transcribe(audio_bytes: bytes) -> str:
    """Send audio to STT server and get transcription."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{settings.stt_host}/transcribe_audio",
            content=audio_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )
        if resp.status_code == 200:
            return resp.json().get("text", "").strip()
    return ""


async def _llm_stream(messages: list[dict]):
    """Stream tokens from vLLM server."""
    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream(
            "POST",
            f"{settings.vllm_host}/v1/chat/completions",
            json={
                "model": settings.vllm_model,
                "messages": messages,
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens,
                "stream": True,
            },
        ) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


async def _synthesize(text: str, voice: str | None) -> bytes | None:
    """Get synthesized audio from TTS server."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.tts_host}/synthesize",
            json={"text": text, "voice": voice, "speed": 1.0},
        )
        if resp.status_code == 200:
            return resp.content
    return None


async def run_pipeline(websocket: WebSocket):
    """Main voice pipeline loop. One instance per WebSocket connection."""
    transport = WebSocketAudioTransport(websocket)
    await transport.start()

    # Parse query params
    character = websocket.query_params.get("character", "")
    voice = websocket.query_params.get("voice", None)
    if voice == "":
        voice = None

    # Build system message
    system_message = build_system_message(character)
    history: list[dict] = []
    if system_message:
        history.append({"role": "system", "content": system_message})

    await transport.send_event("state", {"state": "auscultans"})
    logger.info(f"Pipeline started: character={character}, voice={voice}")

    # Audio accumulation buffer (for VAD)
    audio_buffer = bytearray()
    silence_frames = 0
    speech_detected = False
    FRAME_SIZE = 512  # 16kHz * 32ms
    SILENCE_THRESHOLD = settings.vad_min_silence_ms // 32  # frames of silence to end turn
    is_speaking = False  # Agent is currently outputting audio

    try:
        while transport.is_running:
            try:
                data = await asyncio.wait_for(websocket.receive(), timeout=0.05)
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                break

            if "bytes" in data:
                raw_audio = data["bytes"]

                # If agent is speaking and user starts talking -> barge-in
                if is_speaking:
                    # Simple energy-based barge-in detection
                    pcm = np.frombuffer(raw_audio, dtype=np.int16)
                    energy = np.abs(pcm).mean()
                    if energy > 500:
                        is_speaking = False
                        await transport.send_event("barge_in")
                        await transport.send_event("state", {"state": "auscultans"})
                    continue

                audio_buffer.extend(raw_audio)

                # Simple energy-based VAD
                pcm = np.frombuffer(raw_audio, dtype=np.int16)
                energy = np.abs(pcm).mean()

                if energy > 300:
                    speech_detected = True
                    silence_frames = 0
                elif speech_detected:
                    silence_frames += 1

                # End of turn detected
                if speech_detected and silence_frames >= SILENCE_THRESHOLD:
                    utterance_bytes = bytes(audio_buffer)
                    audio_buffer.clear()
                    speech_detected = False
                    silence_frames = 0

                    # Process utterance
                    await transport.send_event("state", {"state": "cogitans"})

                    # 1. STT
                    text = await _transcribe(utterance_bytes)
                    if not text:
                        await transport.send_event("state", {"state": "auscultans"})
                        continue

                    await transport.send_event("transcript", {"role": "user", "text": text})
                    history.append({"role": "user", "content": text})

                    # 2. LLM streaming + 3. TTS per sentence
                    await transport.send_event("state", {"state": "loquitur"})
                    is_speaking = True

                    accumulator = SentenceAccumulator()
                    full_response = ""

                    async for token in _llm_stream(history):
                        full_response += token
                        sentence = accumulator.add(token)
                        if sentence and is_speaking:
                            wav_data = await _synthesize(sentence, voice)
                            if wav_data:
                                await transport.send_audio(wav_data, 24000)

                    # Flush remaining text
                    remaining = accumulator.flush()
                    if remaining and is_speaking:
                        wav_data = await _synthesize(remaining, voice)
                        if wav_data:
                            await transport.send_audio(wav_data, 24000)

                    if full_response:
                        await transport.send_event("transcript", {
                            "role": "assistant", "text": full_response,
                        })
                        history.append({"role": "assistant", "content": full_response})

                    # Trim history
                    max_turns = settings.max_history_turns * 2  # user + assistant per turn
                    system_msgs = [m for m in history if m["role"] == "system"]
                    chat_msgs = [m for m in history if m["role"] != "system"]
                    if len(chat_msgs) > max_turns:
                        chat_msgs = chat_msgs[-max_turns:]
                    history = system_msgs + chat_msgs

                    is_speaking = False
                    await transport.send_event("state", {"state": "auscultans"})

            elif "text" in data:
                msg = json.loads(data["text"])
                if msg.get("type") == "stop":
                    break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception(f"Pipeline error: {e}")
    finally:
        logger.info("Pipeline stopped")
