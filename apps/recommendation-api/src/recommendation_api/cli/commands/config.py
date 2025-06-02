"""Configuration commands for the Recommendation API CLI."""

import logging
import typer
from rich.console import Console

from recommendation_api.config.app import settings
from recommendation_api.cli.utils import print_config, print_error

app = typer.Typer(
    name="config",
    help="Configuration management commands",
)

console = Console()
logger = logging.getLogger(__name__)


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
) -> None:
    """Display current configuration.

    Args:
        show_secrets: Whether to show sensitive values unmasked
        verbose: Show additional configuration details
    """
    try:
        title = "Recommendation API Configuration"
        if verbose:
            title += " (Detailed)"

        print_config(settings, title, console, show_secrets=show_secrets)
    
        if verbose:
            console.print(f"[dim]Configuration loaded from: {settings.environment} environment[/dim]")
            console.print(f"[dim]Debug mode: {'Enabled' if settings.debug else 'Disabled'}[/dim]")

    except Exception as e:
        print_error(f"Failed to display configuration: {str(e)}", console)
        raise typer.Exit(code=1)


@app.command()
def validate() -> None:
    """Validate the current configuration."""
    try:
        ***REMOVED*** Check required settings
        required_settings = [
            ("Database URL", settings.database_url),
            ("Qdrant URL", settings.qdrant_url),
            ("Embedding Model", settings.embedding_model),
        ]

        console.print("[bold blue]Validating Configuration...[/bold blue]")
        console.print()

        all_valid = True
        for name, value in required_settings:
            if not value:
                console.print(f"[red]❌ {name} is not set[/red]")
                all_valid = False
            else:
                console.print(f"[green]✅ {name} is set[/green]")

        if all_valid:
            console.print("\n[green]✅ All required settings are valid[/green]")
        else:
            console.print("\n[red]❌ Some required settings are missing[/red]")
            raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Failed to validate configuration: {str(e)}", console)
        raise typer.Exit(code=1)


@app.command()
def env() -> None:
    """Show environment-specific configuration."""
    try:
        from rich.table import Table

        table = Table(
            title="Environment Configuration",
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        ***REMOVED*** Environment-specific settings
        settings_list = [
            ("Environment", settings.environment),
            ("Debug Mode", "Enabled" if settings.debug else "Disabled"),
            ("Log Level", settings.log_level),
            ("Host", settings.host),
            ("Port", str(settings.port)),
            ("Workers", str(settings.workers)),
            ("Reload", "Enabled" if settings.reload else "Disabled"),
            ("Verbose", "Enabled" if settings.verbose else "Disabled"),
        ]

        for setting, value in settings_list:
            table.add_row(setting, value)
    
        console.print(table)
        console.print()

    except Exception as e:
        print_error(f"Failed to display environment configuration: {str(e)}", console)
        raise typer.Exit(code=1) 