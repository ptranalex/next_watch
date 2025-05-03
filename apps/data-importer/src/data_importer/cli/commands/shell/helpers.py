"""Helper functions for the data_importer shell."""

import asyncio
import logging
import inspect
from typing import Any, Dict, Callable, List, Optional, cast

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
            if frame:
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
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        limit_per_year: Optional[int] = None,
        save_to_db: Optional[bool] = None,
        include_credits: Optional[bool] = None,
        include_videos: Optional[bool] = None,
        sort_by: Optional[str] = None,
        min_vote_count: Optional[int] = None,
    ) -> None:
        """Sync movies from TMDB and OMDB based on year range.

        Args:
            start_year: Starting year (inclusive), defaults to config value
            end_year: Ending year (inclusive), defaults to config value
            limit_per_year: Maximum number of movies per year, defaults to config value
            save_to_db: Whether to save movies to database, defaults to config value
            include_credits: Whether to include cast and crew information, defaults to config value
            include_videos: Whether to include video/trailer information, defaults to config value
            sort_by: How to sort movies ('popularity.desc' or 'vote_count.desc'), defaults to config value
            min_vote_count: Minimum vote count for movies to include, defaults to config value
        """
        from data_importer.sync import sync_movies_by_year_range
        from data_importer.sync.movie_sync import format_sync_results
        from data_importer.services.tmdb import TMDBClient
        from data_importer.services.omdb import OMDBClient
        from data_importer.config.app import Config

        ***REMOVED*** Imports for database support
        from sqlmodel import Session, create_engine
        from movie_storage.utils import setup_movie_storage  ***REMOVED*** type: ignore

        ***REMOVED*** Get config from global namespace or create a new one
        config = Config.get_instance()

        ***REMOVED*** Get clients from global namespace
        frame = inspect.currentframe()
        if not frame or not frame.f_back:
            console.print("[red]Unable to access shell context[/red]")
            return

        try:
            globals_dict = frame.f_back.f_globals
            global_tmdb_client = globals_dict.get("tmdb_client")
            global_omdb_client = globals_dict.get("omdb_client")
            global_async_run = globals_dict.get("async_run")

            ***REMOVED*** Verify all required objects are available and not None
            if not global_tmdb_client:
                console.print("[red]Error: TMDB client not found in shell context[/red]")
                return

            if not global_omdb_client:
                console.print("[red]Error: OMDB client not found in shell context[/red]")
                return

            if not global_async_run:
                console.print("[red]Error: async_run function not found in shell context[/red]")
                return

            ***REMOVED*** Verify the clients have the required attributes
            if (
                not hasattr(global_tmdb_client, "access_token")
                or not global_tmdb_client.access_token
            ):
                console.print("[red]Error: TMDB client does not have a valid access token[/red]")
                return

            if not hasattr(global_omdb_client, "api_key") or not global_omdb_client.api_key:
                console.print("[red]Error: OMDB client does not have a valid API key[/red]")
                return

            ***REMOVED*** Use config values if not specified
            actual_start_year = (
                start_year if start_year is not None else config.movie_sync_start_year
            )
            actual_end_year = end_year if end_year is not None else config.movie_sync_end_year
            actual_limit = (
                limit_per_year if limit_per_year is not None else config.movie_sync_limit_per_year
            )
            actual_save_to_db = (
                save_to_db if save_to_db is not None else config.movie_sync_save_to_db
            )
            actual_include_credits = (
                include_credits
                if include_credits is not None
                else config.movie_sync_include_credits
            )
            actual_include_videos = (
                include_videos if include_videos is not None else config.movie_sync_include_videos
            )
            actual_sort_by = sort_by if sort_by is not None else config.movie_sync_sort_by
            actual_min_vote_count = (
                min_vote_count if min_vote_count is not None else config.movie_sync_min_vote_count
            )

            ***REMOVED*** Show configuration being used
            console.print("\n[bold cyan]Movie Sync Configuration:[/bold cyan]")
            console.print(f"Year range: {actual_start_year} to {actual_end_year}")
            console.print(f"Limit per year: {actual_limit}")
            console.print(f"Sort by: {actual_sort_by}")
            console.print(f"Min vote count: {actual_min_vote_count}")
            console.print(f"Include credits: {actual_include_credits}")
            console.print(f"Include videos: {actual_include_videos}")
            console.print(f"Save to database: {actual_save_to_db}")
            console.print("")

            console.print(
                f"[cyan]Starting movie sync for years {actual_start_year}-{actual_end_year}...[/cyan]"
            )
            if actual_include_credits:
                console.print("[cyan]Including cast and crew information[/cyan]")
            if actual_include_videos:
                console.print("[cyan]Including video/trailer information[/cyan]")

            ***REMOVED*** Define the entire operation as a single async function
            async def run_sync_operation():
                ***REMOVED*** Create fresh client instances with the same API keys
                tmdb_client = TMDBClient(access_token=global_tmdb_client.access_token)
                omdb_client = OMDBClient(api_key=global_omdb_client.api_key)
                db_session = None

                try:
                    ***REMOVED*** Set up database connection if saving to db
                    if actual_save_to_db:
                        ***REMOVED*** Setup movie storage (uses .env.local if available)
                        setup_info = setup_movie_storage(create_tables=True)
                        db_url = setup_info["database_url"]
                        console.print(f"[bold]Using database:[/bold] {db_url}")

                        ***REMOVED*** Create a database session
                        engine = create_engine(db_url)
                        db_session = Session(engine)

                    ***REMOVED*** Run the sync operation with all the configured parameters
                    results = await sync_movies_by_year_range(
                        tmdb_client,
                        omdb_client,
                        start_year=actual_start_year,
                        end_year=actual_end_year,
                        limit_per_year=actual_limit,
                        db_session=db_session,
                        save_to_db=actual_save_to_db,
                        include_credits=actual_include_credits,
                        include_videos=actual_include_videos,
                        sort_by=actual_sort_by,
                        min_vote_count=actual_min_vote_count,
                    )

                    return results
                finally:
                    ***REMOVED*** Clean up resources
                    if db_session:
                        db_session.close()
                    await tmdb_client.close()
                    await omdb_client.close()

            ***REMOVED*** Run everything in a single event loop
            results = global_async_run(run_sync_operation())

            ***REMOVED*** Format and display results
            if results:
                formatted_results = format_sync_results(results)
                console.print(f"\n{formatted_results}")

                ***REMOVED*** Return the movie info to the shell for further examination
                movie_dicts = results.get("movie_dicts", [])
                movie_models = results.get("movies", [])
                genres = results.get("genres", [])
                credits_saved = results.get("credits_saved", 0)

                ***REMOVED*** Display additional info about credits if included
                if actual_include_credits and credits_saved > 0:
                    console.print(f"[green]Imported {credits_saved} cast and crew credits[/green]")

                console.print(
                    f"\n[green]Synced {len(movie_dicts)} movies with {len(genres)} genres. Access them through the 'synced_movies', 'movie_models', and 'genre_list' variables.[/green]"
                )

                ***REMOVED*** Add results to the global namespace
                globals_dict["synced_movies"] = movie_dicts
                globals_dict["movie_models"] = movie_models
                globals_dict["genre_list"] = genres

                if movie_dicts:
                    globals_dict["movie_example"] = movie_dicts[0]
                    console.print("[green]Example movie available as 'movie_example'[/green]")
            else:
                console.print("[red]Sync operation did not return any results[/red]")
        finally:
            del frame

    def sync_movie_by_id(
        tmdb_id: int,
        save_to_db: Optional[bool] = None,
        include_credits: Optional[bool] = None,
        include_videos: Optional[bool] = None,
    ) -> None:
        """Sync a single movie from TMDB and OMDB by its TMDB ID.

        Args:
            tmdb_id: The TMDB ID of the movie to sync
            save_to_db: Whether to save movie to database, defaults to config value
            include_credits: Whether to include cast and crew information, defaults to config value
            include_videos: Whether to include video/trailer information, defaults to config value
        """
        from data_importer.services.tmdb import TMDBClient
        from data_importer.services.omdb import OMDBClient
        from data_importer.services.data_adapter import MovieDataAdapter
        from data_importer.config.app import Config

        ***REMOVED*** Imports for database support
        from sqlmodel import Session, create_engine
        from movie_storage.utils import setup_movie_storage  ***REMOVED*** type: ignore

        ***REMOVED*** Get config from global namespace or create a new one
        config = Config.get_instance()

        ***REMOVED*** Get clients from global namespace
        frame = inspect.currentframe()
        if not frame or not frame.f_back:
            console.print("[red]Unable to access shell context[/red]")
            return

        try:
            globals_dict = frame.f_back.f_globals
            global_tmdb_client = globals_dict.get("tmdb_client")
            global_omdb_client = globals_dict.get("omdb_client")
            global_async_run = globals_dict.get("async_run")

            ***REMOVED*** Verify all required objects are available and not None
            if not global_tmdb_client:
                console.print("[red]Error: TMDB client not found in shell context[/red]")
                return

            if not global_omdb_client:
                console.print("[red]Error: OMDB client not found in shell context[/red]")
                return

            if not global_async_run:
                console.print("[red]Error: async_run function not found in shell context[/red]")
                return

            ***REMOVED*** Verify the clients have the required attributes
            if (
                not hasattr(global_tmdb_client, "access_token")
                or not global_tmdb_client.access_token
            ):
                console.print("[red]Error: TMDB client does not have a valid access token[/red]")
                return

            if not hasattr(global_omdb_client, "api_key") or not global_omdb_client.api_key:
                console.print("[red]Error: OMDB client does not have a valid API key[/red]")
                return

            ***REMOVED*** Use config values if not specified
            actual_save_to_db = (
                save_to_db if save_to_db is not None else config.movie_sync_save_to_db
            )
            actual_include_credits = (
                include_credits
                if include_credits is not None
                else config.movie_sync_include_credits
            )
            actual_include_videos = (
                include_videos if include_videos is not None else config.movie_sync_include_videos
            )

            ***REMOVED*** Show configuration being used
            console.print("\n[bold cyan]Movie Sync Configuration:[/bold cyan]")
            console.print(f"TMDB ID: {tmdb_id}")
            console.print(f"Include credits: {actual_include_credits}")
            console.print(f"Include videos: {actual_include_videos}")
            console.print(f"Save to database: {actual_save_to_db}")
            console.print("")

            console.print(f"[cyan]Starting sync for movie ID {tmdb_id}...[/cyan]")
            if actual_include_credits:
                console.print("[cyan]Including cast and crew information[/cyan]")
            if actual_include_videos:
                console.print("[cyan]Including video/trailer information[/cyan]")

            ***REMOVED*** Define the entire operation as a single async function
            async def run_sync_operation():
                ***REMOVED*** Create fresh client instances with the same API keys
                tmdb_client = TMDBClient(access_token=global_tmdb_client.access_token)
                omdb_client = OMDBClient(api_key=global_omdb_client.api_key)
                db_session = None

                try:
                    ***REMOVED*** Set up database connection if saving to db
                    if actual_save_to_db:
                        ***REMOVED*** Setup movie storage (uses .env.local if available)
                        setup_info = setup_movie_storage(create_tables=True)
                        db_url = setup_info["database_url"]
                        console.print(f"[bold]Using database:[/bold] {db_url}")

                        ***REMOVED*** Create a database session
                        engine = create_engine(db_url)
                        db_session = Session(engine)

                    ***REMOVED*** Create movie data adapter
                    data_adapter = MovieDataAdapter(tmdb_client, omdb_client)

                    ***REMOVED*** Import movie using combined adapter with OMDB enrichment
                    language = "en-US"  ***REMOVED*** Default language
                    if not db_session and actual_save_to_db:
                        console.print(
                            "[red]Error: Database session is required but not available[/red]"
                        )
                        return None

                    result = await data_adapter.import_movie_with_enrichment(
                        cast(Session, db_session),
                        tmdb_id,
                        language,
                        actual_include_credits,
                        actual_include_videos,
                    )

                    if not result:
                        console.print(f"[red]Failed to sync movie with ID {tmdb_id}[/red]")
                        return None

                    ***REMOVED*** Get the database movie ID and other stats
                    db_movie_id = result.get("movie_id")
                    credit_count = result.get("credit_count", 0)
                    trailer_count = result.get("trailer_count", 0)
                    operation = result.get("operation", "unknown")

                    ***REMOVED*** Get the full movie for display
                    if db_movie_id is not None and db_session:
                        from movie_storage.db.operations import movie as movie_ops

                        db_movie = movie_ops.get_movie_by_id(db_session, db_movie_id)
                        if db_movie:
                            console.print(f"\n[green]Successfully {operation} movie:[/green]")
                            console.print(f"Title: {db_movie.title}")
                            console.print(
                                f"Year: {db_movie.release_date.year if db_movie.release_date else 'Unknown'}"
                            )
                            console.print(f"TMDB Rating: {db_movie.tmdb_rating}")
                            if db_movie.imdb_rating:
                                console.print(f"IMDB Rating: {db_movie.imdb_rating}")
                            if credit_count > 0:
                                console.print(f"Credits: {credit_count}")
                            if trailer_count > 0:
                                console.print(f"Trailers: {trailer_count}")

                            ***REMOVED*** Add the movie to the global namespace for further examination
                            globals_dict["last_synced_movie"] = db_movie
                            console.print(
                                "\n[green]Movie object available as 'last_synced_movie'[/green]"
                            )

                    return result

                finally:
                    ***REMOVED*** Clean up resources
                    if db_session:
                        db_session.close()
                    await tmdb_client.close()
                    await omdb_client.close()

            ***REMOVED*** Run everything in a single event loop
            result = global_async_run(run_sync_operation())

            if not result:
                console.print("[red]Sync operation failed[/red]")

        finally:
            del frame

    ***REMOVED*** Add functions to the namespace
    namespace["list_services"] = list_services
    namespace["sync_movies"] = sync_movies
    namespace["sync_movie_by_id"] = sync_movie_by_id
