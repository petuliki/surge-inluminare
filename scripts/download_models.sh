#!/usr/bin/env bash
# Download all required models to the persistent volume.
# Run this once after first pod creation.
set -e

WORKSPACE="${WORKSPACE_DIR:-/workspace}"
HF_HOME="${WORKSPACE}/models/hf_cache"
export HF_HOME

echo "=========================================="
echo "  Surge Inluminare - Model Download"
echo "=========================================="

# 1. vLLM model (auto-downloads from HuggingFace on first start)
echo ""
echo "[1/3] vLLM model will auto-download on first start."
echo "  Model: mlabonne/Qwen3-14B-abliterated"
echo "  This takes ~10 GB and happens automatically."

# 2. faster-whisper model
echo ""
echo "[2/3] Downloading faster-whisper model..."
python3 -c "
from faster_whisper import WhisperModel
print('Downloading large-v3-turbo...')
model = WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')
print('faster-whisper model ready.')
" 2>&1 || echo "  Warning: faster-whisper download failed. Will retry on startup."

# 3. CosyVoice 2 model
echo ""
echo "[3/3] Downloading CosyVoice 2 model..."
python3 -c "
from huggingface_hub import snapshot_download
import os
model_dir = os.path.join('${WORKSPACE}', 'models', 'cosyvoice')
snapshot_download(
    repo_id='FunAudioLLM/CosyVoice2-0.5B',
    local_dir=model_dir,
    local_dir_use_symlinks=False,
)
print(f'CosyVoice 2 model saved to {model_dir}')
" 2>&1 || echo "  Warning: CosyVoice 2 download failed. Will retry on startup."

echo ""
echo "=========================================="
echo "  Download complete!"
echo "=========================================="
echo ""
echo "Estimated VRAM usage:"
echo "  vLLM (Qwen3-14B AWQ):     ~10 GB"
echo "  faster-whisper (turbo):    ~2.5 GB"
echo "  CosyVoice 2 (0.5B):       ~5 GB"
echo "  Total:                     ~17.5-19.5 GB"
