from fastapi import APIRouter
from app.api.services.character import read_system_prompt, write_system_prompt
from app.api.models.schemas import SystemPromptUpdate

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/system-prompt")
def get_system_prompt():
    return {"content": read_system_prompt()}


@router.post("/system-prompt")
def set_system_prompt(data: SystemPromptUpdate):
    write_system_prompt(data.content)
    return {"status": "ok", "message": "System-Prompt aktualisiert."}
