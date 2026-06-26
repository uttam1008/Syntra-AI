#!/bin/bash
set -e

# ── Start FastAPI backend on port 8000 ─────────────────────────────────────────
echo "==> Starting Syntra FastAPI backend..."
cd /app/backend

# python -m uvicorn guarantees /app/backend is on sys.path so 'app.main' resolves
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Give backend time to fully boot before Streamlit tries to connect
echo "==> Waiting for backend to be ready..."
sleep 6

# ── Start Streamlit UI on port 7860 (required by Hugging Face Spaces) ──────────
echo "==> Starting Syntra Streamlit UI..."
cd /app
streamlit run streamlit_app.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true

# If Streamlit exits, shut down backend too
kill $BACKEND_PID
