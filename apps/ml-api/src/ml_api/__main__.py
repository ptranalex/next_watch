"""ML API entry point for python -m ml_api."""

from ml_api.main import app

if __name__ == "__main__":
    import uvicorn
    from ml_api.config.app import settings

    uvicorn.run(
        "ml_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
