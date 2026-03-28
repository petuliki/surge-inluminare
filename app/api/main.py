import os
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.characters import router as characters_router
from app.api.routes.voices import router as voices_router
from app.api.routes.config_routes import router as config_router
from app.api.routes.system import router as system_router
from app.api.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Surge Inluminare API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(characters_router)
app.include_router(voices_router)
app.include_router(config_router)
app.include_router(system_router)


@app.get("/health")
async def health():
    status = {"api": "ok", "llm": "unknown", "stt": "unknown", "tts": "unknown"}

    async with httpx.AsyncClient(timeout=3) as client:
        # vLLM
        try:
            r = await client.get(f"{settings.vllm_host}/v1/models")
            status["llm"] = "ok" if r.status_code == 200 else "error"
        except Exception:
            status["llm"] = "offline"

        # STT server
        try:
            r = await client.get(f"{settings.stt_host}/health")
            status["stt"] = "ok" if r.status_code == 200 else "error"
        except Exception:
            status["stt"] = "offline"

        # TTS server
        try:
            r = await client.get(f"{settings.tts_host}/health")
            status["tts"] = "ok" if r.status_code == 200 else "error"
        except Exception:
            status["tts"] = "offline"

    return status


# WebSocket endpoint for Pipecat voice pipeline
@app.websocket("/ws/bot")
async def ws_bot(websocket):
    from app.pipeline.bot import run_pipeline
    await run_pipeline(websocket)


# Serve React frontend (built by Vite -> dist/)
_frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(_frontend_dist):
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="frontend")
