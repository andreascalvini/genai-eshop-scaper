#!/usr/bin/env bash
set -euo pipefail

# install_and_run_ollama.sh
# Installs Ollama (if missing), starts server, pulls a model, tests it,
# and runs the scraper in local LLM mode.

# Usage:
#   bash scripts/install_and_run_ollama.sh
# or with custom model:
#   OLLAMA_MODEL_NAME=mistral bash scripts/install_and_run_ollama.sh

TARGET_URL="https://formulaiozzi.com"
MODEL_NAME="${OLLAMA_MODEL_NAME:-llama2}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
VENV_PY="./.venv/bin/python"

echo "=== Ollama local setup & scraper runner ==="

# 1) Ensure ollama is installed
if command -v ollama >/dev/null 2>&1; then
  echo "ollama already installed: $(command -v ollama)"
else
  echo "ollama not found — attempting installer from https://ollama.ai"
  if command -v curl >/dev/null 2>&1; then
    curl https://ollama.ai/install.sh | sh || {
      echo "Ollama install script failed. Check installer output and PATH." >&2
      exit 1
    }
    # Try to add common locations to PATH for this session
    export PATH="$HOME/.ollama/bin:$HOME/.local/bin:/usr/local/bin:$PATH"
    if ! command -v ollama >/dev/null 2>&1; then
      echo "ollama not found after install. Add its bin to your PATH and re-run." >&2
      exit 1
    fi
  else
    echo "curl not available — please download the installer from https://ollama.ai and run it manually." >&2
    exit 1
  fi
fi

# 2) Start ollama server if not already running
OLLAMA_PID_FILE="/tmp/ollama_$$.pid"
ALREADY_RUNNING=false
if curl -sS --connect-timeout 1 "$OLLAMA_BASE_URL/" >/dev/null 2>&1; then
  echo "Ollama server already responding at $OLLAMA_BASE_URL"
  ALREADY_RUNNING=true
else
  echo "Starting Ollama server in background (logs -> /tmp/ollama.log)"
  ollama serve &>/tmp/ollama.log &
  OLLAMA_PID=$!
  echo $OLLAMA_PID > "$OLLAMA_PID_FILE"
  # wait a bit
  sleep 3
  if ! curl -sS --connect-timeout 2 "$OLLAMA_BASE_URL/" >/dev/null 2>&1; then
    echo "Ollama server failed to start. Check /tmp/ollama.log" >&2
    tail -n 100 /tmp/ollama.log || true
    exit 1
  fi
fi

# 3) Ensure the requested model is available
if ollama list 2>/dev/null | grep -q "^${MODEL_NAME}$"; then
  echo "Model '${MODEL_NAME}' already present"
else
  echo "Pulling model '${MODEL_NAME}' (this may take some time)"
  ollama pull "${MODEL_NAME}"
fi

echo "Installed models:"
ollama list || true

# 4) Quick test the model via API
echo "Testing generation via API..."
TEST_PROMPT="Say hello from Ollama"
if command -v jq >/dev/null 2>&1; then
  curl -sS "$OLLAMA_BASE_URL/api/generate" \
    -H 'Content-Type: application/json' -d '{"model":"'"$MODEL_NAME"'","prompt":"'"$TEST_PROMPT"'","stream":false}' | jq . || true
else
  curl -sS "$OLLAMA_BASE_URL/api/generate" -H 'Content-Type: application/json' -d '{"model":"'"$MODEL_NAME"'","prompt":"'"$TEST_PROMPT"'","stream":false}' || true
fi

# 5) Finished: provide next steps to run the scraper manually
echo "Ollama setup complete. Model '${MODEL_NAME}' is available and server is running at ${OLLAMA_BASE_URL}."
echo "To run the scraper against ${TARGET_URL} using the local LLM, set these environment variables and run your project python:" \
     "\n  LLM_MODE=local OLLAMA_MODEL_NAME='${MODEL_NAME}' OLLAMA_BASE_URL='${OLLAMA_BASE_URL}' ./.venv/bin/python src/main.py ${TARGET_URL}" \
     "\nIf you don't use the project's venv, replace ./.venv/bin/python with your python3 executable."

# If we started Ollama in this script, server logs are in /tmp/ollama.log and PID (if created) is in $OLLAMA_PID_FILE
if [ -f "$OLLAMA_PID_FILE" ]; then
  echo "Ollama PID file: $OLLAMA_PID_FILE"
fi

echo "Setup finished. Stop Ollama with: ollama stop <model> (or kill PID from PID file)."