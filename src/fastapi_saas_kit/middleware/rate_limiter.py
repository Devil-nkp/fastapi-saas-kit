"""
Sliding-window rate limiter with in-memory fallback.
"""

import time
from collections import defaultdict

import structlog
from fastapi import HTTPException, Request

from ..config import get_settings

logger = structlog.get_logger("saas_kit.ratelimit")

# ── In-memory sliding window store ───────────────────────────
_memory_store: dict[str, list[float]] = defaultdict(list)


def _memory_rate_check(key: str, limit: int, window: int) -> bool:
    """In-memory sliding window rate check.

    Args:
        key: Unique identifier for the rate limit bucket.
        limit: Maximum allowed requests in the window.
        window: Window size in seconds.

    Returns:
        True if the request is allowed, False if rate limited.
    """
    now = time.time()
    # Remove timestamps outside the window
    _memory_store[key] = [t for t in _memory_store[key] if now - t < window]
    if len(_memory_store[key]) >= limit:
        return False
    _memory_store[key].append(now)
    return True


async def rate_limit_check(key: str, limit: int, window: int = 60) -> bool:
    """Check rate limit for the given key.

    Uses in-memory sliding window by default.
    Override this function to integrate Redis or another store.

    Args:
        key: Rate limit bucket key.
        limit: Maximum requests per window.
        window: Window duration in seconds.

    Returns:
        True if allowed, False if rate limited.
    """
    return _memory_rate_check(key, limit, window)


async def rate_limit_ip(request: Request) -> None:
    """Rate limit by client IP for anonymous endpoints.

    Use as a FastAPI dependency:
        @router.get("/public", dependencies=[Depends(rate_limit_ip)])
        async def public_endpoint():
            ...
    """
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    key = f"rl:ip:{client_ip}"
    allowed = await rate_limit_check(key, settings.RATE_LIMIT_ANONYMOUS, 60)
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")


async def rate_limit_user(user_id: str) -> None:
    """Rate limit by authenticated user ID.

    Usage:
        @router.get("/api/data")
        async def get_data(user: CurrentUser = Depends(get_current_user)):
            await rate_limit_user(user.id)
            ...
    """
    settings = get_settings()
    key = f"rl:user:{user_id}"
    allowed = await rate_limit_check(key, settings.RATE_LIMIT_AUTHENTICATED, 60)
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")


def clear_rate_limit_store() -> None:
    """Clear all rate limit buckets. Useful for testing."""
    _memory_store.clear()
