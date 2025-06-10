"""Utility functions for the CLI interface."""

import inspect
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
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
            sensitive in attr.lower() for sensitive in ["api_key", "token", "password", "secret"]
        ):
            if value:
                masked_value = f"{'*' * 4}{str(value)[-4:] if value else 'Not set'}"
                table.add_row(attr, masked_value)
            else:
                table.add_row(attr, "[red]Not set[/red]")
        elif isinstance(value, bool):
            formatted_value = "[green]Enabled[/green]" if value else "[grey]Disabled[/grey]"
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


def print_plain(text: str) -> None:
    """Print text without syntax highlighting.

    Args:
        text: The text to print
    """
    print(text)


def get_api_key(
    provided_key: Optional[str],
    env_var_name: str,
    key_name: str,
    console: Console,
    required: bool = True,
) -> str:
    """Get API key from provided value or environment variable.

    Args:
        provided_key: Key provided in command options
        env_var_name: Name of the environment variable to check
        key_name: Name of the key for error messages
        console: Rich console for output
        required: Whether the key is required

    Returns:
        The API key (empty string if not required and not found)

    Raises:
        typer.Exit: If the key is required but not found
    """
    import os

    import typer

    key = provided_key or os.environ.get(env_var_name) or ""

    if not key and required:
        console.print(f"[bold red]Error:[/bold red] {key_name} is required.")
        console.print(
            f"Provide it via command option or set the {env_var_name} environment variable."
        )
        raise typer.Exit(code=1)

    return key
