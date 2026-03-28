import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    workspace_dir: str = "/workspace"

    # vLLM
    vllm_host: str = "http://127.0.0.1:8000"
    vllm_model: str = "mlabonne/Qwen3-14B-abliterated"
    llm_temperature: float = 0.75
    llm_max_tokens: int = 300

    # STT
    stt_host: str = "http://127.0.0.1:8002"

    # TTS
    tts_host: str = "http://127.0.0.1:8001"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8888

    # Pipeline
    max_history_turns: int = 20
    vad_min_silence_ms: int = 300

    class Config:
        env_file = "/workspace/config.env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def characters_dir(self) -> str:
        return os.path.join(self.workspace_dir, "characters")

    @property
    def voices_dir(self) -> str:
        return os.path.join(self.workspace_dir, "voices")

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(self.workspace_dir, "system_prompt.txt")


settings = Settings()
