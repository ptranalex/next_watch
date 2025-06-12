"""Main CLI application for BFF service."""

import sys
from typing import Optional, Dict, Any

import typer
from rich.traceback import install
from typing_extensions import Annotated

***REMOVED*** Import command modules
from bff_api.cli.commands import health, cache, serve

***REMOVED*** Import CLI logging utilities
from bff_api.cli.logging import get_cli_output

***REMOVED*** Define version constant
DEFAULT_VERSION = "0.1.0"  ***REMOVED*** Should match pyproject.toml

***REMOVED*** Install rich traceback handler
install()

***REMOVED*** Create main Typer app
app: typer.Typer = typer.Typer(
    name="bff-api",
    help="Backend for Frontend API service for Next Watch movie platform",
    add_completion=True,
)

***REMOVED*** Add command groups with explicit casting for proper type checking
app.add_typer(health.app, name="health")
app.add_typer(cache.app, name="cache")
app.add_typer(serve.app, name="serve")


@app.command(name="version")
def show_version(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed version info")
) -> None:
    """Show BFF API version information."""
    out = get_cli_output("version", verbose=verbose)

    try:
        ***REMOVED*** Try to get version from package metadata
        try:
            import importlib.metadata

            version = importlib.metadata.version("bff-api")
        except (importlib.metadata.PackageNotFoundError, AttributeError):
            version = DEFAULT_VERSION

        ***REMOVED*** Import config only when needed (no auto-logging)
        from bff_api.config.app import settings

        ***REMOVED*** Clean user output
        out.info(f"[bold blue]BFF API[/bold blue] version [green]{version}[/green]")
        out.info(f"Environment: [yellow]{settings.environment}[/yellow]")
        out.info(f"Python: [dim]{sys.version.split()[0]}[/dim]")

        ***REMOVED*** Optional verbose info
        if verbose:
            out.log_operation(
                "Version command completed", version=version, environment=settings.environment
            )

    except Exception as e:
        out.error(f"Error getting version: {e}")
        out.log_error("Version command failed", e)
        raise typer.Exit(code=1)


@app.command()
def config(
    show_secrets: bool = typer.Option(
        False,
        "--show-secrets",
        help="Show sensitive configuration values (use with caution)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed configuration information",
    ),
) -> None:
    """Display current configuration.

    Args:
        show_secrets: Whether to show sensitive values unmasked
        verbose: Show additional configuration details
    """
    out = get_cli_output("config", verbose=verbose)

    try:
        ***REMOVED*** Import config and utilities only when needed
        from bff_api.config.app import get_settings
        from bff_api.cli.utils import print_config

        ***REMOVED*** Get the actual Config instance (not proxy)
        config = get_settings()

        title = "BFF Configuration"
        if verbose:
            title += " (Detailed)"

        print_config(config, title, out.console, show_secrets=show_secrets)

        if verbose:
            out.info(f"[dim]Configuration loaded from: {config.environment} environment[/dim]")
            out.info(f"[dim]Debug mode: {'Enabled' if config.debug else 'Disabled'}[/dim]")
            out.log_operation("Configuration display completed", show_secrets=show_secrets)

    except Exception as e:
        out.error(f"Error displaying configuration: {e}")
        out.log_error("Configuration command failed", e)
        raise typer.Exit(code=1)


def main() -> int:
    """Main entry point for CLI.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        app()
        return 0
    except Exception as e:
        ***REMOVED*** Use CLI output for clean error handling
        out = get_cli_output("main")
        out.error(f"CLI Error: {e}")
        out.log_error("CLI command failed", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
