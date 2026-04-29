"""
Global error handler — structured JSON error responses.
"""

import traceback

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from ..database.connection import DatabaseNotReadyError

logger = structlog.get_logger("saas_kit.errors")


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app.

    Provides consistent JSON error responses for:
    - Database not ready (503)
    - HTTP exceptions (status code from exception)
    - Unhandled exceptions (500)
    """

    @app.exception_handler(DatabaseNotReadyError)
    async def database_not_ready_handler(request: Request, exc: DatabaseNotReadyError):
        return JSONResponse(
            status_code=503,
            content={
                "error": True,
                "status_code": 503,
                "detail": str(exc),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status_code": exc.status_code,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(
            "unhandled_exception",
            path=str(request.url),
            method=request.method,
            error=str(exc),
            traceback=traceback.format_exc(),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "status_code": 500,
                "detail": "An unexpected error occurred. Please try again.",
            },
        )
