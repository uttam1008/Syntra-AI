# Syntra AI - Backend

This is the Python backend application for **Syntra AI**, an advanced Developer Intelligence Platform. It handles AI orchestration, token tracking, semantic scoring, background telemetry, and secure database interactions.

## Core Stack
- **Framework:** FastAPI (Python 3.11+)
- **Server:** Uvicorn
- **ORM:** SQLAlchemy (via `asyncpg` for PostgreSQL integration)
- **Tokenization:** `tiktoken` (cl100k_base encoding)
- **AI Integration:** Google Gemini & Groq API

## Getting Started

1. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Or venv/bin/activate on Linux/Mac
   pip install -r requirements.txt
   ```

2. Configure environment variables in an `.env` file based on `.env.example`.

3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Access the API documentation (Swagger UI) at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Architecture & Layout
For an in-depth dive into the backend architecture, including the Router structures, Pydantic schemas, and Background Task telemetry, please read the main [BACKEND.md](../BACKEND.md) file located in the root repository. 

For deep details into the mathematical 6-factor deterministic scoring and the 8-layer extraction pipeline used in the compression engine, see [INTELLIGENCE_ENGINE.md](../INTELLIGENCE_ENGINE.md).
