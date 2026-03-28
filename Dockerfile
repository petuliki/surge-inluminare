FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV WORKSPACE=/workspace
ENV HF_HOME=/workspace/models/hf_cache
ENV COSYVOICE_PATH=/opt/cosyvoice

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    supervisor \
    wget \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# vLLM
RUN pip install --no-cache-dir vllm

# Pipecat
RUN pip install --no-cache-dir "pipecat-ai[silero,websocket]"

# STT
RUN pip install --no-cache-dir faster-whisper==1.0.3

# TTS - CosyVoice 2
RUN git clone https://github.com/FunAudioLLM/CosyVoice.git ${COSYVOICE_PATH} \
    && cd ${COSYVOICE_PATH} \
    && pip install --no-cache-dir -r requirements.txt

# App Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Node.js for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Build frontend
COPY app/frontend /build/frontend
RUN cd /build/frontend && npm ci && npm run build

# Application code
COPY app /app
RUN cp -r /build/frontend/dist /app/frontend/dist && rm -rf /build

# Services
COPY services /services
RUN chmod +x /services/start_vllm.sh

# Scripts
COPY scripts /scripts
RUN chmod +x /scripts/*.sh

# Workspace template
COPY workspace_template /workspace_template

# Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/surge.conf

# JupyterLab
RUN pip install --no-cache-dir jupyterlab==4.2.5

# Expose ports: vLLM, TTS, STT, API/Pipecat, JupyterLab
EXPOSE 8000 8001 8002 8888 8889

CMD ["/scripts/start.sh"]
