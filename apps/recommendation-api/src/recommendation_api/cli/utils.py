"""Utility functions for the Recommendation API CLI interface."""

import logging
from typing import Any, Dict, Optional, Type, List, Union
from logging import Handler, StreamHandler, FileHandler

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
import httpx

from recommendation_api.config.app import Config

logger = logging.getLogger(__name__)


def format_config_table(config: Config, title: str = "Recommendation API Configuration") -> Table:
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
    settings = [
        ("Host", config.host, "ENV/DEFAULT"),
        ("Port", str(config.port), "ENV/DEFAULT"),
        ("Environment", config.environment, "ENV/DEFAULT"),
        ("Debug", _format_boolean(config.debug), "ENV/DEFAULT"),
        ("Log Level", config.log_level, "ENV/DEFAULT"),
        ("Database URL", _mask_database_url(config.database_url), "ENV/DEFAULT"),
        ("Qdrant URL", config.qdrant_url, "ENV/DEFAULT"),
        ("Embedding Model", config.embedding_model, "ENV/DEFAULT"),
        ("Embedding Dimension", str(config.embedding_dimension), "ENV/DEFAULT"),
        ("Batch Size", str(config.batch_size), "ENV/DEFAULT"),
        ("Max Sequence Length", str(config.max_sequence_length), "ENV/DEFAULT"),
        ("Default Recommendation Count", str(config.default_recommendation_count), "ENV/DEFAULT"),
        ("Min IMDb Rating", str(config.min_imdb_rating), "ENV/DEFAULT"),
        ("Similarity Threshold", str(config.similarity_threshold), "ENV/DEFAULT"),
        ("User Vector Weight", str(config.user_vector_weight), "ENV/DEFAULT"),
        ("Content Vector Weight", str(config.content_vector_weight), "ENV/DEFAULT"),
        ("Enable Caching", _format_boolean(config.enable_caching), "ENV/DEFAULT"),
        ("Cache TTL", f"{config.cache_ttl_seconds}s", "ENV/DEFAULT"),
        ("Precompute Similarities", _format_boolean(config.precompute_similarities), "ENV/DEFAULT"),
        ("Max Concurrent Requests", str(config.max_concurrent_requests), "ENV/DEFAULT"),
        ("Request Timeout", f"{config.request_timeout_seconds}s", "ENV/DEFAULT"),
        ("Embedding Generation Timeout", f"{config.embedding_generation_timeout}s", "ENV/DEFAULT"),
        (
            "Enable Collaborative Filtering",
            _format_boolean(config.enable_collaborative_filtering),
            "ENV/DEFAULT",
        ),
        (
            "Enable Content Filtering",
            _format_boolean(config.enable_content_filtering),
            "ENV/DEFAULT",
        ),
        (
            "Enable Trending Fallback",
            _format_boolean(config.enable_trending_fallback),
            "ENV/DEFAULT",
        ),
        ("Enable Diversity Boost", _format_boolean(config.enable_diversity_boost), "ENV/DEFAULT"),
        ("Enable Metrics", _format_boolean(True), "ALWAYS ON"),
        ("Metrics Port", str(config.metrics_port), "ENV/DEFAULT"),
        ("Health Check Interval", f"{config.health_check_interval}s", "ENV/DEFAULT"),
    ]

    ***REMOVED*** Add sensitive settings with masking
    if config.qdrant_api_key:
        settings.append(
            ("Qdrant API Key", _mask_sensitive_value(config.qdrant_api_key), "ENV/DEFAULT")
        )

    for setting, value, source in settings:
        table.add_row(setting, value, source)

    return table


def print_config(
    config: Config,
    title: str = "Recommendation API Configuration",
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
            ("Database URL", config.database_url, "ENV/DEFAULT"),
            ("Qdrant API Key", config.qdrant_api_key or "[red]Not Set[/red]", "ENV/DEFAULT"),
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


def _mask_database_url(url: str) -> str:
    """Mask password in database URL if present."""
    if "@" in url and "://" in url:
        try:
            protocol_part = url.split("://")[0]
            auth_part = url.split("://")[1].split("@")[0]
            masked_auth = auth_part.split(":")[0] + ":****"
            remaining_part = url.split("@", 1)[1]
            return f"{protocol_part}://{masked_auth}@{remaining_part}"
        except (IndexError, ValueError):
            pass

    return url


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


def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level = getattr(logging, level.upper())

    handlers: List[Handler] = [StreamHandler()]
    if log_file:
        handlers.append(FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
    )


def print_error(
    message: str,
    console: Console,
    error: Optional[Exception] = None,
) -> None:
    """Print error message with optional exception details.

    Args:
        message: Error message to display
        console: Rich console instance
        error: Optional exception that caused the error
    """
    error_text = Text(message, style="bold red")
    if error:
        error_text.append(f"\n\n{str(error)}", style="red")

    console.print(Panel(error_text, title="Error", border_style="red"))


def print_success(
    message: str,
    console: Console,
) -> None:
    """Print success message.

    Args:
        message: Success message to display
        console: Rich console instance
    """
    console.print(
        Panel(
            Text(message, style="bold green"),
            title="Success",
            border_style="green",
        )
    )
