"""Utility functions for the Auth API CLI interface."""

import logging
import os
from typing import Any, Dict, Optional
import httpx

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from auth_api.config.app import Config

logger = logging.getLogger(__name__)


def format_config_table(config: Config, title: str = "Auth API Configuration") -> Table:
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

    ***REMOVED*** Get environment from environment variable
    environment = os.getenv("ENVIRONMENT", "development")

    ***REMOVED*** Configuration settings to display
    settings = [
        ("Environment", environment, "ENV/DEFAULT"),
        ("API Port", str(config.api_port), "ENV/DEFAULT"),
        ("Debug", _format_boolean(config.debug), "ENV/DEFAULT"),
        ("Log Level", config.log_level, "ENV/DEFAULT"),
        ("Log Directory", str(config.logs_dir), "ENV/DEFAULT"),
        ("Database URL", _mask_database_url(config.database_url), "ENV/DEFAULT"),
        (
            "CORS Origins",
            ", ".join(config.cors_origins) if config.cors_origins else "None",
            "ENV/DEFAULT",
        ),
        ("JWT Algorithm", config.jwt_algorithm, "ENV/DEFAULT"),
        (
            "Access Token Expire",
            f"{config.access_token_expire_minutes} min",
            "ENV/DEFAULT",
        ),
        (
            "Refresh Token Expire",
            f"{config.refresh_token_expire_days} days",
            "ENV/DEFAULT",
        ),
        (
            "Performance Metrics",
            _format_boolean(config.enable_performance_metrics),
            "ENV/DEFAULT",
        ),
        (
            "Password Hash Rounds",
            str(getattr(config, "password_hash_rounds", "Default")),
            "ENV/DEFAULT",
        ),
        (
            "Max Login Attempts",
            str(getattr(config, "max_login_attempts", "Default")),
            "ENV/DEFAULT",
        ),
        (
            "Login Lockout Duration",
            f"{getattr(config, 'login_lockout_duration_minutes', 'Default')} min",
            "ENV/DEFAULT",
        ),
    ]

    ***REMOVED*** Add sensitive settings with masking
    jwt_display = _mask_sensitive_value(config.jwt_secret)
    settings.append(("JWT Secret", jwt_display, "ENV/DEFAULT"))

    ***REMOVED*** Add JWK status
    jwk_status = "[green]Configured[/green]" if config.jwt_jwk else "[yellow]Not Set[/yellow]"
    settings.append(("JWK Configuration", jwk_status, "ENV/DEFAULT"))

    for setting, value, source in settings:
        table.add_row(setting, value, source)

    return table


def print_config(
    config: Config,
    title: str = "Auth API Configuration",
    console: Optional[Console] = None,
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
                "Database URL",
                config.database_url or "[red]Not Set[/red]",
                "ENV/DEFAULT",
            ),
        ]

        if config.jwt_jwk:
            settings.append(("JWK Configuration", str(config.jwt_jwk)[:100] + "...", "ENV/DEFAULT"))

        for setting, value, source in settings:
            table.add_row(setting, value, source)

        console.print(table)
        console.print()
    else:
        table = format_config_table(config, title=title)
        console.print(table)
        console.print()


async def check_service_health(
    url: str, service_name: str, timeout: int = 5, console: Optional[Console] = None
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
            task = progress.add_task(f"Checking {service_name}...", total=None)

            async with httpx.AsyncClient() as client:
                response = await client.get(health_url, timeout=timeout)
                response.raise_for_status()

                data = response.json()
                console.print(f"✅ {service_name} is healthy: {data.get('status', 'OK')}")

                if data.get("details"):
                    for key, value in data["details"].items():
                        console.print(f"   • {key}: {value}")

                return True

    except httpx.RequestError as e:
        console.print(f"❌ Failed to connect to {service_name}: {e}")
        logger.error(f"Health check failed for {service_name}: {e}")
        return False
    except httpx.HTTPStatusError as e:
        console.print(f"❌ {service_name} returned error: HTTP {e.response.status_code}")
        logger.error(f"Health check failed for {service_name}: HTTP {e.response.status_code}")
        return False
    except Exception as e:
        console.print(f"❌ Unexpected error checking {service_name}: {e}")
        logger.error(f"Unexpected error in health check for {service_name}: {e}")
        return False


def display_service_status(
    services: Dict[str, Dict[str, Any]], console: Optional[Console] = None
) -> None:
    """Display status of multiple services in a table.

    Args:
        services: Dictionary mapping service names to their status info
        console: Rich console for output
    """
    if console is None:
        console = Console()

    table = Table(title="Service Health Status", show_header=True, header_style="bold blue")
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


def display_user_table(
    users: list[dict[str, Any]], title: str = "Users", console: Optional[Console] = None
) -> None:
    """Display users in a formatted table.

    Args:
        users: List of user dictionaries
        title: Table title
        console: Rich console for output
    """
    if console is None:
        console = Console()

    if not users:
        console.print(f"[yellow]No users found.[/yellow]")
        return

    table = Table(title=title, show_header=True, header_style="bold green")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Email", style="blue")
    table.add_column("Username", style="green")
    table.add_column("Active", style="bold")
    table.add_column("Created", style="dim")
    table.add_column("Last Login", style="yellow")

    for user in users:
        ***REMOVED*** Format active status
        is_active = user.get("is_active", False)
        active_display = "[green]✓ Active[/green]" if is_active else "[red]✗ Inactive[/red]"

        ***REMOVED*** Format dates
        created_at = user.get("created_at", "Unknown")
        if created_at and created_at != "Unknown":
            try:
                from datetime import datetime

                if isinstance(created_at, str):
                    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    created_at = created_dt.strftime("%Y-%m-%d")
            except:
                pass

        last_login = user.get("last_login_at", "Never")
        if last_login and last_login != "Never":
            try:
                from datetime import datetime

                if isinstance(last_login, str):
                    login_dt = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
                    last_login = login_dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass

        table.add_row(
            str(user.get("id", "N/A")),
            user.get("email", "N/A"),
            user.get("username", "N/A"),
            active_display,
            str(created_at),
            str(last_login),
        )

    console.print(table)
    console.print()


def _format_boolean(value: bool) -> str:
    """Format boolean values with color coding."""
    return "[green]Enabled[/green]" if value else "[grey]Disabled[/grey]"


def _mask_sensitive_value(value: Optional[str]) -> str:
    """Mask sensitive configuration values."""
    if not value:
        return "[red]Not Set[/red]"

    if len(value) <= 8:
        return "****"

    return f"****{value[-4:]}"


def _mask_database_url(database_url: str) -> str:
    """Mask password in database URL if present."""
    if not database_url:
        return "[red]Not Set[/red]"

    ***REMOVED*** Handle PostgreSQL URLs like postgresql://user:pass@host:port/db
    if "://" in database_url and "@" in database_url:
        try:
            protocol_part, rest = database_url.split("://", 1)
            if "@" in rest:
                auth_part, host_part = rest.split("@", 1)
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                    return f"{protocol_part}://{username}:****@{host_part}"
        except (IndexError, ValueError):
            pass

    return database_url
