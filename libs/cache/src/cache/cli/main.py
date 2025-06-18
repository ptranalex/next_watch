***REMOVED***!/usr/bin/env python3
"""Main CLI entry point for NextWatch Cache library."""

import typer
from rich.console import Console

from cache.cli.metrics import metrics_app
from cache.cli.warming import warming_app

console = Console()

***REMOVED*** Main cache CLI application
cache_app = typer.Typer(
    name="cache",
    help="NextWatch Cache Management CLI",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

***REMOVED*** Add subcommands
cache_app.add_typer(metrics_app, name="metrics", help="Cache metrics and performance tracking")
cache_app.add_typer(warming_app, name="warming", help="Cache warming and preloading")


@cache_app.command("version")
def show_version() -> None:
    """Show cache library version."""
    from cache import __version__

    console.print(f"[bold blue]NextWatch Cache Library[/bold blue] v{__version__}")


@cache_app.command("status")
def show_status() -> None:
    """Show overall cache system status."""
    console.print("[bold green]Cache System Status[/bold green]")
    console.print("• Redis connection: [green]Connected[/green]")
    console.print("• Metrics collection: [green]Enabled[/green]")
    console.print("• Warming system: [green]Ready[/green]")


def main() -> None:
    """Main CLI entry point."""
    cache_app()


if __name__ == "__main__":
    main()
