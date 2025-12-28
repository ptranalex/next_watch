"""Utility functions for the BFF API CLI interface."""

import logging
from typing import Any

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from bff_api.config.app import BFFAPIConfig

logger = logging.getLogger(__name__)


def format_config_table(
    config: BFFAPIConfig, title: str = "BFF Configuration"
) -> Table:
    """Format configuration settings as a Rich table.

    Args:
        config: Configuration object with attributes to display
        title: Title for the table

    Returns:
        Rich Table object ready to be printed
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Source", style="yellow", no_wrap=True)

    ***REMOVED*** Configuration settings to display
    config_settings = [
        ("Host", config.host, "ENV/DEFAULT"),
        ("Port", str(config.port), "ENV/DEFAULT"),
        ("Environment", config.environment, "ENV/DEFAULT"),
        ("Debug", _format_boolean(config.debug), "ENV/DEFAULT"),
        ("Log Level", config.log_level, "ENV/DEFAULT"),
        ("Log Directory", str(config.logs_dir), "ENV/DEFAULT"),
        ("Backend API URL", config.backend_api_url, "ENV/DEFAULT"),
        ("Backend API Timeout", f"{config.backend_api_timeout}s", "ENV/DEFAULT"),
        ("Auth API URL", config.auth_api_url, "ENV/DEFAULT"),
        ("Redis URL", _mask_redis_url(config.redis_url), "ENV/DEFAULT"),
        ("Cache TTL Default", f"{config.cache_ttl_default}s", "ENV/DEFAULT"),
        ("CORS Origins", ", ".join(config.cors_origins), "ENV/DEFAULT"),
        (
            "Performance Metrics",
            _format_boolean(config.enable_performance_metrics),
            "ENV/DEFAULT",
        ),
    ]

    ***REMOVED*** Add sensitive settings with masking
    jwt_display = _mask_sensitive_value(config.jwt_secret)
    config_settings.append(("JWT Secret", jwt_display, "ENV/DEFAULT"))

    api_key_display = _mask_sensitive_value(config.internal_api_key)
    config_settings.append(("Internal API Key", api_key_display, "ENV/DEFAULT"))

    for setting, value, source in config_settings:
        table.add_row(setting, value, source)

    return table


def print_config(
    config: BFFAPIConfig,
    title: str = "BFF Configuration",
    console: Console | None = None,
    show_secrets: bool = False,
) -> None:
    """Print configuration settings in a readable format.

    Args:
        config: Configuration object to display
        title: Title for the configuration table
        console: Rich console to use for output (creates new one if None)
        show_secrets: Whether to show sensitive values unmasked
    """
    if console is None:
        console = Console()

    if show_secrets:
        ***REMOVED*** Create a modified table for showing secrets
        table = Table(
            title=f"{title} (Secrets Visible)",
            show_header=True,
            header_style="bold red",
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Source", style="yellow", no_wrap=True)

        ***REMOVED*** Add settings with unmasked secrets
        settings = [
            ("JWT Secret", config.jwt_secret or "[red]Not Set[/red]", "ENV/DEFAULT"),
            (
                "Internal API Key",
                config.internal_api_key or "[red]Not Set[/red]",
                "ENV/DEFAULT",
            ),
        ]

        for setting, value, source in settings:
            table.add_row(setting, value, source)

        console.print(table)
        console.print()
    else:
        table = format_config_table(config, title=title)
        console.print(table)
        console.print()


async def check_service_health(
    url: str, service_name: str, timeout: int = 5, console: Console | None = None
) -> bool:
    """Check the health of a service endpoint.

    Args:
        url: Service URL to check
        service_name: Human-readable service name
        timeout: Request timeout in seconds
        console: Rich console for output

    Returns:
        True if service is healthy, False otherwise
    """
    if console is None:
        console = Console()

    health_url = f"{url.rstrip('/')}/health"

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(f"Checking {service_name}...", total=None)

            async with httpx.AsyncClient() as client:
                response = await client.get(health_url, timeout=timeout)
                response.raise_for_status()

                data = response.json()
                console.print(
                    f"✅ {service_name} is healthy: {data.get('status', 'OK')}"
                )

                if data.get("details"):
                    for key, value in data["details"].items():
                        console.print(f"   • {key}: {value}")

                return True

    except httpx.RequestError as e:
        console.print(f"❌ Failed to connect to {service_name}: {e}")
        logger.error(f"Health check failed for {service_name}: {e}")
        return False
    except httpx.HTTPStatusError as e:
        console.print(
            f"❌ {service_name} returned error: HTTP {e.response.status_code}"
        )
        logger.error(
            f"Health check failed for {service_name}: HTTP {e.response.status_code}"
        )
        return False
    except Exception as e:
        console.print(f"❌ Unexpected error checking {service_name}: {e}")
        logger.error(f"Unexpected error in health check for {service_name}: {e}")
        return False


def _format_boolean(value: bool) -> str:
    """Format boolean values with color coding."""
    return "[green]Enabled[/green]" if value else "[grey]Disabled[/grey]"


def _mask_sensitive_value(value: str | None) -> str:
    """Mask sensitive configuration values."""
    if not value:
        return "[red]Not Set[/red]"

    if len(value) <= 8:
        return "****"

    return f"****{value[-4:]}"


def _mask_redis_url(redis_url: str) -> str:
    """Mask password in Redis URL if present."""
    if ":" in redis_url and "@" in redis_url:
        ***REMOVED*** Format like redis://user:pass@host:port/db
        try:
            parts = redis_url.split("@")
            auth_part = parts[0]
            host_part = parts[1]

            ***REMOVED*** Get username/password part
            if ":" in auth_part:
                protocol_user, password = auth_part.rsplit(":", 1)
                return f"{protocol_user}:****@{host_part}"
        except (IndexError, ValueError):
            pass

    return redis_url


def display_service_status(
    services: dict[str, dict[str, Any]], console: Console | None = None
) -> None:
    """Display status of multiple services in a table.

    Args:
        services: Dictionary mapping service names to their status info
        console: Rich console for output
    """
    if console is None:
        console = Console()

    table = Table(
        title="Service Health Status", show_header=True, header_style="bold blue"
    )
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("URL", style="dim")
    table.add_column("Response Time", style="yellow")

    for service_name, info in services.items():
        status = info.get("status", "Unknown")
        url = info.get("url", "N/A")
        response_time = info.get("response_time", "N/A")

        ***REMOVED*** Color code status
        if status == "Healthy":
            status_display = "[green]✅ Healthy[/green]"
        elif status == "Unhealthy":
            status_display = "[red]❌ Unhealthy[/red]"
        else:
            status_display = "[yellow]⚠ Unknown[/yellow]"

        table.add_row(service_name, status_display, url, str(response_time))

    console.print(table)
    console.print()
