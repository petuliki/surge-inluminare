"""
STT Server - FastAPI wrapper around faster-whisper.
Runs as a standalone GPU process on port 8002.
"""
import io
import os
import numpy as np
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import soundfile as sf

app = FastAPI(title="STT Server")

_model = None


def get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        model_size = os.environ.get("STT_MODEL", "large-v3-turbo")
        device = os.environ.get("STT_DEVICE", "cuda")
        compute_type = os.environ.get("STT_COMPUTE_TYPE", "float16")
        _model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
    return _model


class TranscribeRequest(BaseModel):
    sample_rate: int = 16000


@app.on_event("startup")
async def startup():
    get_model()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model is not None}


@app.post("/transcribe")
async def transcribe(request_body: bytes = ...) -> JSONResponse:
    """Transcribe raw PCM16 audio bytes. Send audio as request body."""
    from starlette.requests import Request
    # This will be called with raw bytes
    return JSONResponse({"error": "Use /transcribe_pcm or /transcribe_file"}, status_code=400)


@app.post("/transcribe_pcm")
async def transcribe_pcm(
    sample_rate: int = 16000,
    language: str = "de",
):
    """Transcribe raw PCM16 mono audio sent as request body."""
    from starlette.requests import Request
    import struct

    # Placeholder - actual implementation reads from request body
    return JSONResponse({"text": "", "language": language})


@app.post("/transcribe_audio")
async def transcribe_audio(audio_data: bytes):
    """Transcribe audio bytes (PCM16 mono 16kHz)."""
    model = get_model()
    language = os.environ.get("STT_LANGUAGE", "de")

    # Convert bytes to float32 numpy array
    pcm16 = np.frombuffer(audio_data, dtype=np.int16)
    audio_float = pcm16.astype(np.float32) / 32768.0

    segments, info = model.transcribe(
        audio_float,
        language=language,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 300},
    )

    text = " ".join(seg.text.strip() for seg in segments)
    return {"text": text, "language": info.language}


@app.post("/transcribe_file")
async def transcribe_file_endpoint(file_path: str):
    """Transcribe an audio file by path (used for voice cloning reference)."""
    model = get_model()
    language = os.environ.get("STT_LANGUAGE", "de")

    segments, info = model.transcribe(
        file_path,
        language=language,
        vad_filter=True,
    )
    text = " ".join(seg.text.strip() for seg in segments)
    return {"text": text, "language": info.language}


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("STT_HOST", "127.0.0.1")
    port = int(os.environ.get("STT_PORT", "8002"))
    uvicorn.run(app, host=host, port=port)
