#!/usr/bin/env bash
# =============================================================
#  Surge Inluminare - RunPod Direct Setup (ohne Docker)
#
#  Dieses Script installiert alles direkt auf einem RunPod Pod.
#  Voraussetzung: RunPod Pod mit PyTorch 2.4.0 Template
#  GPU: L40S 48GB (empfohlen)
# =============================================================
set -e

WORKSPACE="/workspace"
APP_DIR="/app"
SERVICES_DIR="/services"

echo "=========================================="
echo "  Surge Inluminare - RunPod Setup"
echo "=========================================="
echo ""

# ----------------------------------------------------------
# 1. System-Pakete
# ----------------------------------------------------------
echo "[1/7] Installiere System-Pakete..."
apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Node.js fuer Frontend-Build
if ! command -v node &> /dev/null; then
    echo "  Installiere Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    rm -rf /var/lib/apt/lists/*
fi

# ----------------------------------------------------------
# 2. vLLM installieren
# ----------------------------------------------------------
echo ""
echo "[2/7] Installiere vLLM..."
pip install --no-cache-dir vllm 2>&1 | tail -1

# ----------------------------------------------------------
# 3. Pipecat installieren
# ----------------------------------------------------------
echo ""
echo "[3/7] Installiere Pipecat..."
pip install --no-cache-dir "pipecat-ai[silero,websocket]" 2>&1 | tail -1

# ----------------------------------------------------------
# 4. STT (faster-whisper) installieren
# ----------------------------------------------------------
echo ""
echo "[4/7] Installiere faster-whisper..."
pip install --no-cache-dir faster-whisper==1.0.3 2>&1 | tail -1

# ----------------------------------------------------------
# 5. TTS (CosyVoice 2) installieren
# ----------------------------------------------------------
echo ""
echo "[5/7] Installiere CosyVoice 2..."
COSYVOICE_PATH="/opt/cosyvoice"
if [ ! -d "${COSYVOICE_PATH}" ]; then
    git clone https://github.com/FunAudioLLM/CosyVoice.git "${COSYVOICE_PATH}"
    cd "${COSYVOICE_PATH}"
    pip install --no-cache-dir -r requirements.txt 2>&1 | tail -1
    cd /
else
    echo "  CosyVoice bereits vorhanden, ueberspringe."
fi

# ----------------------------------------------------------
# 6. App-Dependencies installieren
# ----------------------------------------------------------
echo ""
echo "[6/7] Installiere App-Dependencies..."

# Finde das Projektverzeichnis (wo dieses Script liegt)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"

pip install --no-cache-dir \
    fastapi==0.115.0 \
    "uvicorn[standard]==0.30.6" \
    python-multipart==0.0.9 \
    httpx==0.27.2 \
    pydantic-settings==2.4.0 \
    "websockets>=12.0" \
    soundfile==0.12.1 \
    "numpy>=1.26,<2.0" \
    huggingface_hub \
    jupyterlab==4.2.5 \
    2>&1 | tail -1

# ----------------------------------------------------------
# 7. App-Code und Frontend deployen
# ----------------------------------------------------------
echo ""
echo "[7/7] Deploye App-Code..."

# App-Code kopieren
rm -rf "${APP_DIR}"
cp -r "${PROJECT_DIR}/app" "${APP_DIR}"

# Services kopieren
rm -rf "${SERVICES_DIR}"
cp -r "${PROJECT_DIR}/services" "${SERVICES_DIR}"
chmod +x "${SERVICES_DIR}/start_vllm.sh"

# Scripts kopieren
cp -r "${PROJECT_DIR}/scripts" /scripts
chmod +x /scripts/*.sh

# Workspace-Template kopieren
cp -r "${PROJECT_DIR}/workspace_template" /workspace_template

# Supervisord-Config kopieren
cp "${PROJECT_DIR}/supervisord.conf" /etc/supervisor/conf.d/surge.conf

# Frontend bauen
echo "  Baue Frontend..."
cd "${APP_DIR}/frontend"
npm ci --silent
npm run build
cd /

# Workspace initialisieren
bash /scripts/init_workspace.sh

echo ""
echo "=========================================="
echo "  Setup abgeschlossen!"
echo "=========================================="
echo ""
echo "Naechster Schritt: Modelle herunterladen"
echo "  bash /scripts/download_models.sh"
echo ""
echo "Danach starten mit:"
echo "  bash /scripts/start.sh"
echo ""
echo "Oder einzelne Services testen:"
echo "  bash /services/start_vllm.sh &"
echo "  python /services/stt_server.py &"
echo "  python /services/tts_server.py &"
echo "  uvicorn app.api.main:app --host 0.0.0.0 --port 8888 --app-dir /app"
