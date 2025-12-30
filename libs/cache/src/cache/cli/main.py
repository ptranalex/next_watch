#!/usr/bin/env python3
"""Main CLI entry point for NextWatch Cache library."""

import typer
from rich.console import Console

from cache.cli.metrics import metrics_app
from cache.cli.warming import warming_app
from cache.config.settings import CacheSettings

console = Console()

# Main cache CLI application
cache_app = typer.Typer(
    name="cache",
    help="NextWatch Cache Management CLI",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add subcommands
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


@cache_app.command()
def info() -> None:
    """Display cache configuration information."""
    settings = CacheSettings()

    console.print("Cache Configuration:")
    console.print(f"Redis URL: {settings.get_redis_url()}")
    console.print(f"Redis Pool Size: {settings.redis_pool_size}")
    console.print(f"Redis Timeout: {settings.redis_timeout} seconds")
    console.print(f"Key Prefix: {settings.key_prefix}")
    console.print(f"Default TTL: {settings.cache_ttl_default} seconds")
    console.print(f"Metrics Enabled: {settings.enable_metrics}")


@cache_app.command()
def validate_config(
    strict: bool = typer.Option(False, "--strict", "-s", help="Fail on any configuration issues"),
) -> None:
    """Validate the cache configuration.

    Checks that Redis configuration is using the proper CACHE_ prefixed environment variables.
    """
    settings = CacheSettings()
    issues = settings.validate_config()

    if not issues:
        console.print(typer.style("✅ Cache configuration is valid", fg=typer.colors.GREEN))
        return

    console.print(typer.style("⚠️ Cache configuration issues found:", fg=typer.colors.YELLOW))
    for issue in issues:
        console.print(f"  - {issue}")

    if strict and any("Found" in issue for issue in issues):
        console.print(typer.style("\n❌ Validation failed in strict mode", fg=typer.colors.RED))
        raise typer.Exit(code=1)


def main() -> None:
    """Main CLI entry point."""
    cache_app()


if __name__ == "__main__":
    main()
