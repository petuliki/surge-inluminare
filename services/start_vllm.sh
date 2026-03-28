#!/usr/bin/env bash
# Start vLLM server with AWQ-Marlin quantization
set -e

MODEL="${VLLM_MODEL:-mlabonne/Qwen3-14B-abliterated}"
QUANT="${VLLM_QUANTIZATION:-awq_marlin}"
GPU_MEM="${VLLM_GPU_MEMORY_UTILIZATION:-0.50}"
MAX_LEN="${VLLM_MAX_MODEL_LEN:-4096}"
HOST="${VLLM_HOST:-127.0.0.1}"
PORT="${VLLM_PORT:-8000}"

echo "Starting vLLM server..."
echo "  Model: ${MODEL}"
echo "  Quantization: ${QUANT}"
echo "  GPU Memory: ${GPU_MEM}"
echo "  Max Context: ${MAX_LEN}"
echo "  Port: ${PORT}"

exec python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --quantization "${QUANT}" \
    --gpu-memory-utilization "${GPU_MEM}" \
    --max-model-len "${MAX_LEN}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --dtype float16
