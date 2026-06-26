FROM python:3.11-slim

# ── Install all dependencies ───────────────────────────────────────────────────
WORKDIR /app
COPY syntra_backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy backend (into /app/backend so app/ is a direct child) ─────────────────
COPY syntra_backend/ ./backend/

# ── Copy Streamlit frontend ────────────────────────────────────────────────────
COPY streamlit_app.py .
COPY start.sh .
RUN chmod +x start.sh

# ── Hugging Face Spaces requires port 7860 ─────────────────────────────────────
EXPOSE 7860

CMD ["./start.sh"]
