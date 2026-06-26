FROM python:3.11-slim

WORKDIR /app

# ── Install all dependencies from backend requirements ─────────────────────────
COPY syntra_backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy backend as a Python package at /app/backend ──────────────────────────
COPY syntra_backend/ ./backend/

# ── Copy Streamlit frontend ────────────────────────────────────────────────────
COPY streamlit_app.py .

# ── Hugging Face Spaces requires port 7860 ─────────────────────────────────────
EXPOSE 7860

# ── ONE process. Zero connection errors. ──────────────────────────────────────
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port", "7860", \
     "--server.address", "0.0.0.0", \
     "--server.headless", "true"]
