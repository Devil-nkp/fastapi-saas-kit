"""
Database connection pool and migration runner.
Uses asyncpg for high-performance async PostgreSQL access.
"""

import asyncio
from pathlib import Path

import asyncpg
import structlog

from ..config import get_settings

logger = structlog.get_logger("saas_kit.db")

_pool: asyncpg.Pool | None = None
DB_POOL_COMMAND_TIMEOUT = 30
DB_POOL_CONNECT_TIMEOUT = 12.0
DB_POOL_INIT_ATTEMPTS = 4


class DatabaseNotReadyError(RuntimeError):
    """Raised when the database pool is not ready for application traffic."""


def _describe_error(exc: Exception) -> str:
    """Return a useful error string even for empty exception messages."""
    message = str(exc).strip()
    return message or repr(exc)


def _require_pool() -> asyncpg.Pool:
    """Return the active pool or raise a clean not-ready error."""
    if not _pool:
        raise DatabaseNotReadyError("Database is still initializing. Please retry shortly.")
    return _pool


async def init_db_pool(
    *,
    max_attempts: int = DB_POOL_INIT_ATTEMPTS,
    log_failures: bool = True,
) -> None:
    """Initialize the asyncpg connection pool.

    Called during application initialization. Retries on failure with
    exponential backoff.
    """
    global _pool
    settings = get_settings()
    last_error: Exception | None = None
    total_attempts = max(1, int(max_attempts))

    for attempt in range(1, total_attempts + 1):
        try:
            _pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=DB_POOL_COMMAND_TIMEOUT,
                timeout=DB_POOL_CONNECT_TIMEOUT,
            )
            logger.info(
                "db_pool_initialized",
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                attempt=attempt,
            )

            async with _pool.acquire() as conn:
                await run_migrations(conn)
            return
        except Exception as exc:
            last_error = exc
            if log_failures:
                logger.warning(
                    "db_pool_init_attempt_failed",
                    attempt=attempt,
                    max_attempts=total_attempts,
                    error_type=type(exc).__name__,
                    error=_describe_error(exc),
                )

            if _pool:
                await _pool.close()
                _pool = None

            if attempt >= total_attempts:
                break

            await asyncio.sleep(min(5, attempt * 2))

    raise last_error or RuntimeError("Database pool initialization failed.")


async def close_db_pool() -> None:
    """Close the connection pool on app shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("db_pool_closed")


async def get_db() -> asyncpg.Connection:
    """Acquire a connection from the pool."""
    pool = _require_pool()
    return await pool.acquire()


class DatabaseConnection:
    """Async context manager for database connections.

    Usage:
        async with DatabaseConnection() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    """

    def __init__(self) -> None:
        self.conn: asyncpg.Connection | None = None
        self.pool: asyncpg.Pool | None = None

    async def __aenter__(self) -> asyncpg.Connection:
        self.pool = _require_pool()
        self.conn = await self.pool.acquire()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn and self.pool:
            await self.pool.release(self.conn)


async def run_migrations(conn: asyncpg.Connection) -> None:
    """Run numbered SQL migration files.

    Tracks applied versions in a `schema_migrations` table.
    Migration files are discovered from the `migrations/` directory
    adjacent to this module.
    """
    logger.info("running_migrations")

    # Ensure tracking table exists
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # Get already-applied versions
    applied = {
        row["version"]
        for row in await conn.fetch("SELECT version FROM schema_migrations")
    }

    # Discover and sort migration files
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        logger.warning("migrations_directory_not_found", path=str(migrations_dir))
        return

    migration_files = sorted(
        f for f in migrations_dir.iterdir()
        if f.suffix == ".sql" and f.name[0].isdigit()
    )

    applied_count = 0
    for migration_file in migration_files:
        version = migration_file.stem
        if version in applied:
            continue

        sql = migration_file.read_text(encoding="utf-8")
        try:
            await conn.execute(sql)
            await conn.execute(
                "INSERT INTO schema_migrations (version) VALUES ($1)",
                version,
            )
            applied_count += 1
            logger.info("migration_applied", version=version)
        except Exception as exc:
            logger.error("migration_failed", version=version, error=str(exc))
            raise

    logger.info(
        "migrations_complete",
        newly_applied=applied_count,
        total_tracked=len(applied) + applied_count,
    )
