"""Help text and documentation for the data_importer shell."""

from typing import Callable, List, Dict, Any
from rich.console import Console

console = Console()


def get_help_text() -> List[str]:
    """Get the detailed help text for the shell.

    Returns:
        List of help text lines
    """
    help_text_lines = [
        "\n=== Next Watch Data Importer Shell Help ===",
        "",
        "Available modules:",
        "  - tmdb_client: TMDBClient instance for The Movie Database API access",
        "  - imdb_client: IMDBClient instance for IMDb API access",
        "  - console: Rich console instance for fancy terminal output",
        "  - pprint: Pretty print function for rich output",
        "  - asyncio: Python's asyncio module for working with async code",
        "",
        "Helper functions:",
        "  - run(coro) - Run an async function/coroutine without 'await'",
        "  - print_plain(text) - Print text without syntax highlighting",
        "  - list_services() - List available data services",
        "  - help() - Show this help message",
        "",
        "TMDb Features:",
        "  - movies = tmdb_client.get_popular_movies(page=1) - Get popular movies",
        "",
        "IMDb Features:",
        "  - movies = imdb_client.get_top_movies(limit=10) - Get top rated movies",
        "",
        "Python tools:",
        "  - dir(object) - List all attributes of an object",
        "  - help(object) - Get help on a Python object",
    ]

    return help_text_lines


def get_banner_text() -> str:
    """Get the banner text for the shell.

    Returns:
        Banner text as a string
    """
    banner_lines = [
        "=== Next Watch Data Importer Interactive Shell ===",
        "",
        "Pre-loaded modules:",
        "  - tmdb_client: TMDBClient instance for The Movie Database API",
        "  - imdb_client: IMDBClient instance for IMDb API",
        "",
        "Helper functions:",
        "  - run(coro) - Run async functions (coroutines)",
        "  - list_services() - List available data services",
        "  - help() - Show detailed help",
        "",
        "Example commands:",
        "  - movies = tmdb_client.get_popular_movies(page=1)  ***REMOVED*** Get popular movies",
        "  - movies = imdb_client.get_top_movies(limit=10)  ***REMOVED*** Get top IMDb movies",
    ]

    return "\n".join(banner_lines)


def create_shell_help_function(namespace: Dict[str, Any]) -> Callable[[], None]:
    """Create a help function for the shell.

    Args:
        namespace: The shell namespace containing objects and functions

    Returns:
        A callable help function
    """

    def shell_help() -> None:
        """Display help information for the Home Assistant Assistant shell."""
        for line in get_help_text():
            console.print(line)

    return shell_help
