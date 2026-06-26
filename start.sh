#!/bin/bash

# Start the FastAPI backend in the background on port 8000
echo "Starting FastAPI backend..."
cd /app/backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait a moment to ensure backend starts
sleep 3

# Start the Streamlit UI in the foreground on port 7860 (Hugging Face default)
echo "Starting Streamlit UI..."
cd /app
streamlit run streamlit_app.py --server.port 7860 --server.address 0.0.0.0

# If Streamlit stops, kill the backend too
kill $BACKEND_PID
