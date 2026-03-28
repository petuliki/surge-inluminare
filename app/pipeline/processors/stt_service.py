"""
Pipecat STT Service - wraps the faster-whisper HTTP server at localhost:8002.
"""
import io
import struct
import httpx
import numpy as np
from pipecat.services.ai_services import STTService
from pipecat.frames.frames import (
    Frame,
    TranscriptionFrame,
    InterimTranscriptionFrame,
    ErrorFrame,
)


class FasterWhisperHTTPService(STTService):
    """STT service that sends audio to the faster-whisper HTTP server."""

    def __init__(self, *, base_url: str = "http://127.0.0.1:8002", language: str = "de", **kwargs):
        super().__init__(**kwargs)
        self._base_url = base_url
        self._language = language
        self._client = httpx.AsyncClient(timeout=10)

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Send audio bytes to STT server and yield transcription frames."""
        try:
            response = await self._client.post(
                f"{self._base_url}/transcribe_audio",
                content=audio,
                headers={"Content-Type": "application/octet-stream"},
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get("text", "").strip()
                if text:
                    yield TranscriptionFrame(text=text, user_id="user", timestamp="")
            else:
                yield ErrorFrame(f"STT error: {response.status_code}")
        except Exception as e:
            yield ErrorFrame(f"STT connection error: {e}")

    async def cleanup(self):
        await self._client.aclose()
        await super().cleanup()
