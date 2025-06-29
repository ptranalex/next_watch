"""Command-line interface for the ML API."""

import logging
import sys
from typing import Any, Dict, List, NoReturn, Optional, Union

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from ml_api import __version__
from ml_api.config import settings
from ml_api.services import embedding_service

***REMOVED*** Create the Typer app
app = typer.Typer(help="ML API for Next Watch platform")
serve_app = typer.Typer(help="Server management commands")
config_app = typer.Typer(help="Configuration commands")
model_app = typer.Typer(help="Model management commands")
health_app = typer.Typer(help="Health check commands")

***REMOVED*** Add sub-apps
app.add_typer(serve_app, name="serve")
app.add_typer(config_app, name="config")
app.add_typer(model_app, name="model")
app.add_typer(health_app, name="health")

***REMOVED*** Create console for rich output
console = Console()


***REMOVED*** Configure logging
def configure_logging(log_level: str = "INFO", verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    ***REMOVED*** Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    ***REMOVED*** Set more verbose logging for the ML API if requested
    if verbose:
        logging.getLogger("ml_api").setLevel(logging.DEBUG)


***REMOVED*** Server commands
@serve_app.command("start")
def start_server(
    host: str = typer.Option(settings.host, "--host", help="Host to bind the server to"),
    port: int = typer.Option(settings.port, "--port", "-p", help="Port to bind the server to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of worker processes"),
    log_level: str = typer.Option(settings.log_level, "--log-level", "-l", help="Logging level"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
) -> None:
    """Start the ML API server."""
    ***REMOVED*** Configure logging
    configure_logging(log_level, verbose)

    if not quiet:
        console.print(f"[bold green]Starting ML API server[/]")
        console.print(f"Host: [cyan]{host}[/]")
        console.print(f"Port: [cyan]{port}[/]")
        console.print(f"Workers: [cyan]{workers}[/]")
        console.print(f"Log level: [cyan]{log_level}[/]")
        console.print(f"Reload: [cyan]{reload}[/]")

    ***REMOVED*** Start the server
    uvicorn.run(
        "ml_api.app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level=log_level.lower(),
    )


***REMOVED*** Configuration commands
@config_app.command("show")
def show_config(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
) -> None:
    """Show the current configuration."""
    table = Table(title="ML API Configuration")

    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in settings.__dict__.items():
        if not key.startswith("_"):  ***REMOVED*** Skip private attributes
            table.add_row(key, str(value))

    console.print(table)


@config_app.command("validate")
def validate_config() -> bool:
    """Validate the current configuration."""
    ***REMOVED*** This is a simple validation that just checks if the config can be loaded
    try:
        ***REMOVED*** Try to access settings to validate it's properly loaded
        _ = settings.service_name
        console.print("[bold green]Configuration is valid[/]")
        return True
    except Exception as e:
        console.print(f"[bold red]Configuration error: {e}[/]")
        return False


***REMOVED*** Model commands
@model_app.command("load")
def load_model(
    model_name: Optional[str] = typer.Option(
        None, "--model-name", "-m", help="Name of the model to load"
    ),
) -> int:
    """Load the embedding model."""
    if model_name:
        console.print(f"[yellow]Warning: Custom model selection not yet implemented[/]")
        console.print(f"Using default model: [cyan]{settings.embedding_model}[/]")

    console.print(f"Loading model: [cyan]{settings.embedding_model}[/]")

    success = embedding_service.load_model()

    if success:
        console.print("[bold green]Model loaded successfully[/]")
    else:
        console.print("[bold red]Failed to load model[/]")
        return 1

    return 0


@model_app.command("info")
def model_info() -> None:
    """Get information about the embedding model."""
    model_info = embedding_service.get_model_info()

    table = Table(title="Embedding Model Information")

    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in model_info.items():
        if key == "stats":
            continue
        table.add_row(key, str(value))

    console.print(table)

    if "stats" in model_info and model_info["stats"]:
        stats_table = Table(title="Model Statistics")

        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        for key, value in model_info["stats"].items():
            stats_table.add_row(key, str(value))

        console.print(stats_table)


@model_app.command("status")
def model_status() -> int:
    """Check the status of the embedding model."""
    model_info = embedding_service.get_model_info()

    status = model_info["status"]
    health = model_info["health"]

    if status == "loaded" and health == "ok":
        console.print("[bold green]Model is loaded and healthy[/]")
    elif status == "loaded":
        console.print(f"[bold yellow]Model is loaded but health is {health}[/]")
    else:
        console.print(f"[bold red]Model is not loaded (status: {status})[/]")
        return 1

    return 0


***REMOVED*** Health check commands
@health_app.command("check")
def health_check() -> None:
    """Check the health of the ML API."""
    ***REMOVED*** Check model status
    model_info = embedding_service.get_model_info()

    table = Table(title="ML API Health Check")

    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    ***REMOVED*** API status
    table.add_row("API", "OK", f"Version {__version__}")

    ***REMOVED*** Model status
    model_status = model_info["status"]
    model_health = model_info["health"]

    if model_status == "loaded" and model_health == "ok":
        status_str = "[bold green]OK[/]"
    elif model_status == "loaded":
        status_str = "[bold yellow]WARNING[/]"
    else:
        status_str = "[bold red]ERROR[/]"

    table.add_row("Model", status_str, f"Status: {model_status}, Health: {model_health}")

    console.print(table)


***REMOVED*** Version command
@app.command("version")
def version() -> None:
    """Show the version of the ML API."""
    console.print(f"ML API version: [bold cyan]{__version__}[/]")


if __name__ == "__main__":
    app()
