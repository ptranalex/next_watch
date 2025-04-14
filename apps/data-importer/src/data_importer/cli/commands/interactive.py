"""Command for launching an interactive chat-like interface for Home Assistant."""

import logging
from pathlib import Path

import typer
from rich.console import Console

from data_importer.config.app import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_LOGS_DIR,
    DEFAULT_QUIET,
    DEFAULT_VERBOSE,
    Config,
)
from data_importer.config.logging import configure_logging
from data_importer.cli.utils import print_config

logger = logging.getLogger("data_importer.cli.commands.interactive")
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

        ***REMOVED*** Create config object
        config = Config(
            config_dir=config_dir,
            logs_dir=logs_dir,
            log_level=log_level,
            verbose=verbose,
            quiet=quiet,
        )

        ***REMOVED*** Display the config
        print_config(config, title="Interactive Mode Configuration", console=console)

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
