import os
import shutil
import subprocess
import tempfile
from app.api.config import settings

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".opus"}


def list_voices() -> list[str]:
    d = settings.voices_dir
    if not os.path.isdir(d):
        return []
    return sorted(
        f[:-4] for f in os.listdir(d)
        if f.endswith(".wav") and not f.startswith(".")
    )


def delete_voice(name: str) -> None:
    path = os.path.join(settings.voices_dir, f"{name}.wav")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Voice '{name}' not found")
    os.remove(path)


def save_and_convert_audio(upload_path: str, ext: str, voice_name: str) -> str:
    os.makedirs(settings.voices_dir, exist_ok=True)
    dest_wav = os.path.join(settings.voices_dir, f"{voice_name}.wav")

    if ext == ".wav":
        # Re-encode to ensure 24kHz mono PCM16
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", upload_path,
             "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", dest_wav],
            capture_output=True, timeout=60,
        )
        if result.returncode != 0:
            shutil.copy2(upload_path, dest_wav)
    else:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", upload_path,
             "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", dest_wav],
            capture_output=True, timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Audio conversion failed: {result.stderr.decode(errors='replace')}"
            )

    return dest_wav


async def clone_voice(voice_name: str, audio_file) -> str:
    safe_name = "".join(c for c in voice_name if c.isalnum() or c in "-_").lower()
    if not safe_name:
        raise ValueError("Ungueltiger Stimmenname")

    ext = os.path.splitext(audio_file.filename or "")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Nicht unterstuetztes Format. Erlaubt: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp_path = tmp.name
        shutil.copyfileobj(audio_file.file, tmp)

    try:
        save_and_convert_audio(tmp_path, ext, safe_name)
    finally:
        os.unlink(tmp_path)

    return safe_name
