from fastapi import APIRouter
from app.api.models.schemas import SessionConfig

router = APIRouter(prefix="/api/config", tags=["config"])

_active_config = SessionConfig()


@router.get("")
def get_config():
    return _active_config.model_dump()


@router.post("")
def update_config(data: SessionConfig):
    global _active_config
    updates = data.model_dump(exclude_none=True)
    current = _active_config.model_dump()
    current.update(updates)
    _active_config = SessionConfig(**current)
    return _active_config.model_dump()
