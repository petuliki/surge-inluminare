"""
TTS Server - FastAPI wrapper around CosyVoice 2.
Runs as a standalone GPU process on port 8001.
Supports streaming synthesis and zero-shot voice cloning.
"""
import io
import os
import sys
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

# Add CosyVoice to path
COSYVOICE_PATH = os.environ.get("COSYVOICE_PATH", "/opt/cosyvoice")
if os.path.isdir(COSYVOICE_PATH):
    sys.path.insert(0, COSYVOICE_PATH)

app = FastAPI(title="TTS Server")

_model = None
_voices_dir = os.environ.get("VOICES_DIR", "/workspace/voices")


class SynthesizeRequest(BaseModel):
    text: str
    voice: str | None = None  # Voice reference name (without .wav)
    speed: float = 1.0


def get_model():
    global _model
    if _model is None:
        from cosyvoice.cli.cosyvoice import CosyVoice2
        model_dir = os.environ.get("TTS_MODEL_DIR", "/workspace/models/cosyvoice")
        _model = CosyVoice2(model_dir, load_jit=False, load_trt=False)
    return _model


def _get_voice_path(voice_name: str) -> str:
    path = os.path.join(_voices_dir, f"{voice_name}.wav")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Voice reference '{voice_name}' not found")
    return path


@app.on_event("startup")
async def startup():
    get_model()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model is not None}


@app.get("/voices")
def list_voices():
    if not os.path.isdir(_voices_dir):
        return {"voices": []}
    voices = sorted(
        f[:-4] for f in os.listdir(_voices_dir)
        if f.endswith(".wav") and not f.startswith(".")
    )
    return {"voices": voices}


@app.post("/synthesize")
async def synthesize(req: SynthesizeRequest):
    """Synthesize speech. Returns WAV audio as streaming response."""
    model = get_model()

    if req.voice:
        try:
            voice_path = _get_voice_path(req.voice)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Stimme '{req.voice}' nicht gefunden")

        # Zero-shot voice cloning with reference audio
        import torchaudio
        prompt_speech, sr = torchaudio.load(voice_path)

        output_chunks = []
        for chunk in model.inference_zero_shot(
            tts_text=req.text,
            prompt_text="",
            prompt_speech_16k=prompt_speech,
            stream=True,
            speed=req.speed,
        ):
            audio_np = chunk["tts_speech"].numpy().flatten()
            output_chunks.append(audio_np)

        if not output_chunks:
            raise HTTPException(status_code=500, detail="TTS produced no audio")

        audio = np.concatenate(output_chunks)
    else:
        # Default voice (no cloning)
        output_chunks = []
        for chunk in model.inference_sft(
            tts_text=req.text,
            spk_id="default",
            stream=True,
            speed=req.speed,
        ):
            audio_np = chunk["tts_speech"].numpy().flatten()
            output_chunks.append(audio_np)

        if not output_chunks:
            raise HTTPException(status_code=500, detail="TTS produced no audio")

        audio = np.concatenate(output_chunks)

    # Encode as WAV
    import soundfile as sf
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio, 24000, format="WAV", subtype="PCM_16")
    wav_buffer.seek(0)

    return StreamingResponse(
        wav_buffer,
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=speech.wav"},
    )


@app.post("/synthesize_stream")
async def synthesize_stream(req: SynthesizeRequest):
    """Streaming synthesis - yields audio chunks as they're generated."""
    model = get_model()
    import soundfile as sf

    if req.voice:
        try:
            voice_path = _get_voice_path(req.voice)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Stimme '{req.voice}' nicht gefunden")

        import torchaudio
        prompt_speech, sr = torchaudio.load(voice_path)

        async def generate():
            for chunk in model.inference_zero_shot(
                tts_text=req.text,
                prompt_text="",
                prompt_speech_16k=prompt_speech,
                stream=True,
                speed=req.speed,
            ):
                audio_np = chunk["tts_speech"].numpy().flatten()
                buf = io.BytesIO()
                sf.write(buf, audio_np, 24000, format="WAV", subtype="PCM_16")
                yield buf.getvalue()
    else:
        async def generate():
            for chunk in model.inference_sft(
                tts_text=req.text,
                spk_id="default",
                stream=True,
                speed=req.speed,
            ):
                audio_np = chunk["tts_speech"].numpy().flatten()
                buf = io.BytesIO()
                sf.write(buf, audio_np, 24000, format="WAV", subtype="PCM_16")
                yield buf.getvalue()

    return StreamingResponse(generate(), media_type="audio/wav")


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("TTS_HOST", "127.0.0.1")
    port = int(os.environ.get("TTS_PORT", "8001"))
    uvicorn.run(app, host=host, port=port)
