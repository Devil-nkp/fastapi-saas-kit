"""
fastapi-saas-kit — Application Factory

Creates and configures the FastAPI application with all middleware,
routers, and lifecycle events.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager, suppress

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .auth.dependencies import configure_auth
from .auth.mock import MockAuthProvider
from .billing.adapters.mock import MockBillingProvider
from .billing.router import configure_billing
from .billing.router import router as billing_router
from .config import get_settings
from .database.connection import close_db_pool, init_db_pool
from .health.router import router as health_router
from .middleware.error_handler import register_error_handlers
from .middleware.security_headers import SecurityHeadersMiddleware
from .tenancy.router import router as tenancy_router

# ── Structured Logging ───────────────────────────────────────
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger("saas_kit")


async def _bootstrap_database(app: FastAPI) -> None:
    """Initialize the database pool in the background.

    This allows the HTTP server to start accepting health check
    requests immediately while the database connects.
    """
    retry_delay = 3

    while True:
        try:
            await init_db_pool(max_attempts=1, log_failures=False)
            app.state.db_ready = True
            logger.info("database_ready")
            return
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            app.state.db_ready = False
            logger.warning("db_init_retrying", retry_in=retry_delay, error=str(exc))
            await asyncio.sleep(retry_delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown."""
    settings = get_settings()

    logger.info("starting_app", version=settings.APP_VERSION, env=settings.ENVIRONMENT)

    # Initialize state
    app.state.started_at = time.time()
    app.state.db_ready = False

    # Configure auth provider
    if settings.AUTH_PROVIDER == "mock":
        configure_auth(MockAuthProvider())
    else:
        # For JWT or custom providers, configure_auth is called
        # with your implementation during setup
        configure_auth(MockAuthProvider())

    # Configure billing provider
    if settings.BILLING_PROVIDER == "mock":
        configure_billing(MockBillingProvider())

    # Start database initialization in background
    db_task = asyncio.create_task(_bootstrap_database(app))

    yield

    # Shutdown
    db_task.cancel()
    with suppress(asyncio.CancelledError):
        await db_task

    await close_db_pool()
    logger.info("shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance with all middleware and routers.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-ready FastAPI multi-tenant SaaS boilerplate",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────
    allowed_origins = [settings.FRONTEND_URL]
    if settings.DEBUG:
        allowed_origins.extend([
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
        ])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # ── Security Headers ─────────────────────────────────
    app.add_middleware(SecurityHeadersMiddleware)

    # ── Error Handlers ───────────────────────────────────
    register_error_handlers(app)

    # ── Routers ──────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(tenancy_router)
    app.include_router(billing_router)

    # ── Root Health ──────────────────────────────────────
    @app.api_route("/", methods=["GET", "HEAD"])
    async def root():
        """Root endpoint — lightweight health probe."""
        db_ready = bool(getattr(app.state, "db_ready", False))
        return JSONResponse({
            "status": "ok" if db_ready else "starting",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        })

    return app
