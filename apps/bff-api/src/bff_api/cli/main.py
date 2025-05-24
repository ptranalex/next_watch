"""Main CLI application for BFF service."""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from bff_api.config.app import settings, Config
from bff_api.main import create_app

console = Console()
logger = logging.getLogger(__name__)

***REMOVED*** Create main Typer app
app = typer.Typer(
    name="bff-api",
    help="Backend for Frontend API service for Next Watch movie platform",
    add_completion=False,
)


@app.command()
def serve(
    host: str = typer.Option(
        None,
        "--host",
        "-h",
        help="Host to bind server to",
        envvar="HOST",
    ),
    port: int = typer.Option(
        None,
        "--port",
        "-p",
        help="Port to bind server to",
        envvar="PORT",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload for development",
    ),
    log_level: str = typer.Option(
        None,
        "--log-level",
        help="Set log level",
        envvar="LOG_LEVEL",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
) -> None:
    """Start the BFF API server."""

    ***REMOVED*** Create configuration
    config_kwargs: Dict[str, Any] = {}
    if host:
        config_kwargs["host"] = host
    if port:
        config_kwargs["port"] = port
    if log_level:
        config_kwargs["log_level"] = log_level

    ***REMOVED*** Update global settings if any CLI overrides are provided
    if config_kwargs:
        ***REMOVED*** For CLI usage, we'd need to create a new Config instance
        config = Config(**config_kwargs)
    else:
        config = settings

    ***REMOVED*** Display configuration
    _display_config(config)

    ***REMOVED*** Create FastAPI app (no longer accepts config parameter)
    fastapi_app = create_app()

    ***REMOVED*** Start server
    logger.info(f"Starting BFF API server on {config.host}:{config.port}")

    uvicorn.run(
        fastapi_app,
        host=config.host,
        port=config.port,
        reload=reload,
        log_level=config.log_level.lower(),
        access_log=not config.is_production,
    )


@app.command()
def config(
    show_secrets: bool = typer.Option(
        False,
        "--show-secrets",
        help="Show sensitive configuration values",
    ),
) -> None:
    """Display current configuration."""

    _display_config(settings, show_secrets=show_secrets)


@app.command()
def health_check(
    backend_api_url: str = typer.Option(
        None,
        "--backend-api-url",
        help="Backend API URL to check",
        envvar="BACKEND_API_URL",
    ),
) -> None:
    """Check health of backend services."""

    config = settings
    if backend_api_url:
        config.backend_api_url = backend_api_url

    console.print(f"[blue]Checking backend API at: {config.backend_api_url}[/blue]")

    ***REMOVED*** TODO: Implement actual health checks
    ***REMOVED*** For now, just show configuration
    console.print("[green]✓[/green] Configuration loaded successfully")
    console.print(f"[yellow]⚠[/yellow] Backend API health check not implemented yet")


def _display_config(config: Config, show_secrets: bool = False) -> None:
    """Display configuration in a formatted table.

    Args:
        config: Configuration instance
        show_secrets: Whether to show sensitive values
    """
    table = Table(
        title="BFF Configuration", show_header=True, header_style="bold magenta"
    )
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source", style="yellow")

    ***REMOVED*** Configuration settings to display
    settings = [
        ("Host", config.host, "ENV/DEFAULT"),
        ("Port", str(config.port), "ENV/DEFAULT"),
        ("Environment", config.environment, "ENV/DEFAULT"),
        ("Debug", str(config.debug), "ENV/DEFAULT"),
        ("Log Level", config.log_level, "ENV/DEFAULT"),
        ("Backend API URL", config.backend_api_url, "ENV/DEFAULT"),
        ("Backend API Timeout", f"{config.backend_api_timeout}s", "ENV/DEFAULT"),
        ("Redis URL", config.redis_url, "ENV/DEFAULT"),
        ("Cache TTL", f"{config.cache_ttl}s", "ENV/DEFAULT"),
    ]

    ***REMOVED*** Add JWT secret (masked by default)
    if show_secrets and config.jwt_secret:
        settings.append(("JWT Secret", config.jwt_secret, "ENV/DEFAULT"))
    else:
        secret_display = "***" if config.jwt_secret else "Not Set"
        settings.append(("JWT Secret", secret_display, "ENV/DEFAULT"))

    for setting, value, source in settings:
        table.add_row(setting, value, source)

    console.print(table)
    console.print()


def main() -> None:
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
