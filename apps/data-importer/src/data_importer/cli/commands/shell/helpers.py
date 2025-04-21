"""Helper functions for the data_importer shell."""

import asyncio
import logging
import inspect
from typing import Any, Dict, Callable, List, Optional

from rich.console import Console
from data_importer.cli.utils import (
    format_config_table,
    print_config as print_config_util,
)

logger = logging.getLogger("data_importer.cli.shell.helpers")
console = Console()


def async_run(coro: Any, close_loop: bool = True) -> Any:
    """Run an async coroutine in the REPL.

    Args:
        coro: The coroutine to run
        close_loop: Whether to close the event loop after running (defaults to True)

    Returns:
        The result of the coroutine

    Example:
        async_run(tmdb_client.get_popular_movies(1))
    """
    try:
        ***REMOVED*** Always create a new event loop for each call
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            ***REMOVED*** Run the coroutine and return the result
            return loop.run_until_complete(coro)
        finally:
            ***REMOVED*** Close the loop if requested
            if close_loop:
                loop.close()
    except Exception as e:
        console.print(f"[red]Error running async operation:[/red] {str(e)}")
        return None


def print_plain(obj: Any) -> None:
    """Print object in plain text without colors or formatting.

    Args:
        obj: Object to print
    """
    print(str(obj))


def print_config(config=None) -> None:
    """Print configuration settings in a readable format.

    This is a shell-specific wrapper that auto-detects the config object
    if not provided and uses the generic print_config utility.

    Args:
        config: Config object (uses the one from global namespace if None)
    """
    ***REMOVED*** Get config from globals if not provided
    if config is None:
        ***REMOVED*** Get from globals (assumes running in shell with config in namespace)
        frame = inspect.currentframe()
        try:
            if frame and frame.f_back and "config" in frame.f_back.f_globals:
                config = frame.f_back.f_globals["config"]
            else:
                console.print("[red]No config object found in current context[/red]")
                return
        finally:
            del frame

    ***REMOVED*** Use the generic utility function
    print_config_util(config, title="Data Importer Configuration", console=console)


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
        console.print("3. [cyan]OMDB Client[/cyan] - Access via omdb_client")

        console.print("\n[bold green]Available commands:[/bold green]")
        console.print("- [cyan]help()[/cyan] - Show this help text")
        console.print("- [cyan]async_run(coroutine)[/cyan] - Run async coroutines")
        console.print("- [cyan]print_config()[/cyan] - Display configuration settings")

    def sync_movies(
        start_year: int,
        end_year: int,
        limit_per_year: int = 20,
        save_to_db: bool = False,
    ) -> None:
        """Sync movies from TMDB and OMDB based on year range.

        Args:
            start_year: Starting year (inclusive)
            end_year: Ending year (inclusive)
            limit_per_year: Maximum number of movies per year (default: 20)
            save_to_db: Whether to save movies to database (default: False)
        """
        from data_importer.sync import sync_movies_by_year_range
        from data_importer.sync.movie_sync import format_sync_results
        from data_importer.services import TMDBClient, OMDBClient

        ***REMOVED*** Imports for database support
        from sqlmodel import Session, create_engine
        from movie_storage.utils import setup_movie_storage  ***REMOVED*** type: ignore

        ***REMOVED*** Get clients from global namespace to get API keys
        frame = inspect.currentframe()
        try:
            if frame and frame.f_back:
                globals_dict = frame.f_back.f_globals
                global_tmdb_client = globals_dict.get("tmdb_client")
                global_omdb_client = globals_dict.get("omdb_client")
                async_run = globals_dict.get("async_run")

                if not all([global_tmdb_client, global_omdb_client, async_run]):
                    console.print(
                        "[red]Error: Required clients not found in shell context[/red]"
                    )
                    return

                console.print(
                    f"[cyan]Starting movie sync for years {start_year}-{end_year}...[/cyan]"
                )

                ***REMOVED*** Define the entire operation as a single async function
                async def run_sync_operation():
                    ***REMOVED*** Create fresh client instances with the same API keys
                    tmdb_client = TMDBClient(
                        access_token=global_tmdb_client.access_token
                    )
                    omdb_client = OMDBClient(api_key=global_omdb_client.api_key)

                    try:
                        ***REMOVED*** Set up database connection if saving to db
                        db_session = None
                        if save_to_db:
                            ***REMOVED*** Setup movie storage (uses .env.local if available)
                            setup_info = setup_movie_storage(create_tables=True)
                            db_url = setup_info["database_url"]
                            console.print(f"[bold]Using database:[/bold] {db_url}")

                            ***REMOVED*** Create a database session
                            engine = create_engine(db_url)
                            db_session = Session(engine)

                        ***REMOVED*** Run the sync operation
                        results = await sync_movies_by_year_range(
                            tmdb_client,
                            omdb_client,
                            start_year,
                            end_year,
                            limit_per_year=limit_per_year,
                            db_session=db_session,
                            save_to_db=save_to_db,
                        )

                        ***REMOVED*** Close database session if we created one
                        if save_to_db and db_session:
                            db_session.close()

                        return results
                    finally:
                        ***REMOVED*** Clean up the temporary clients
                        await tmdb_client.close()
                        await omdb_client.close()

                ***REMOVED*** Run everything in a single event loop
                results = async_run(run_sync_operation())

                ***REMOVED*** Format and display results
                if results:
                    formatted_results = format_sync_results(results)
                    console.print(f"\n{formatted_results}")

                    ***REMOVED*** Return the movie info to the shell for further examination
                    movie_dicts = results.get("movie_dicts", [])
                    movie_models = results.get("movies", [])
                    genres = results.get("genres", [])

                    console.print(
                        f"\n[green]Synced {len(movie_dicts)} movies with {len(genres)} genres. Access them through the 'synced_movies', 'movie_models', and 'genre_list' variables.[/green]"
                    )

                    ***REMOVED*** Add results to the global namespace
                    globals_dict["synced_movies"] = movie_dicts
                    globals_dict["movie_models"] = movie_models
                    globals_dict["genre_list"] = genres

                    if len(movie_dicts) > 0:
                        globals_dict["movie_example"] = movie_dicts[0]
                        console.print(
                            "[green]Example movie available as 'movie_example'[/green]"
                        )
                else:
                    console.print(
                        "[red]Sync operation did not return any results[/red]"
                    )
            else:
                console.print("[red]Unable to access shell context[/red]")
        finally:
            del frame

    ***REMOVED*** Add functions to the namespace
    namespace["list_services"] = list_services
    namespace["sync_movies"] = sync_movies
