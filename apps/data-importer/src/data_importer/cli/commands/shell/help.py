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
        "  - omdb_client: OMDBClient instance for Open Movie Database API access",
        "  - config: Configuration instance with all app settings",
        "  - console: Rich console instance for fancy terminal output",
        "  - pprint/pp: Pretty print functions for rich output",
        "  - asyncio: Python's asyncio module for working with async code",
        "",
        "Helper functions:",
        "  - async_run(coro) - Run an async function/coroutine without 'await'",
        "  - print_plain(obj) - Print object without syntax highlighting",
        "  - print_json(obj) - Print JSON with syntax highlighting",
        "  - print_config() - Print configuration settings in a table",
        "  - list_services() - List available data services",
        "  - sync_movies(start_year, end_year, limit_per_year=20) - Sync movies for a year range",
        "  - help() - Show this help message",
        "",
        "TMDb Features:",
        "  - movies = async_run(tmdb_client.get_popular_movies(page=1)) - Get popular movies",
        "  - movies = async_run(tmdb_client.fetch_movies_by_year(year=2023, limit=10)) - Get 2023 movies",
        "",
        "IMDb Features:",
        "  - movies = imdb_client.get_top_movies(limit=10) - Get top rated movies",
        "",
        "OMDB Features:",
        "  - movie = async_run(omdb_client.get_movie_by_imdb_id('tt1285016')) - Get movie by IMDb ID",
        "  - movie = async_run(omdb_client.search_movie('The Dark Knight', '2008')) - Search by title and year",
        "  - movies = async_run(omdb_client.search_movies('Batman')) - Search for multiple movies",
        "",
        "Data Sync:",
        "  - sync_movies(2020, 2023) - Import movies from 2020-2023 using TMDB and OMDB",
        "  - sync_movies(2022, 2022, limit_per_year=5) - Import 5 movies from 2022",
        "  - synced_movies - List of all movies after running sync_movies()",
        "  - movie_example - Example of first movie from last sync",
        "  - genre_list - List of all genres fetched from TMDB",
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
        "[blue]Next Watch Data Importer Shell - Interactive Mode[/blue]",
        "",
        "Access movie data through the following clients:",
        "  - tmdb_client - The Movie Database client (async)",
        "  - imdb_client - IMDb client",
        "  - omdb_client - Open Movie Database client (async)",
        "",
        "Useful commands:",
        "  - help() - Show detailed help",
        "  - async_run(coro) - Run async functions (for TMDB client)",
        "  - print_config() - Show configuration settings",
        "  - list_services() - Show available services",
        "  - sync_movies(start_year, end_year) - Sync movies for a year range",
        "",
        "Example commands:",
        "  - movies = async_run(tmdb_client.get_popular_movies(page=1))  ***REMOVED*** Get popular movies",
        "  - movies = async_run(tmdb_client.fetch_movies_by_year(2023))  ***REMOVED*** Get 2023 movies",
        "  - movies = imdb_client.get_top_movies(limit=10)  ***REMOVED*** Get top IMDb movies",
        "  - movie = async_run(omdb_client.get_movie_by_imdb_id('tt1285016'))  ***REMOVED*** Get movie details",
        "  - sync_movies(2022, 2023)  ***REMOVED*** Import movies from 2022-2023",
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
