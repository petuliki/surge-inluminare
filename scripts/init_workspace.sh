#!/usr/bin/env bash
# Initialize workspace directories and copy templates on first run.
set -e

WORKSPACE="${WORKSPACE_DIR:-/workspace}"
TEMPLATE="/workspace_template"

echo "Initializing workspace at ${WORKSPACE}..."

# Create directory structure
mkdir -p "${WORKSPACE}/models/llm"
mkdir -p "${WORKSPACE}/models/whisper"
mkdir -p "${WORKSPACE}/models/cosyvoice"
mkdir -p "${WORKSPACE}/models/hf_cache"
mkdir -p "${WORKSPACE}/characters"
mkdir -p "${WORKSPACE}/voices"
mkdir -p "${WORKSPACE}/logs"

# Copy templates only if not already present
if [ -f "${TEMPLATE}/system_prompt.txt" ] && [ ! -f "${WORKSPACE}/system_prompt.txt" ]; then
    cp "${TEMPLATE}/system_prompt.txt" "${WORKSPACE}/system_prompt.txt"
    echo "  Copied system_prompt.txt"
fi

if [ -f "${TEMPLATE}/config.env" ] && [ ! -f "${WORKSPACE}/config.env" ]; then
    cp "${TEMPLATE}/config.env" "${WORKSPACE}/config.env"
    echo "  Copied config.env"
fi

# Copy example characters if characters dir is empty
if [ -d "${TEMPLATE}/characters" ] && [ -z "$(ls -A ${WORKSPACE}/characters/ 2>/dev/null)" ]; then
    cp "${TEMPLATE}/characters/"*.txt "${WORKSPACE}/characters/" 2>/dev/null || true
    echo "  Copied example characters"
fi

# Set HuggingFace cache directory
export HF_HOME="${WORKSPACE}/models/hf_cache"

echo "Workspace initialization complete."
