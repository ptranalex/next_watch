"""Configuration commands for the Recommendation API CLI."""

import logging
import typer
from rich.console import Console
from rich.table import Table
from typing import Union, Tuple, List, Any

from recommendation_api.config.app import settings
from recommendation_api.cli.utils import print_config, print_error
from recommendation_api.config.logging import configure_logging

app = typer.Typer(
    name="config",
    help="Configuration management commands",
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging for config commands.

    Args:
        verbose: Enable verbose logging
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging based on verbosity
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "WARNING"
    configure_logging(log_level=log_level, verbose=verbose)


@app.command()
def show(
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
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Display current configuration.

    Args:
        show_secrets: Whether to show sensitive values unmasked
        verbose: Show additional configuration details
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    try:
        title = "Recommendation API Configuration"
        if verbose:
            title += " (Detailed)"

        print_config(settings, title, console, show_secrets=show_secrets)

        if verbose:
            console.print(
                f"[dim]Configuration loaded from: {settings.environment} environment[/dim]"
            )
            console.print(f"[dim]Debug mode: {'Enabled' if settings.debug else 'Disabled'}[/dim]")

    except Exception as e:
        print_error(f"Failed to display configuration: {str(e)}", console)
        if verbose:
            logger.exception("Configuration display error")
        raise typer.Exit(code=1)


@app.command()
def validate(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation information",
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Validate the current configuration.

    Args:
        verbose: Show detailed validation information
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    try:
        ***REMOVED*** Check required settings
        required_settings = [
            ("Database URL", settings.database_url),
            ("Qdrant URL", settings.qdrant_url),
            ("Embedding Model", settings.embedding_model),
        ]

        console.print("[bold cyan]Validating Configuration...[/bold cyan]")
        console.print()

        all_valid = True
        for name, value in required_settings:
            if not value:
                console.print(f"[red]❌ {name} is not set[/red]")
                all_valid = False
            else:
                console.print(f"[green]✅ {name} is set[/green]")

        ***REMOVED*** Add optional settings validation if verbose
        if verbose:
            console.print("\n[bold cyan]Optional Settings:[/bold cyan]")
            ***REMOVED*** Create properly typed list of tuples
            optional_settings: List[Tuple[str, Any, Any]] = [
                ("Host", settings.host, "0.0.0.0"),
                ("Port", settings.port, 8000),
                ("Log Level", settings.log_level, "INFO"),
                ("Batch Size", settings.batch_size, 100),
                ("Embedding Dimension", settings.embedding_dimension, 384),
            ]

            for name, value, default in optional_settings:
                if value == default:
                    console.print(f"[blue]ℹ {name} is using default value: {value}[/blue]")
                else:
                    console.print(f"[green]✅ {name} is customized: {value}[/green]")

        if all_valid:
            console.print("\n[green]✅ All required settings are valid[/green]")
        else:
            console.print("\n[red]❌ Some required settings are missing[/red]")
            raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Failed to validate configuration: {str(e)}", console)
        if verbose:
            logger.exception("Configuration validation error")
        raise typer.Exit(code=1)


@app.command()
def env(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show additional environment details",
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Show environment-specific configuration.

    Args:
        verbose: Show additional environment details
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    try:
        table = Table(
            title="Environment Configuration",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        if verbose:
            table.add_column("Description", style="dim")

        ***REMOVED*** Environment-specific settings
        settings_list = [
            ("Environment", settings.environment, "Current environment"),
            (
                "Debug Mode",
                "Enabled" if settings.debug else "Disabled",
                "Enable debugging features",
            ),
            ("Log Level", settings.log_level, "Logging verbosity level"),
            ("Host", settings.host, "Server host address"),
            ("Port", str(settings.port), "Server port number"),
            ("Workers", str(settings.workers), "Number of worker processes"),
            ("Reload", "Enabled" if settings.reload else "Disabled", "Auto-reload on code changes"),
            ("Verbose", "Enabled" if settings.verbose else "Disabled", "Verbose output"),
        ]

        for setting_data in settings_list:
            if verbose:
                setting, value, description = setting_data
                table.add_row(setting, value, description)
            else:
                setting, value, _ = setting_data
                table.add_row(setting, value)

        console.print(table)

        if verbose:
            console.print(
                "\n[yellow]Note: These settings can be overridden by environment variables or command line arguments[/yellow]"
            )

    except Exception as e:
        print_error(f"Failed to display environment configuration: {str(e)}", console)
        if verbose:
            logger.exception("Environment display error")
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def config_main(ctx: typer.Context) -> None:
    """Configuration management commands.

    This command group provides tools for managing and viewing the Recommendation API
    configuration settings.
    """
    if ctx.invoked_subcommand is None:
        show()
