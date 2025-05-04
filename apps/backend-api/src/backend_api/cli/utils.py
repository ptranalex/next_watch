"""Utility functions for the CLI interface."""

import logging
from typing import Any, Dict, Optional

from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)


def format_config_table(config: Any, title: str = "Configuration") -> Table:
    """Format configuration settings as a Rich table.

    Args:
        config: Configuration object with attributes to display
        title: Title for the table

    Returns:
        Rich Table object ready to be printed
    """
    table = Table(title=title)

    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    ***REMOVED*** Add rows for each config attribute
    for attr in dir(config):
        ***REMOVED*** Skip private attributes and methods
        if attr.startswith("_") or callable(getattr(config, attr)):
            continue

        value = getattr(config, attr)

        ***REMOVED*** Handle sensitive values
        if any(
            sensitive in attr.lower()
            for sensitive in ["api_key", "token", "password", "secret"]
        ):
            if value:
                masked_value = f"{'*' * 4}{str(value)[-4:] if value else 'Not set'}"
                table.add_row(attr, masked_value)
            else:
                table.add_row(attr, "[red]Not set[/red]")
        elif isinstance(value, bool):
            formatted_value = (
                "[green]Enabled[/green]" if value else "[grey]Disabled[/grey]"
            )
            table.add_row(attr, formatted_value)
        else:
            table.add_row(attr, str(value))

    return table


def print_config(
    config: Any, title: str = "Configuration", console: Optional[Console] = None
) -> None:
    """Print configuration settings in a readable format.

    Args:
        config: Configuration object to display
        title: Title for the configuration table
        console: Rich console to use for output (creates new one if None)
    """
    if console is None:
        console = Console()

    table = format_config_table(config, title=title)
    console.print(table)


def display_redis_config(
    redis_url: str, options: Dict[str, Any], console: Optional[Console] = None
) -> None:
    """Display Redis connection and command configuration.

    Args:
        redis_url: Redis connection URL
        options: Dictionary of command options
        console: Rich console to use (creates new one if None)
    """
    if console is None:
        console = Console()

    table = Table(title="Redis Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    ***REMOVED*** Add Redis URL (mask password if present)
    if ":" in redis_url and "@" in redis_url:
        ***REMOVED*** Format like redis://user:pass@host:port/db
        parts = redis_url.split("@")
        auth_part = parts[0]
        host_part = parts[1]

        ***REMOVED*** Get username/password part
        if ":" in auth_part:
            protocol_user, password = auth_part.rsplit(":", 1)
            masked_url = f"{protocol_user}:****@{host_part}"
        else:
            masked_url = redis_url
    else:
        masked_url = redis_url

    table.add_row("Redis URL", masked_url)

    ***REMOVED*** Add other options
    for key, value in options.items():
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)
    console.print()
