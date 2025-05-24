"""
CLI for Next Watch Authentication Service.
"""

import logging
import typer
from typing import Optional

from auth_api.config.app import settings

app = typer.Typer(
    name="auth-api",
    help="Next Watch Authentication Service CLI",
)

logger = logging.getLogger(__name__)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(settings.api_port, help="Port to bind to"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
    log_level: str = typer.Option("info", help="Log level"),
):
    """Start the authentication API server."""
    import uvicorn

    typer.echo(f"Starting Next Watch Authentication Service on {host}:{port}")

    uvicorn.run(
        "auth_api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


@app.command()
def health():
    """Check the health of the authentication service."""
    import httpx

    url = f"http://localhost:{settings.api_port}/health"

    try:
        response = httpx.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        typer.echo(f"✅ Auth service is healthy: {data}")

    except httpx.RequestError as e:
        typer.echo(f"❌ Failed to connect to auth service: {e}")
        raise typer.Exit(1)
    except httpx.HTTPStatusError as e:
        typer.echo(f"❌ Auth service returned error: {e}")
        raise typer.Exit(1)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
