"""Functions for syncing movie data from various sources."""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from datetime import datetime, date
from pathlib import Path
import json
from sqlmodel import Session, select

from rich.console import Console
from rich.progress import Progress, TaskID

from data_importer.services.tmdb import TMDBClient
from data_importer.services.omdb import OMDBClient

***REMOVED*** Import database models and storage operations
from movie_storage.models import Movie
from movie_storage.db.operations import genre as genre_ops
from movie_storage.db.operations import movie as movie_ops
from movie_storage.db.operations.movie import create_movie_from_tmdb_details

logger = logging.getLogger(__name__)
console = Console()


def convert_string_to_date(date_str: Optional[str]) -> Optional[date]:
    """Convert a string date in format YYYY-MM-DD to a date object.

    Args:
        date_str: String date or None

    Returns:
        Date object or None if conversion fails
    """
    if not date_str:
        return None

    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert date: {date_str}")
        return None


async def fetch_genre_data(tmdb_client: TMDBClient) -> Dict[int, Dict[str, Any]]:
    """Fetch genres from TMDB as simple dictionaries.

    Args:
        tmdb_client: TMDBClient instance

    Returns:
        Dictionary mapping genre IDs to genre data dictionaries
    """
    genre_map = {}

    try:
        ***REMOVED*** Fetch genres from TMDB
        tmdb_genres = await tmdb_client.get_movie_genres()

        ***REMOVED*** Create simple dictionary for each genre
        for genre_data in tmdb_genres:
            genre_id = genre_data.get("id")
            name = genre_data.get("name")

            if genre_id and name:
                genre_map[genre_id] = {"id": genre_id, "name": name}

        logger.info(f"Fetched {len(genre_map)} genres from TMDB")
    except Exception as e:
        logger.error(f"Error fetching genres: {str(e)}")

    return genre_map


async def sync_movies_by_year_range(
    tmdb_client: TMDBClient,
    omdb_client: OMDBClient,
    start_year: int,
    end_year: int,
    limit_per_year: int = 20,
    show_progress: bool = True,
    db_session: Optional[Session] = None,
    save_to_db: bool = False,
    include_credits: bool = False,
) -> Dict[str, Any]:
    """Sync movies from TMDB and OMDB based on a year range.

    Args:
        tmdb_client: TMDBClient instance
        omdb_client: OMDBClient instance
        start_year: Starting year (inclusive)
        end_year: Ending year (inclusive)
        limit_per_year: Maximum number of movies to sync per year
        show_progress: Whether to show a progress bar
        db_session: Optional database session for saving to database
        save_to_db: Whether to save movies to the database
        include_credits: Whether to include cast and crew information (default: False)

    Returns:
        Dictionary with statistics about the sync operation and list of movie models
    """
    if start_year > end_year:
        start_year, end_year = end_year, start_year

    ***REMOVED*** Check if we should save to database
    if save_to_db and db_session is None:
        logger.warning("save_to_db is True but no db_session provided. Movies will not be saved.")
        save_to_db = False

    total_movies = 0
    tmdb_movies = []
    movie_models = []
    movie_dicts = []
    years = list(range(start_year, end_year + 1))

    ***REMOVED*** Fetch genres first
    genre_map = await fetch_genre_data(tmdb_client)

    ***REMOVED*** Create database genres if saving to database
    db_genres = {}
    if save_to_db and db_session:
        for genre_id, genre_data in genre_map.items():
            try:
                ***REMOVED*** Get or create the genre by TMDB ID
                db_genre = genre_ops.get_genre_by_tmdb_id(db_session, genre_id)
                if not db_genre:
                    ***REMOVED*** Create a new genre with the TMDB ID
                    db_genre = genre_ops.create_genre(
                        db_session, genre_data["name"], tmdb_id=genre_id
                    )
                db_genres[genre_id] = db_genre.id
            except Exception as e:
                logger.error(f"Error creating genre {genre_data['name']}: {str(e)}")

    ***REMOVED*** Statistics to return
    stats = {
        "tmdb_movies_found": 0,
        "omdb_matches_found": 0,
        "years_processed": 0,
        "movies_synced": 0,
        "movies_saved_to_db": 0,
        "credits_saved": 0,
        "genres_found": len(genre_map),
        "start_year": start_year,
        "end_year": end_year,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "elapsed_seconds": 0,
        "errors": [],
        "movies": [],  ***REMOVED*** Will hold simplified movie data
    }

    ***REMOVED*** Set up progress tracking
    progress = None
    task_ids = {}

    if show_progress:
        progress = Progress()
        main_task = progress.add_task(
            f"[cyan]Syncing movies from {start_year} to {end_year}...", total=len(years)
        )
        progress.start()

    try:
        ***REMOVED*** Process each year
        for year in years:
            if show_progress and progress is not None:
                year_task = progress.add_task(
                    f"[green]Processing year {year}", total=limit_per_year
                )
                task_ids[year] = year_task

            try:
                ***REMOVED*** Fetch movies from TMDB for this year
                year_movies = await tmdb_client.fetch_movies_by_year(year, limit=limit_per_year)
                tmdb_movies.extend(year_movies)
                stats["tmdb_movies_found"] += len(year_movies)

                ***REMOVED*** Process each movie from TMDB
                for i, tmdb_movie in enumerate(year_movies):
                    try:
                        movie_title = tmdb_movie.get("title", "")
                        year_str = str(year)
                        tmdb_id = tmdb_movie.get("id")

                        if include_credits and save_to_db and db_session and tmdb_id:
                            ***REMOVED*** If we want credits and we're saving to DB, we'll use a different approach
                            ***REMOVED*** that gets all details including credits in one API call
                            try:
                                ***REMOVED*** Fetch complete movie details with credits
                                movie_details = await tmdb_client.get_movie_details(
                                    movie_id=tmdb_id, append_credits=True
                                )

                                if movie_details:
                                    ***REMOVED*** Create or update movie in database with all details including credits
                                    db_movie = create_movie_from_tmdb_details(
                                        db_session, movie_details
                                    )

                                    ***REMOVED*** Count credits for statistics
                                    credit_count = len(db_movie.credits) if db_movie.credits else 0
                                    stats["credits_saved"] += credit_count

                                    ***REMOVED*** Add to in-memory movie models list
                                    movie_models.append(db_movie)

                                    ***REMOVED*** Create a dictionary representation (safer for shell use)
                                    movie_dict = {
                                        "tmdb_id": db_movie.tmdb_id,
                                        "title": db_movie.title,
                                        "original_title": db_movie.original_title,
                                        "overview": db_movie.overview,
                                        "language": db_movie.language,
                                        "release_date": db_movie.release_date,
                                        "poster_url": db_movie.poster_url,
                                        "backdrop_url": db_movie.backdrop_url,
                                        "tmdb_rating": db_movie.tmdb_rating,
                                        "popularity": db_movie.popularity,
                                        "budget": db_movie.budget,
                                        "revenue": db_movie.revenue,
                                        "genres": [
                                            {"id": g.id, "name": g.name} for g in db_movie.genres
                                        ],
                                        "credits_count": credit_count,
                                        "year": year,
                                        "imdb_id": db_movie.imdb_id,
                                    }

                                    movie_dicts.append(movie_dict)
                                    stats["movies_synced"] += 1
                                    stats["movies_saved_to_db"] += 1

                                    ***REMOVED*** Continue to next movie
                                    if show_progress and progress is not None and year in task_ids:
                                        progress.update(task_ids[year], advance=1)
                                    continue
                            except Exception as e:
                                logger.error(
                                    f"Error fetching full details for {movie_title}: {str(e)}"
                                )
                                ***REMOVED*** Fall back to normal processing without credits
                                logger.info(
                                    f"Falling back to standard processing for {movie_title}"
                                )

                        ***REMOVED*** Get genres for this movie
                        movie_genres = []
                        genre_ids = tmdb_movie.get("genre_ids", [])
                        db_genre_ids = []

                        for genre_id in genre_ids:
                            if genre_id in genre_map:
                                movie_genres.append(genre_map[genre_id])
                                ***REMOVED*** Add to db genre ids if we're saving to db
                                if save_to_db and genre_id in db_genres:
                                    db_genre_ids.append(db_genres[genre_id])

                        ***REMOVED*** Create a new movie model for in-memory use
                        movie = Movie(
                            tmdb_id=tmdb_id or 0,
                            title=movie_title,
                            original_title=tmdb_movie.get("original_title"),
                            overview=tmdb_movie.get("overview"),
                            language=tmdb_movie.get("original_language"),
                            release_date=convert_string_to_date(tmdb_movie.get("release_date")),
                            poster_url=tmdb_movie.get("poster_path"),
                            backdrop_url=tmdb_movie.get("backdrop_path"),
                            tmdb_rating=tmdb_movie.get("vote_average"),
                            popularity=tmdb_movie.get("popularity"),
                            budget=tmdb_movie.get("budget"),
                            revenue=tmdb_movie.get("revenue"),
                            runtime=tmdb_movie.get("runtime"),
                            imdb_rating=None,
                            imdb_id=None,
                            genres=[],  ***REMOVED*** Empty list for SQLModel initialization
                        )

                        ***REMOVED*** Create a dictionary representation (safer for shell use)
                        movie_dict = {
                            "tmdb_id": movie.tmdb_id,
                            "title": movie.title,
                            "original_title": movie.original_title,
                            "overview": movie.overview,
                            "language": movie.language,
                            "release_date": movie.release_date,
                            "poster_url": movie.poster_url,
                            "backdrop_url": movie.backdrop_url,
                            "tmdb_rating": movie.tmdb_rating,
                            "popularity": movie.popularity,
                            "budget": movie.budget,
                            "revenue": movie.revenue,
                            "genres": movie_genres,  ***REMOVED*** Using the genre dictionaries here
                            "year": year,
                        }

                        ***REMOVED*** Fetch additional data from OMDB if movie title exists
                        if movie_title:
                            try:
                                omdb_movie = await omdb_client.search_movie(
                                    movie_title, year=year_str
                                )

                                if omdb_movie and omdb_movie.get("Response") == "True":
                                    ***REMOVED*** Add OMDB data to the movie model and dictionary
                                    movie.imdb_id = omdb_movie.get("imdbID")
                                    movie_dict["imdb_id"] = omdb_movie.get("imdbID")

                                    imdb_rating = None
                                    if omdb_movie.get("imdbRating", "N/A") != "N/A":
                                        try:
                                            imdb_rating = float(omdb_movie.get("imdbRating", 0))
                                        except (ValueError, TypeError):
                                            pass

                                    movie.imdb_rating = imdb_rating
                                    movie_dict["imdb_rating"] = imdb_rating

                                    ***REMOVED*** Add runtime from OMDB if available
                                    runtime_str = omdb_movie.get("Runtime", "")
                                    if (
                                        runtime_str
                                        and runtime_str != "N/A"
                                        and "min" in runtime_str
                                    ):
                                        try:
                                            runtime_mins = int(runtime_str.split()[0])
                                            movie.runtime = runtime_mins
                                            movie_dict["runtime"] = runtime_mins
                                        except (ValueError, IndexError):
                                            pass

                                    stats["omdb_matches_found"] += 1
                            except Exception as e:
                                logger.warning(f"OMDB lookup failed for '{movie_title}': {str(e)}")

                        ***REMOVED*** Save to database if requested
                        if save_to_db and db_session:
                            try:
                                ***REMOVED*** Check if movie already exists
                                existing_movie = movie_ops.get_movie_by_tmdb_id(
                                    db_session, movie.tmdb_id
                                )

                                if not existing_movie:
                                    ***REMOVED*** Create new movie in database
                                    db_movie = movie_ops.create_movie(
                                        db_session,
                                        movie_dict,  ***REMOVED*** Pass the dictionary data
                                        genre_ids=db_genre_ids,  ***REMOVED*** Pass the genre IDs
                                    )
                                    stats["movies_saved_to_db"] += 1
                                    logger.info(f"Saved movie to database: {movie.title}")
                                else:
                                    logger.info(f"Movie already exists in database: {movie.title}")
                            except Exception as e:
                                error_msg = (
                                    f"Error saving movie {movie.title} to database: {str(e)}"
                                )
                                logger.error(error_msg)
                                stats["errors"].append(error_msg)

                        ***REMOVED*** Add movie to the result lists
                        movie_models.append(movie)
                        movie_dicts.append(movie_dict)

                        ***REMOVED*** Add simplified movie data to stats
                        stats["movies"].append(
                            {
                                "id": movie.tmdb_id,
                                "title": movie.title,
                                "year": year,
                                "tmdb_rating": movie.tmdb_rating,
                                "imdb_rating": movie.imdb_rating,
                                "imdb_id": movie.imdb_id,
                                "genres": (
                                    [g["name"] for g in movie_genres] if movie_genres else []
                                ),
                            }
                        )

                        stats["movies_synced"] += 1

                        ***REMOVED*** Update progress
                        if show_progress and progress is not None and year in task_ids:
                            progress.update(
                                task_ids[year],
                                completed=i + 1,
                                description=f"[green]Year {year}: {i+1}/{len(year_movies)} movies",
                            )

                    except Exception as e:
                        error_msg = (
                            f"Error processing movie {tmdb_movie.get('title', 'Unknown')}: {str(e)}"
                        )
                        logger.error(error_msg)
                        stats["errors"].append(error_msg)

                stats["years_processed"] += 1

                ***REMOVED*** Update main progress bar
                if show_progress and progress is not None:
                    progress.update(main_task, advance=1)

            except Exception as e:
                error_msg = f"Error processing year {year}: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)

                if show_progress and progress is not None and year in task_ids:
                    progress.update(
                        task_ids[year],
                        completed=limit_per_year,
                        description=f"[red]Year {year}: Error!",
                    )

        ***REMOVED*** Complete the progress
        if show_progress and progress is not None:
            progress.update(
                main_task,
                completed=len(years),
                description="[bold green]Sync complete!",
            )

    finally:
        ***REMOVED*** Record end time and calculate elapsed time
        end_time = datetime.now()
        stats["end_time"] = end_time.isoformat()
        stats["elapsed_seconds"] = (
            end_time - datetime.fromisoformat(stats["start_time"])
        ).total_seconds()

        ***REMOVED*** Stop progress bar if it's running
        if progress and progress.live.is_started:
            progress.stop()

    return {
        "stats": stats,
        "movies": movie_models,
        "movie_dicts": movie_dicts,
        "genres": list(genre_map.values()),
    }


def format_sync_results(results: Dict[str, Any]) -> str:
    """Format sync results for display.

    Args:
        results: Dictionary of sync results

    Returns:
        Formatted string for display
    """
    if not results:
        return "No results available"

    ***REMOVED*** Calculate elapsed time
    start_time = datetime.fromisoformat(results.get("start_time", datetime.now().isoformat()))
    end_time = datetime.fromisoformat(results.get("end_time", datetime.now().isoformat()))
    elapsed_seconds = (end_time - start_time).total_seconds()

    ***REMOVED*** Build the formatted string
    formatted = []
    formatted.append("[bold cyan]===== Movie Sync Results =====[/bold cyan]")
    formatted.append(
        f"[bold]Time Range:[/bold] {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    formatted.append(f"[bold]Elapsed Time:[/bold] {elapsed_seconds:.2f} seconds")
    formatted.append(
        f"[bold]Year Range:[/bold] {results.get('start_year', 'N/A')} to {results.get('end_year', 'N/A')}"
    )
    formatted.append("")
    formatted.append("[bold cyan]--- Statistics ---[/bold cyan]")
    formatted.append(f"[bold]Years Processed:[/bold] {results.get('years_processed', 0)}")
    formatted.append(f"[bold]TMDB Movies Found:[/bold] {results.get('tmdb_movies_found', 0)}")
    formatted.append(f"[bold]OMDB Matches Found:[/bold] {results.get('omdb_matches_found', 0)}")
    formatted.append(f"[bold]Movies Synced:[/bold] {results.get('movies_synced', 0)}")
    formatted.append(f"[bold]Genres Found:[/bold] {results.get('genres_found', 0)}")

    ***REMOVED*** Add credit information if available
    if "credits_saved" in results:
        formatted.append(f"[bold]Credits Saved:[/bold] {results.get('credits_saved', 0)}")

    if results.get("save_to_db", False):
        formatted.append(f"[bold]Movies Saved to DB:[/bold] {results.get('movies_saved_to_db', 0)}")

    ***REMOVED*** Add errors if any
    errors = results.get("errors", [])
    if errors:
        formatted.append("")
        formatted.append("[bold red]--- Errors ---[/bold red]")
        for error in errors[:5]:  ***REMOVED*** Show at most 5 errors
            formatted.append(f"[red]- {error}[/red]")
        if len(errors) > 5:
            formatted.append(f"[red]... and {len(errors) - 5} more errors[/red]")

    return "\n".join(formatted)
