from fastapi import APIRouter, HTTPException
from app.api.services.character import (
    list_characters, read_character, write_character, delete_character,
)
from app.api.models.schemas import CharacterFields, CharacterUpdate

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("")
def get_characters():
    return {"characters": list_characters()}


@router.get("/{name}")
def get_character(name: str):
    try:
        return read_character(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Charakter '{name}' nicht gefunden")


@router.post("", status_code=201)
def create_character(data: CharacterFields):
    slug = write_character(data.name, data.model_dump())
    return {"status": "ok", "slug": slug, "message": f"Charakter '{data.name}' erstellt."}


@router.put("/{name}")
def update_character(name: str, data: CharacterUpdate):
    try:
        existing = read_character(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Charakter '{name}' nicht gefunden")

    updates = data.model_dump(exclude_none=True)
    existing.update(updates)
    write_character(name, existing)
    return {"status": "ok", "message": f"Charakter '{name}' aktualisiert."}


@router.delete("/{name}")
def remove_character(name: str):
    try:
        delete_character(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Charakter '{name}' nicht gefunden")
    return {"status": "ok", "message": f"Charakter '{name}' geloescht."}
