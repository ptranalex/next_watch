"""Utility functions for the CLI interface."""

import logging
import os
import re
from typing import Any, Dict, Tuple

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

logger = logging.getLogger(__name__)


def display_config(console: Console, command: str, config: Dict[str, Any]) -> None:
    """Display configuration settings.

    Args:
        console: Rich console instance
        command: Name of the command being executed
        config: Configuration settings dictionary
    """
    console.print(f"\n[bold blue]Configuration for '{command}' command:[/bold blue]")

    ***REMOVED*** Filter out sensitive information
    filtered_config = {
        k: v for k, v in config.items() if "token" not in k and "key" not in k
    }

    ***REMOVED*** Handle sensitive values
    for key in config:
        if "token" in key or "key" in key:
            if config[key] and len(str(config[key])) > 0:
                filtered_config[key] = "********"
            else:
                filtered_config[key] = "[red]Not set[/red]"

    ***REMOVED*** Display configuration
    for key, value in filtered_config.items():
        if key in ["verbose", "quiet", "cache_enabled"]:
            value = "[green]Enabled[/green]" if value else "[grey]Disabled[/grey]"
        console.print(f"  [cyan]{key}[/cyan]: {value}")

    console.print("")
