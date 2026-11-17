#!/usr/bin/env bash
set -e

echo "=============================================="
echo " Starting ResearchIQ Production Services"
echo " FastAPI Port:   ${API_PORT:-8000}"
echo " Gradio UI Port:  ${GRADIO_PORT:-7860}"
echo " AWS Region:      ${AWS_REGION:-${AWS_DEFAULT_REGION:-ap-southeast-2}}"
echo "=============================================="

mkdir -p data/uploads data/chroma

# Start FastAPI backend in background
uvicorn app.api:app --host 0.0.0.0 --port "${API_PORT:-8000}" &
API_PID=$!

# Start Gradio UI in background
python -u -m app.ui &
UI_PID=$!

# Graceful termination handler
shutdown() {
    echo "Terminating ResearchIQ services..."
    kill -TERM "$API_PID" "$UI_PID" 2>/dev/null || true
    wait "$API_PID" "$UI_PID" 2>/dev/null || true
    exit 0
}

trap shutdown SIGTERM SIGINT

wait -n "$API_PID" "$UI_PID"
