import os
import re
from app.api.config import settings


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "_", name.lower()).strip("_")


def list_characters() -> list[str]:
    d = settings.characters_dir
    if not os.path.isdir(d):
        return []
    return sorted(
        f[:-4] for f in os.listdir(d)
        if f.endswith(".txt") and not f.startswith(".")
    )


def parse_character(content: str) -> dict:
    fields = {
        "name": "",
        "type": "Rollenspielcharakter",
        "response_length": 3,
        "traits": "",
        "appearance": "",
        "speech": "",
    }
    current_key = None
    current_lines: list[str] = []

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("NAME:"):
            fields["name"] = stripped[5:].strip()
        elif stripped.startswith("TYP:"):
            fields["type"] = stripped[4:].strip()
        elif stripped.startswith("ANTWORTLAENGE:"):
            try:
                fields["response_length"] = int(stripped[14:].strip())
            except ValueError:
                pass
        elif stripped.startswith("CHARAKTEREIGENSCHAFTEN:"):
            if current_key:
                fields[current_key] = "\n".join(current_lines).strip()
            current_key = "traits"
            current_lines = []
        elif stripped.startswith("AUSSEHEN:"):
            if current_key:
                fields[current_key] = "\n".join(current_lines).strip()
            current_key = "appearance"
            current_lines = []
        elif stripped.startswith("BESONDERHEITEN IN DER SPRACHE:"):
            if current_key:
                fields[current_key] = "\n".join(current_lines).strip()
            current_key = "speech"
            current_lines = []
        else:
            current_lines.append(line)

    if current_key:
        fields[current_key] = "\n".join(current_lines).strip()

    return fields


def serialize_character(data: dict) -> str:
    lines = [
        f"NAME: {data.get('name', '')}",
        f"TYP: {data.get('type', 'Rollenspielcharakter')}",
        f"ANTWORTLAENGE: {data.get('response_length', 3)}",
        "",
        "CHARAKTEREIGENSCHAFTEN:",
        data.get("traits", ""),
        "",
        "AUSSEHEN:",
        data.get("appearance", ""),
        "",
        "BESONDERHEITEN IN DER SPRACHE:",
        data.get("speech", ""),
    ]
    return "\n".join(lines) + "\n"


def read_character(name: str) -> dict:
    path = os.path.join(settings.characters_dir, f"{name}.txt")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Character '{name}' not found")
    with open(path, "r", encoding="utf-8") as f:
        return parse_character(f.read())


def read_character_raw(name: str) -> str:
    path = os.path.join(settings.characters_dir, f"{name}.txt")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Character '{name}' not found")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_character(name: str, data: dict) -> str:
    os.makedirs(settings.characters_dir, exist_ok=True)
    slug = _slugify(name)
    path = os.path.join(settings.characters_dir, f"{slug}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(serialize_character(data))
    return slug


def delete_character(name: str) -> None:
    path = os.path.join(settings.characters_dir, f"{name}.txt")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Character '{name}' not found")
    os.remove(path)


def read_system_prompt() -> str:
    path = settings.system_prompt_path
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_system_prompt(content: str) -> None:
    with open(settings.system_prompt_path, "w", encoding="utf-8") as f:
        f.write(content)


def build_system_message(character_name: str) -> str:
    base = read_system_prompt()
    try:
        char_raw = read_character_raw(character_name)
    except FileNotFoundError:
        char_raw = ""

    parts = [base]
    if char_raw:
        parts.append(char_raw)

    parsed = parse_character(char_raw) if char_raw else {}
    length = parsed.get("response_length", 3)
    if length:
        parts.append(f"Halte Antworten auf {length} Saetze.")

    return "\n\n".join(p for p in parts if p).strip()
