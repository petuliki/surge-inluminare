from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.api.services.voice import list_voices, delete_voice, clone_voice

router = APIRouter(prefix="/api/voices", tags=["voices"])


@router.get("")
def get_voices():
    return {"voices": list_voices()}


@router.post("/clone")
async def create_voice_clone(
    voice_name: str = Form(..., description="Name fuer die neue Stimme"),
    audio_file: UploadFile = File(..., description="Referenz-Audio (WAV, MP3, OPUS, 3-10 Sek.)"),
):
    try:
        safe_name = await clone_voice(voice_name, audio_file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "voice_name": safe_name,
        "message": f"Stimme '{safe_name}' wurde erfolgreich geklont.",
    }


@router.delete("/{name}")
def remove_voice(name: str):
    try:
        delete_voice(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Stimme '{name}' nicht gefunden")
    return {"status": "ok", "message": f"Stimme '{name}' geloescht."}
