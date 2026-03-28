#!/usr/bin/env bash
# Container entrypoint for Surge Inluminare.
# Initializes workspace and starts all services via supervisord.
set -e

WORKSPACE="${WORKSPACE_DIR:-/workspace}"

echo "=========================================="
echo "  Surge Inluminare - Starting..."
echo "=========================================="

# Load runtime config if present
if [ -f "${WORKSPACE}/config.env" ]; then
    echo "Loading config from ${WORKSPACE}/config.env"
    set -a
    source "${WORKSPACE}/config.env"
    set +a
fi

# Initialize workspace
bash /scripts/init_workspace.sh

# Set environment defaults
export WORKSPACE_DIR="${WORKSPACE}"
export HF_HOME="${WORKSPACE}/models/hf_cache"
export VOICES_DIR="${WORKSPACE}/voices"
export TTS_MODEL_DIR="${WORKSPACE}/models/cosyvoice"
export COSYVOICE_PATH="${COSYVOICE_PATH:-/opt/cosyvoice}"

# Check if vLLM model is accessible (it auto-downloads from HF)
echo ""
echo "Service configuration:"
echo "  vLLM:     port 8000 (model: ${VLLM_MODEL:-mlabonne/Qwen3-14B-abliterated})"
echo "  TTS:      port 8001 (CosyVoice 2)"
echo "  STT:      port 8002 (faster-whisper ${STT_MODEL:-large-v3-turbo})"
echo "  API:      port 8888 (FastAPI + Pipecat + Frontend)"
echo ""

# Start all services via supervisord
exec supervisord -c /etc/supervisor/conf.d/surge.conf
