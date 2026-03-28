"""
Pipecat TTS Service - wraps the CosyVoice 2 HTTP server at localhost:8001.
"""
import io
import httpx
import numpy as np
from pipecat.services.ai_services import TTSService
from pipecat.frames.frames import Frame, AudioRawFrame, ErrorFrame


class CosyVoiceHTTPService(TTSService):
    """TTS service that calls the CosyVoice 2 HTTP server for synthesis."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8001",
        voice: str | None = None,
        sample_rate: int = 24000,
        **kwargs,
    ):
        super().__init__(sample_rate=sample_rate, **kwargs)
        self._base_url = base_url
        self._voice = voice
        self._client = httpx.AsyncClient(timeout=30)

    def set_voice(self, voice: str | None):
        self._voice = voice

    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        """Send text to TTS server and yield audio frames."""
        try:
            response = await self._client.post(
                f"{self._base_url}/synthesize",
                json={"text": text, "voice": self._voice, "speed": 1.0},
            )
            if response.status_code == 200:
                # Parse WAV data
                wav_bytes = response.content
                import soundfile as sf
                audio_data, sr = sf.read(io.BytesIO(wav_bytes), dtype="int16")
                yield AudioRawFrame(
                    audio=audio_data.tobytes(),
                    sample_rate=sr,
                    num_channels=1,
                )
            else:
                yield ErrorFrame(f"TTS error: {response.status_code}")
        except Exception as e:
            yield ErrorFrame(f"TTS connection error: {e}")

    async def cleanup(self):
        await self._client.aclose()
        await super().cleanup()
