from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import enhance_router
from app.api.routers import intent_router
from app.api.routers import routing_router
from app.api.routers import compress_router
# auth_router intentionally removed — app is fully open, no login required

# ── App Factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Syntra AI API",
    version="1.0.0",
    description="Intelligence Distillation Engine — open, free, no DB.",
)

# Rate limiting is applied per-route via Depends(rate_limit) in app/core/rate_limiter.py

# ── CORS — allow all origins for public demo ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,          # must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(enhance_router.router)    # Prompt Enhancement
app.include_router(intent_router.router)     # Intent Intelligence
app.include_router(routing_router.router)    # Routing & Execution
app.include_router(compress_router.router)   # Compression Engine


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Syntra AI",
        "mode": "open — no auth required",
    }
