"""Command for launching an interactive chat-like interface for Home Assistant."""

import logging
from pathlib import Path

import typer
from rich.console import Console

from ha_assistant.config.app import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_HA_TOKEN,
    DEFAULT_HA_URL,
    DEFAULT_LOGS_DIR,
    DEFAULT_QUIET,
    DEFAULT_VERBOSE,
)
from ha_assistant.config.logging import configure_logging

logger = logging.getLogger("ha_assistant.cli.commands.interactive")
console = Console()


def interactive(
    config_dir: Path = typer.Option(
        DEFAULT_CONFIG_DIR,
        "--config-dir",
        "-c",
        help="Configuration directory for app settings.",
    ),
    logs_dir: Path = typer.Option(
        DEFAULT_LOGS_DIR,
        "--logs-dir",
        "-l",
        help="Directory to save log files.",
    ),
    ha_url: str = typer.Option(
        DEFAULT_HA_URL,
        "--ha-url",
        "-u",
        help="Home Assistant URL (or set HA_URL environment variable)",
    ),
    ha_token: str = typer.Option(
        DEFAULT_HA_TOKEN,
        "--ha-token",
        "-t",
        help="Home Assistant access token (or set HA_TOKEN environment variable)",
    ),
    verbose: bool = typer.Option(
        DEFAULT_VERBOSE,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    quiet: bool = typer.Option(
        DEFAULT_QUIET,
        "--quiet",
        "-q",
        help="Suppress non-essential output",
    ),
) -> None:
    """Launch an interactive chat interface with Home Assistant.

    This provides a conversational way to interact with your Home Assistant instance.
    You can ask questions about your devices, execute commands, and more.
    """
    ***REMOVED*** Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(
        log_level=log_level,
        log_dir=logs_dir,
        verbose=verbose,
        quiet=quiet,
    )

    logger.debug("Interactive mode started")

    try:
        ***REMOVED*** Create directories if they don't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        ***REMOVED*** TODO: Initialize Home Assistant client

        ***REMOVED*** TODO: Set up interactive session

        ***REMOVED*** TODO: Implement chat loop

        console.print("[bold green]Interactive mode initialized[/bold green]")
        console.print("Type 'exit' or 'quit' to end the session")

        ***REMOVED*** Placeholder for interactive loop
        console.print("[yellow]Interactive mode not yet implemented[/yellow]")

    except Exception as e:
        logger.error(f"Error in interactive session: {str(e)}")
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
