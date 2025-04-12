"""Helper functions for the data_importer shell."""

import asyncio
import logging
from typing import Any, Dict, Callable

from rich.console import Console

logger = logging.getLogger("data_importer.cli.shell.helpers")
console = Console()


def async_run(coro: Any) -> Any:
    """Run an async coroutine in the REPL.

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine

    Example:
        run(tmdb_client.get_popular_movies(1))
    """
    try:
        ***REMOVED*** Create a new event loop if there isn't one running
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        ***REMOVED*** Run the coroutine and return the result
        return loop.run_until_complete(coro)
    except Exception as e:
        console.print(f"[red]Error running async operation:[/red] {str(e)}")
        return None


def print_plain(text: Any) -> None:
    """Print text without syntax highlighting.

    Args:
        text: The text to print
    """
    print(text)


def create_loading_functions(namespace: Dict[str, Any]) -> None:
    """Create helper functions for the shell.

    Args:
        namespace: The namespace dictionary to add functions to
    """

    def list_services() -> None:
        """List available data services."""
        console.print("\n[bold green]Available data services:[/bold green]")
        console.print("1. [cyan]TMDb Client[/cyan] - Access via tmdb_client")
        console.print("2. [cyan]IMDb Client[/cyan] - Access via imdb_client")

        console.print("\n[bold green]Available commands:[/bold green]")
        console.print("- [cyan]help()[/cyan] - Show this help text")
        console.print("- [cyan]run(coroutine)[/cyan] - Run async coroutines")

    ***REMOVED*** Add the function to the namespace
    namespace["list_services"] = list_services
