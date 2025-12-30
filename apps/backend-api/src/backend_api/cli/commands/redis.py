"""Commands for Redis operations."""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Any

import typer
from config.logging import get_logger
from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from sqlmodel import text
from typer import Typer

from backend_api.cli.utils import display_redis_config
from backend_api.db.database import get_db
from backend_api.services.suggestion_engine import SuggestionEngine

app: Typer = typer.Typer(name="redis", help="Redis data management commands.")
console = Console()
logger = get_logger(__name__)


@app.command(name="populate-suggestions")
def populate_suggestions(
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of movies to load"),
    clear: bool = typer.Option(True, "--clear/--no-clear", help="Clear existing suggestions first"),
    include_words: bool = typer.Option(
        True, "--words/--no-words", help="Include individual words from titles"
    ),
    min_word_length: int = typer.Option(
        3, "--min-word", "-m", help="Minimum length for individual words"
    ),
    include_actors: bool = typer.Option(
        True, "--actors/--no-actors", help="Include actors in suggestions"
    ),
    include_directors: bool = typer.Option(
        True, "--directors/--no-directors", help="Include directors in suggestions"
    ),
    actor_limit: int = typer.Option(500, "--actor-limit", help="Maximum number of actors to load"),
    director_limit: int = typer.Option(
        200, "--director-limit", help="Maximum number of directors to load"
    ),
    redis_url: str = typer.Option(
        None,
        "--redis-url",
        "-r",
        help="Redis URL (defaults to REDIS_URL env var or localhost)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """
    Populate Redis with movie, actor, and director suggestions for autocomplete.

    This command fetches entities from the database and loads them into Redis
    in a format optimized for prefix searching with the search suggestions API.

    Data is stored in two formats:
    1. In a sorted set for fast prefix matching
    2. As structured JSON objects with entity details for rich UI rendering

    Examples:
        backend-api redis populate-suggestions --limit 5000
        backend-api redis populate-suggestions --no-actors --no-directors
        backend-api redis populate-suggestions --no-clear --verbose
    """
    # Get Redis URL from environment or use default
    actual_redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Display configuration
    if verbose:
        display_redis_config(
            actual_redis_url,
            {
                "Movie limit": limit,
                "Include actors": include_actors,
                "Include directors": include_directors,
                "Actor limit": actor_limit,
                "Director limit": director_limit,
                "Clear existing": clear,
                "Include words": include_words,
                "Min word length": min_word_length,
            },
            console=console,
        )

    try:
        # Run the population async task
        asyncio.run(
            _populate_suggestions_async(
                redis_url=actual_redis_url,
                limit=limit,
                clear=clear,
                include_words=include_words,
                min_word_length=min_word_length,
                include_actors=include_actors,
                include_directors=include_directors,
                actor_limit=actor_limit,
                director_limit=director_limit,
                verbose=verbose,
            )
        )

        console.print(
            "[bold green]✅ Successfully populated Redis with entity suggestions![/bold green]"
        )

    except Exception as e:
        console.log(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error populating Redis suggestions")
        raise typer.Exit(code=1)


async def _populate_suggestions_async(
    redis_url: str,
    limit: int,
    clear: bool,
    include_words: bool,
    min_word_length: int,
    include_actors: bool,
    include_directors: bool,
    actor_limit: int,
    director_limit: int,
    verbose: bool,
) -> None:
    """
    Async implementation of the suggestion population.

    Args:
        redis_url: Redis connection URL
        limit: Maximum number of movies to fetch
        clear: Whether to clear existing suggestions
        include_words: Whether to index individual words
        min_word_length: Minimum length for individual words
        include_actors: Whether to include actors
        include_directors: Whether to include directors
        actor_limit: Maximum number of actors to load
        director_limit: Maximum number of directors to load
        verbose: Enable verbose output
    """
    start_time = datetime.now()

    # Initialize Redis suggestion engine
    console.print(f"Connecting to Redis at {redis_url}")
    suggestion_engine = SuggestionEngine(redis_url)
    redis_client: Any | None = None

    try:
        await suggestion_engine.initialize()

        # Initialize Redis connection with basic configuration
        import redis.asyncio

        redis_client = redis.asyncio.Redis.from_url(
            redis_url, decode_responses=True, encoding="utf-8"
        )
        pipeline = redis_client.pipeline()
        batch_size = 100
        movie_count = 0

        # Clear existing data if requested
        if clear:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Clearing existing suggestion data...", total=1)
                if verbose:
                    console.print("Deleting existing suggestion data...")

                # Delete the sorted set
                await redis_client.delete("suggestions")

                # Delete all suggestion keys
                cursor = 0
                total_deleted = 0

                while True:
                    cursor, keys = await redis_client.scan(
                        cursor=cursor, match="suggestions:*", count=1000
                    )
                    if keys:
                        total_deleted += len(keys)
                        await redis_client.delete(*keys)

                    # Also delete entity keys
                    cursor2, entity_keys = await redis_client.scan(
                        cursor=cursor, match="entity:*", count=1000
                    )
                    if entity_keys:
                        total_deleted += len(entity_keys)
                        await redis_client.delete(*entity_keys)

                    if cursor == 0:
                        break

                if verbose:
                    console.print(f"Deleted {total_deleted} Redis keys")

                progress.update(task, completed=1)

        # Process movies
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            # Fetch movie data from database
            console.print(f"Fetching up to {limit} movies from database...")
            movies_task = progress.add_task("Fetching movies...", total=1)
            movies = await _fetch_movie_data(limit)
            progress.update(movies_task, completed=1)

            if not movies:
                console.print("[yellow]No movies found in database.[/yellow]")
            else:
                console.print(f"Found {len(movies)} movies to process")

                # Process movies
                movie_task = progress.add_task("Processing movies...", total=len(movies))

                for i, movie in enumerate(movies):
                    title = movie["title"].lower()
                    movie_id = movie["id"]

                    # Add to sorted set for prefix matching
                    pipeline.zadd("suggestions", {title: i})

                    # Add key for direct lookup
                    pipeline.set(f"suggestions:{title}", movie_id)

                    # Store detailed movie data in JSON format
                    movie_data = {
                        "id": movie["id"],
                        "title": movie["title"],
                        "type": "movie",
                        "image_path": movie.get("poster_path"),
                        "year": movie.get("release_year"),
                        "popularity": movie.get("popularity"),
                        "vote_average": movie.get("vote_average"),
                    }

                    # IMPORTANT: Store the original title format in additional_info
                    # so we have proper capitalization in UI
                    if movie_data["title"] != title:
                        movie_data["original_title_format"] = movie["title"]

                    pipeline.set(f"entity:movie:{title}", json.dumps(movie_data))

                    # Also add searchable variations of the title
                    # For titles with parentheses, add the version without parentheses
                    if "(" in title and ")" in title:
                        # Get the main title before parentheses
                        main_title = title.split("(")[0].strip()
                        if main_title:
                            pipeline.zadd("suggestions", {main_title: i})
                            pipeline.set(f"suggestions:{main_title}", movie_id)
                            pipeline.set(f"entity:movie:{main_title}", json.dumps(movie_data))

                        # Also get what's inside the parentheses
                        for paren_part in re.findall(r"\((.*?)\)", title):
                            if paren_part and len(paren_part) > 3:  # Only if meaningful
                                paren_title = paren_part.strip().lower()
                                pipeline.zadd("suggestions", {paren_title: i})
                                pipeline.set(f"suggestions:{paren_title}", movie_id)

                    # Process words for improved partial matching
                    words = re.split(r"[\s\(\)\[\]\{\}\:\;\,\.\-\_\+\=]+", title)

                    # Always add whole word indexing for better prefix matching
                    for word in [w for w in words if w and len(w) >= 3]:
                        # Add the full word
                        pipeline.zadd("suggestions", {word: i})
                        pipeline.set(f"suggestions:{word}", movie_id)

                        # For important words, also add specific prefixes
                        # This helps with searches like "bird" matching "birdman"
                        if len(word) >= 5:
                            for prefix_len in range(3, min(len(word), 6)):
                                prefix = word[:prefix_len]
                                # Store prefix with score offset to prioritize full words
                                pipeline.zadd("suggestions", {prefix: i + 100000})
                                if not await redis_client.exists(f"suggestions:{prefix}"):
                                    pipeline.set(f"suggestions:{prefix}", movie_id)

                    movie_count += 1

                    # Execute pipeline in batches
                    if (i + 1) % batch_size == 0 or i == len(movies) - 1:
                        await pipeline.execute()
                        pipeline = redis_client.pipeline()

                    progress.update(movie_task, completed=i + 1)

            # Fetch and process actors if requested
            actor_count = 0
            if include_actors:
                actors_task = progress.add_task("Fetching actors...", total=1)
                actors = await _fetch_actor_data(actor_limit)
                progress.update(actors_task, completed=1)

                if not actors:
                    console.print("[yellow]No actors found in database.[/yellow]")
                else:
                    console.print(f"Found {len(actors)} actors to process")
                    actor_task = progress.add_task("Processing actors...", total=len(actors))

                    for i, actor in enumerate(actors):
                        name = actor["name"].lower()
                        actor_id = actor["id"]

                        # Add to sorted set
                        pipeline.zadd("suggestions", {name: i + 10000})  # Offset for sorting

                        # Add key for direct lookup
                        pipeline.set(f"suggestions:{name}", actor_id)

                        # Store detailed actor data
                        actor_data = {
                            "id": actor["id"],
                            "name": actor["name"],
                            "type": "actor",
                            "image_path": actor.get("profile_path"),
                            "popularity": actor.get("popularity"),
                            "gender": actor.get("gender"),
                        }

                        pipeline.set(f"entity:actor:{name}", json.dumps(actor_data))
                        actor_count += 1

                        # Execute pipeline in batches
                        if (i + 1) % batch_size == 0 or i == len(actors) - 1:
                            await pipeline.execute()
                            pipeline = redis_client.pipeline()

                        progress.update(actor_task, completed=i + 1)

            # Fetch and process directors if requested
            director_count = 0
            if include_directors:
                directors_task = progress.add_task("Fetching directors...", total=1)
                directors = await _fetch_director_data(director_limit)
                progress.update(directors_task, completed=1)

                if not directors:
                    console.print("[yellow]No directors found in database.[/yellow]")
                else:
                    console.print(f"Found {len(directors)} directors to process")
                    director_task = progress.add_task(
                        "Processing directors...", total=len(directors)
                    )

                    for i, director in enumerate(directors):
                        name = director["name"].lower()
                        director_id = director["id"]

                        # Add to sorted set
                        pipeline.zadd("suggestions", {name: i + 20000})  # Offset for sorting

                        # Add key for direct lookup
                        pipeline.set(f"suggestions:{name}", director_id)

                        # Store detailed director data
                        director_data = {
                            "id": director["id"],
                            "name": director["name"],
                            "type": "director",
                            "image_path": director.get("profile_path"),
                            "popularity": director.get("popularity"),
                        }

                        pipeline.set(f"entity:director:{name}", json.dumps(director_data))
                        director_count += 1

                        # Execute pipeline in batches
                        if (i + 1) % batch_size == 0 or i == len(directors) - 1:
                            await pipeline.execute()
                            pipeline = redis_client.pipeline()

                        progress.update(director_task, completed=i + 1)

            # Verify results
            verify_task = progress.add_task("Verifying data...", total=1)

            # Count entries in sorted set
            zset_count = await redis_client.zcard("suggestions")

            # Count entity keys
            cursor = 0
            entity_count = 0
            while True:
                cursor, keys = await redis_client.scan(cursor=cursor, match="entity:*", count=1000)
                entity_count += len(keys)
                if cursor == 0:
                    break

            progress.update(verify_task, completed=1)

        # Show summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        console.print(
            "\n[bold green]Successfully loaded entity suggestions into Redis:[/bold green]"
        )
        console.print(f"  • Movies: {movie_count:,}")
        console.print(f"  • Actors: {actor_count:,}")
        console.print(f"  • Directors: {director_count:,}")
        console.print(f"  • Total entities: {movie_count + actor_count + director_count:,}")
        console.print(f"  • Entries in sorted set: {zset_count:,}")
        console.print(f"  • Entity detail records: {entity_count:,}")
        console.print(f"  • Duration: {duration:.2f} seconds")

    finally:
        # Close Redis connection
        if redis_client is not None:
            await redis_client.close()

        # Clean up suggestion engine connection
        await suggestion_engine.shutdown()


async def _fetch_movie_data(limit: int) -> list[dict[str, Any]]:
    """
    Fetch movie data from the database.

    Args:
        limit: Maximum number of movies to fetch

    Returns:
        List of movie data with complete information
    """
    db = next(get_db())

    try:
        # Updated query with correct column name poster_url
        query = text(
            """
            SELECT
                id,
                title,
                poster_url,
                release_date,
                popularity,
                vote_average,
                EXTRACT(YEAR FROM release_date) AS release_year
            FROM movie
            WHERE title IS NOT NULL AND title != ''
            ORDER BY popularity DESC, vote_count DESC
            LIMIT :limit
            """
        )

        result = db.execute(query, {"limit": limit})

        movies = []
        for row in result:
            movie = {
                "id": row[0],
                "title": row[1],
                "poster_path": row[2],  # Using poster_url as poster_path
                "release_date": row[3].isoformat() if row[3] else None,
                "popularity": float(row[4]) if row[4] else None,
                "vote_average": float(row[5]) if row[5] else None,
                "release_year": int(row[6]) if row[6] else None,
            }
            movies.append(movie)

        return movies

    finally:
        db.close()


async def _fetch_actor_data(limit: int) -> list[dict[str, Any]]:
    """
    Fetch actor data from the database.

    Args:
        limit: Maximum number of actors to fetch

    Returns:
        List of actor data with complete information
    """
    db = next(get_db())

    try:
        # Updated query to use the Credit table for actors
        query = text(
            """
            SELECT
                c.tmdb_person_id as id,
                c.name,
                c.profile_path,
                c.popularity
            FROM credit c
            WHERE
                c.name IS NOT NULL
                AND c.name != ''
                AND c.department = 'Acting'
            GROUP BY c.tmdb_person_id, c.name, c.profile_path, c.popularity
            ORDER BY c.popularity DESC
            LIMIT :limit
            """
        )

        result = db.execute(query, {"limit": limit})

        actors = []
        for row in result:
            actor = {
                "id": row[0],
                "name": row[1],
                "profile_path": row[2],
                "popularity": float(row[3]) if row[3] else None,
                "gender": None,
            }
            actors.append(actor)

        return actors

    finally:
        db.close()


async def _fetch_director_data(limit: int) -> list[dict[str, Any]]:
    """
    Fetch director data from the database.

    Args:
        limit: Maximum number of directors to fetch

    Returns:
        List of director data with complete information
    """
    db = next(get_db())

    try:
        # Updated query to use the Credit table for directors
        query = text(
            """
            SELECT
                c.tmdb_person_id as id,
                c.name,
                c.profile_path,
                c.popularity
            FROM credit c
            WHERE
                c.name IS NOT NULL
                AND c.name != ''
                AND c.department = 'Directing'
                AND c.job = 'Director'
            GROUP BY c.tmdb_person_id, c.name, c.profile_path, c.popularity
            ORDER BY c.popularity DESC
            LIMIT :limit
            """
        )

        result = db.execute(query, {"limit": limit})

        directors = []
        for row in result:
            director = {
                "id": row[0],
                "name": row[1],
                "profile_path": row[2],
                "popularity": float(row[3]) if row[3] else None,
            }
            directors.append(director)

        return directors

    finally:
        db.close()


# Register with cache command group
from backend_api.cli import cache_app  # noqa: E402

cache_app.add_typer(app, name="redis")
