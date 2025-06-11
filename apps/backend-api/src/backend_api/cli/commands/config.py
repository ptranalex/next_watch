"""Configuration commands for the Backend API CLI."""

import logging
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from typer import Typer

from backend_api.cli.utils import format_config_table, print_config
from backend_api.config.app import settings
from backend_api.config.logging import configure_logging, get_logger

app = typer.Typer(
    name="config",
    help="Display and manage configuration settings.",
    add_completion=False,
)

console = Console()
logger = logging.getLogger("backend_api.cli.commands.config")


@app.command(name="show")
def show_config(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed configuration"),
    show_secrets: bool = typer.Option(
        False, "--show-secrets", help="Show sensitive configuration values"
    ),
) -> None:
    """Display current configuration.

    Args:
        verbose: Show detailed configuration including sensitive information masked
        show_secrets: Show sensitive information unmasked (use with caution)
    """
    configure_logging(log_level="INFO", quiet=not verbose)
    logger = get_logger(__name__)

    if not show_secrets:
        console.print("🔧 Next Watch Backend API Configuration")
        console.print(f"Environment: {getattr(settings, 'environment', 'unknown')}")
        console.print(f"Debug mode: {settings.debug}")
        console.print(f"API port: {getattr(settings, 'api_port', 8000)}")
        console.print(f"Log level: {getattr(settings, 'log_level', 'INFO')}")

        if verbose:
            ***REMOVED*** Create a table with all config values
            table = Table(title="Detailed Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")

            ***REMOVED*** Add rows for each config attribute, masking sensitive values
            for attr in dir(settings):
                ***REMOVED*** Skip private attributes and methods
                if attr.startswith("_") or callable(getattr(settings, attr)):
                    continue

                value = getattr(settings, attr)

                ***REMOVED*** Mask sensitive values
                if any(
                    sensitive in attr.lower()
                    for sensitive in ["api_key", "password", "secret", "token"]
                ):
                    if value:
                        masked_value = f"{'*' * 4}{str(value)[-4:] if len(str(value)) > 4 else ''}"
                        table.add_row(attr, masked_value)
                    else:
                        table.add_row(attr, "[grey]Not set[/grey]")
                else:
                    table.add_row(attr, str(value))

            console.print(table)
    else:
        ***REMOVED*** Show all config, including sensitive values
        console.print("[bold red]⚠️  WARNING: Displaying sensitive configuration values[/bold red]")
        print_config(settings, title="Full Configuration (Including Secrets)", console=console)

    if verbose:
        logger.info("Configuration displayed")


***REMOVED*** Default command - alias to show
@app.callback(invoke_without_command=True)
def config(ctx: typer.Context) -> None:
    """Display current configuration."""
    if ctx.invoked_subcommand is None:
        show_config()


***REMOVED*** Register config command directly with main app
from backend_api.cli import app as main_app

***REMOVED*** Register the show command directly as "config"
main_app.command("config")(show_config)
