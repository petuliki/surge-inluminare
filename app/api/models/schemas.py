from pydantic import BaseModel, Field


class CharacterFields(BaseModel):
    name: str = Field(..., description="Name des Charakters")
    type: str = Field("Rollenspielcharakter", description="Rollenspielcharakter oder AI Agent")
    response_length: int = Field(3, description="Antwortlaenge in Saetzen", ge=1, le=20)
    traits: str = Field("", description="Charaktereigenschaften")
    appearance: str = Field("", description="Aussehen des Charakters")
    speech: str = Field("", description="Besonderheiten in der Sprache")


class CharacterUpdate(BaseModel):
    type: str | None = None
    response_length: int | None = Field(None, ge=1, le=20)
    traits: str | None = None
    appearance: str | None = None
    speech: str | None = None


class SystemPromptUpdate(BaseModel):
    content: str


class SessionConfig(BaseModel):
    character: str | None = None
    voice: str | None = None


class VoiceCloneResponse(BaseModel):
    status: str
    voice_name: str
    message: str
