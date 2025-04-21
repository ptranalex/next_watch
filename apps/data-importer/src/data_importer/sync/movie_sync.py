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

from data_importer.services import TMDBClient, OMDBClient

***REMOVED*** Import database models and storage operations
from movie_storage.db.models import Movie
from movie_storage.db.operations import genre as genre_ops
from movie_storage.db.operations import movie as movie_ops


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
                            tmdb_id=tmdb_movie.get("id", 0),
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
    """Format sync results into a human-readable string.

    Args:
        results: Dictionary with statistics and movie models

    Returns:
        Formatted string with results
    """
    stats = results.get("stats", {})
    movie_dicts = results.get("movie_dicts", [])
    genres = results.get("genres", [])

    if not stats:
        return "No sync results available."

    start_time = datetime.fromisoformat(stats["start_time"])
    formatted_start = start_time.strftime("%Y-%m-%d %H:%M:%S")

    if stats["end_time"]:
        end_time = datetime.fromisoformat(stats["end_time"])
        formatted_end = end_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        formatted_end = "N/A"

    formatted_results = [
        f"Movie Sync Results ({stats['start_year']} - {stats['end_year']})",
        f"Started: {formatted_start}",
        f"Finished: {formatted_end}",
        f"Duration: {stats['elapsed_seconds']:.2f} seconds",
        f"Years processed: {stats['years_processed']} of {stats['end_year'] - stats['start_year'] + 1}",
        f"Genres found: {stats.get('genres_found', 0)}",
        f"TMDB movies found: {stats['tmdb_movies_found']}",
        f"OMDB matches found: {stats['omdb_matches_found']}",
        f"Total movies synced: {stats['movies_synced']}",
    ]

    ***REMOVED*** Add database storage information if available
    if "movies_saved_to_db" in stats:
        formatted_results.append(f"Movies saved to database: {stats['movies_saved_to_db']}")

    ***REMOVED*** Add genre list
    if genres:
        formatted_results.append("\nGenres:")
        genre_names = [f"{g['id']}: {g['name']}" for g in genres[:10]]
        formatted_results.append("  " + ", ".join(genre_names))
        if len(genres) > 10:
            formatted_results.append(f"  ... and {len(genres) - 10} more genres")

    ***REMOVED*** Add movie list summary
    if movie_dicts:
        formatted_results.append("\nSynced Movies:")
        for idx, movie in enumerate(movie_dicts[:10], 1):  ***REMOVED*** Show first 10 movies
            imdb_info = f" (IMDb: {movie.get('imdb_rating')})" if movie.get("imdb_rating") else ""
            tmdb_info = f" (TMDB: {movie.get('tmdb_rating')})" if movie.get("tmdb_rating") else ""
            ratings = f"{imdb_info}{tmdb_info}" if (imdb_info or tmdb_info) else ""

            ***REMOVED*** Get genres if available
            genre_text = ""
            if movie.get("genres"):
                genre_names = [g.get("name", "") for g in movie.get("genres", [])]
                if genre_names:
                    genre_text = f" - Genres: {', '.join(genre_names)}"

            release_date = movie.get("release_date")
            if release_date:
                if isinstance(release_date, date):
                    release_date = release_date.strftime("%Y-%m-%d")
            else:
                release_date = "Unknown"

            formatted_results.append(
                f"  {idx}. {movie.get('title')} ({release_date}){ratings}{genre_text}"
            )

        if len(movie_dicts) > 10:
            formatted_results.append(f"  ... and {len(movie_dicts) - 10} more movies")

    if stats["errors"]:
        formatted_results.append(f"\nErrors encountered: {len(stats['errors'])}")
        for i, error in enumerate(stats["errors"][:5]):  ***REMOVED*** Show first 5 errors
            formatted_results.append(f"  {i+1}. {error}")

        if len(stats["errors"]) > 5:
            formatted_results.append(f"  ... and {len(stats['errors']) - 5} more errors")
    else:
        formatted_results.append("\nNo errors encountered.")

    return "\n".join(formatted_results)
