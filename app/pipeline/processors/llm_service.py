"""
Pipecat LLM Service - uses OpenAI-compatible API provided by vLLM.
vLLM exposes an OpenAI-compatible endpoint, so we use Pipecat's built-in
OpenAI LLM service with a custom base URL.
"""
from pipecat.services.openai import OpenAILLMService


def create_llm_service(
    base_url: str = "http://127.0.0.1:8000/v1",
    model: str = "mlabonne/Qwen3-14B-abliterated",
    temperature: float = 0.75,
    max_tokens: int = 300,
) -> OpenAILLMService:
    """Create an OpenAI-compatible LLM service pointing to the local vLLM server."""
    return OpenAILLMService(
        api_key="not-needed",  # vLLM doesn't require an API key
        base_url=base_url,
        model=model,
        params=OpenAILLMService.InputParams(
            temperature=temperature,
            max_tokens=max_tokens,
        ),
    )
