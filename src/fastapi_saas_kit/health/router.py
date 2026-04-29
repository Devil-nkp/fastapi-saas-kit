"""
Health check endpoints.
"""

import time

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..database.connection import DatabaseConnection

logger = structlog.get_logger("saas_kit.health")
router = APIRouter(tags=["Health"])

NO_STORE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
}


def _health_payload(app_state, settings, *, status: str, database: str) -> dict:
    """Build a consistent health check response payload."""
    started_at = float(getattr(app_state, "started_at", time.time()))
    uptime_seconds = max(0, int(time.time() - started_at))
    return {
        "status": status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": database,
        "uptime_seconds": uptime_seconds,
    }


@router.get("/health")
async def health(request: Request):
    """Basic health check. Returns 200 if the service is running."""
    settings = get_settings()
    db_ready = bool(getattr(request.app.state, "db_ready", False))
    return JSONResponse(
        _health_payload(
            request.app.state,
            settings,
            status="ok" if db_ready else "starting",
            database="ok" if db_ready else "starting",
        ),
        headers=NO_STORE_HEADERS,
    )


@router.get("/health/ready")
async def health_ready(request: Request):
    """Readiness check. Returns 200 only when the database is fully connected.

    Use this for container orchestration readiness probes (Kubernetes, ECS, etc.).
    """
    settings = get_settings()

    if not bool(getattr(request.app.state, "db_ready", False)):
        return JSONResponse(
            _health_payload(
                request.app.state,
                settings,
                status="starting",
                database="initializing",
            ),
            status_code=503,
            headers=NO_STORE_HEADERS,
        )

    try:
        async with DatabaseConnection() as conn:
            await conn.fetchval("SELECT 1")
    except Exception as exc:
        logger.warning("health_ready_check_failed", error=str(exc))
        return JSONResponse(
            _health_payload(
                request.app.state,
                settings,
                status="degraded",
                database="unavailable",
            ),
            status_code=503,
            headers=NO_STORE_HEADERS,
        )

    return JSONResponse(
        _health_payload(
            request.app.state,
            settings,
            status="ready",
            database="ok",
        ),
        headers=NO_STORE_HEADERS,
    )
