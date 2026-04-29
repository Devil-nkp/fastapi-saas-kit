"""
fastapi-saas-kit - Entry Point

Run with:
    uvicorn fastapi_saas_kit.main:app --reload
    # or
    python -m fastapi_saas_kit.main
"""

from contextlib import suppress

from .app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    from .config import get_settings

    settings = get_settings()
    port = 8000
    with suppress(ValueError, IndexError):
        port = int(settings.BACKEND_URL.split(":")[-1])

    uvicorn.run(
        "fastapi_saas_kit.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
    )
