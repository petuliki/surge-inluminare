"""
WebSocket transport for Pipecat pipeline.
Handles audio I/O between browser and Pipecat.
"""
import json
import struct
import asyncio
import numpy as np
from fastapi import WebSocket


class WebSocketAudioTransport:
    """Bridges a FastAPI WebSocket to Pipecat's audio pipeline."""

    def __init__(self, websocket: WebSocket, sample_rate: int = 16000):
        self.ws = websocket
        self.sample_rate = sample_rate
        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._running = False

    async def start(self):
        self._running = True
        await self.ws.accept()

    async def stop(self):
        self._running = False

    async def receive_audio(self) -> bytes | None:
        """Receive audio bytes from the WebSocket client."""
        try:
            data = await asyncio.wait_for(self.ws.receive_bytes(), timeout=0.1)
            return data
        except asyncio.TimeoutError:
            return None
        except Exception:
            self._running = False
            return None

    async def send_audio(self, audio_bytes: bytes, sample_rate: int = 24000):
        """Send audio bytes back to the client as base64-encoded WAV chunks."""
        import base64
        import io
        import soundfile as sf

        pcm16 = np.frombuffer(audio_bytes, dtype=np.int16)
        buf = io.BytesIO()
        sf.write(buf, pcm16, sample_rate, format="WAV", subtype="PCM_16")
        b64 = base64.b64encode(buf.getvalue()).decode()

        await self.ws.send_json({
            "type": "audio_chunk",
            "data": b64,
            "sample_rate": sample_rate,
        })

    async def send_event(self, event_type: str, data: dict | None = None):
        """Send a JSON event to the client."""
        msg = {"type": event_type}
        if data:
            msg.update(data)
        await self.ws.send_json(msg)

    @property
    def is_running(self) -> bool:
        return self._running
