"""
Simple in-memory IP rate limiter — no external dependencies needed.
Limits: 30 requests per minute per IP across AI endpoints.
"""
import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException

# Store: ip -> deque of timestamps
_request_log: dict[str, deque] = defaultdict(deque)

WINDOW_SECONDS = 60
MAX_REQUESTS = 30   # per window per IP


def rate_limit(request: Request):
    """FastAPI dependency — call via Depends(rate_limit)."""
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - WINDOW_SECONDS

    log = _request_log[ip]

    # Drop timestamps outside the rolling window
    while log and log[0] < window_start:
        log.popleft()

    if len(log) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {MAX_REQUESTS} requests per minute. Please wait a moment.",
        )

    log.append(now)
