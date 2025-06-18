"""Version information command for the Backend API CLI."""

import importlib

import platform
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

import typer
from rich.console import Console
from rich.table import Table
from typer import Typer

from config.logging import configure_logging, get_logger

from config.logging import get_logger
app = typer.Typer(
    name="version",
    help="Display version information for the Backend API and its dependencies.",
    add_completion=False,
)

console = Console()
logger = get_logger("backend_api.cli.commands.version")


@app.command()
def show_version(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed version information"
    ),
) -> None:
    """Display version information for Backend API and its dependencies.

    Args:
        verbose: Show detailed version information including system and dependencies
    """
    configure_logging(logger_name="backend_api", log_level="ERROR", quiet=not verbose)

    try:
        ***REMOVED*** Try to get version from package metadata
        backend_version = pkg_version("backend_api")
    except PackageNotFoundError:
        ***REMOVED*** Fall back to using a version constant or hardcoded version
        backend_version = "0.1.0"  ***REMOVED*** Default version if not found

    ***REMOVED*** Display version information
    console.print(f"🚀 Backend API v{backend_version}")

    if verbose:
        ***REMOVED*** System information
        table = Table(title="System Information")
        table.add_column("Component", style="cyan")
        table.add_column("Version", style="green")

        table.add_row("Python", platform.python_version())
        table.add_row("Platform", platform.platform())
        table.add_row("System", f"{platform.system()} {platform.release()}")

        console.print(table)

        ***REMOVED*** Dependencies
        deps_table = Table(title="Key Dependencies")
        deps_table.add_column("Package", style="cyan")
        deps_table.add_column("Version", style="green")

        ***REMOVED*** List important dependencies
        dependencies = [
            "fastapi",
            "uvicorn",
            "sqlmodel",
            "sqlalchemy",
            "redis",
            "httpx",
            "typer",
            "rich",
            "pydantic",
        ]

        for dep in dependencies:
            try:
                dep_version = pkg_version(dep)
                deps_table.add_row(dep, dep_version)
            except PackageNotFoundError:
                ***REMOVED*** Try to import and get version
                try:
                    module = importlib.import_module(dep)
                    if hasattr(module, "__version__"):
                        dep_version = getattr(module, "__version__")
                    elif hasattr(module, "VERSION"):
                        dep_version = getattr(module, "VERSION")
                    else:
                        dep_version = "unknown"

                    deps_table.add_row(dep, dep_version)
                except ImportError:
                    deps_table.add_row(dep, "[red]not installed[/red]")

        console.print(deps_table)


***REMOVED*** Register version command directly with main app
from backend_api.cli import app as main_app

***REMOVED*** Register the show_version command directly as "version"
main_app.command("version")(show_version)
