"""Redis management commands for the Search API CLI."""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
import structlog
import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.table import Table
from typer import Typer

from search_api.config.app import get_search_settings
from search_api.services.suggestion_engine import SuggestionEngine
from search_api.services.backend_client import BackendAPIClient
from config.logging import get_logger

app: Typer = typer.Typer(
    name="redis", help="Redis data management commands for search suggestions."
)
console = Console()
logger = get_logger(__name__)


def display_redis_config(redis_url: str, options: Dict[str, Any], console: Console) -> None:
    """Display Redis configuration in a formatted way."""
    ***REMOVED*** Mask sensitive parts of the URL
    masked_url = redis_url
    if "@" in redis_url:
        parts = redis_url.split("@")
        if len(parts) > 1:
            masked_url = f"{parts[0].split('://')[0]}://***@{parts[1]}"

    console.print(f"\n[bold blue]Redis Configuration:[/bold blue]")
    console.print(f"  Redis URL: {masked_url}")

    for key, value in options.items():
        console.print(f"  {key}: {value}")
    console.print()


@app.command(name="populate-suggestions")
def populate_suggestions(
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of movies to load"),
    clear: bool = typer.Option(True, "--clear/--no-clear", help="Clear existing suggestions first"),
    fetch_all: bool = typer.Option(
        False, "--fetch-all", help="Fetch ALL available data from database (ignores limit)"
    ),
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
    entity_types: str = typer.Option(
        "movie,actor,director",
        "--entity-types",
        help="Comma-separated list of entity types to populate (e.g., 'movie,actor,director,series')",
    ),
    actor_limit: int = typer.Option(500, "--actor-limit", help="Maximum number of actors to load"),
    director_limit: int = typer.Option(
        200, "--director-limit", help="Maximum number of directors to load"
    ),
    batch_size: int = typer.Option(
        100, "--batch-size", help="Number of operations to batch in Redis pipeline"
    ),
    redis_url: str = typer.Option(
        None,
        "--redis-url",
        "-r",
        help="Redis URL (defaults to config or localhost)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    validate_data: bool = typer.Option(
        True, "--validate/--no-validate", help="Validate data consistency after population"
    ),
) -> None:
    """
    Populate Redis with movie, actor, and director suggestions for autocomplete.

    This command fetches entities from the Backend API and loads them into Redis
    in a format optimized for prefix searching with the search suggestions API.

    Data is stored in two formats:
    1. In a sorted set for fast prefix matching
    2. As structured JSON objects with entity details for rich UI rendering

    Examples:
        search-api cli redis populate-suggestions --limit 5000
        search-api cli redis populate-suggestions --fetch-all --verbose
        search-api cli redis populate-suggestions --no-actors --no-directors
        search-api cli redis populate-suggestions --no-clear --verbose
        search-api cli redis populate-suggestions --entity-types "movie,actor" --batch-size 200
        search-api cli redis populate-suggestions --fetch-all --no-validate
    """
    ***REMOVED*** Get configuration
    config = get_search_settings()

    ***REMOVED*** Parse entity types
    enabled_entity_types = [t.strip() for t in entity_types.split(",") if t.strip()]

    ***REMOVED*** Override individual flags with entity_types parameter
    include_movies = "movie" in enabled_entity_types
    include_actors = include_actors and "actor" in enabled_entity_types
    include_directors = include_directors and "director" in enabled_entity_types

    ***REMOVED*** Get Redis URL from parameter, config, or default
    actual_redis_url = redis_url or config.redis_url or "redis://localhost:6379/0"

    ***REMOVED*** Determine actual limit based on fetch_all flag
    actual_limit = None if fetch_all else limit
    display_limit = "ALL" if fetch_all else str(limit)

    ***REMOVED*** Display configuration
    if verbose:
        display_redis_config(
            actual_redis_url,
            {
                "Movie limit": display_limit,
                "Fetch all data": fetch_all,
                "Include actors": include_actors,
                "Include directors": include_directors,
                "Actor limit": actor_limit if include_actors else "Disabled",
                "Director limit": director_limit if include_directors else "Disabled",
                "Clear existing": clear,
                "Include words": include_words,
                "Min word length": min_word_length,
                "Backend API": config.backend_api_url,
            },
            console=console,
        )

    try:
        ***REMOVED*** Run the async population
        asyncio.run(
            _populate_suggestions_async(
                config,  ***REMOVED*** First parameter should be config
                actual_redis_url,
                actual_limit,
                clear,
                include_words,
                min_word_length,
                include_movies,
                include_actors,
                include_directors,
                enabled_entity_types,
                actor_limit,
                director_limit,
                batch_size,
                verbose,
                validate_data,
            )
        )

        console.print(
            "[bold green]✅ Successfully populated Redis with entity suggestions![/bold green]"
        )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error populating Redis suggestions")
        raise typer.Exit(code=1)


async def _populate_suggestions_async(
    config: Any,
    redis_url: str,
    limit: Optional[int],
    clear: bool,
    include_words: bool,
    min_word_length: int,
    include_movies: bool,
    include_actors: bool,
    include_directors: bool,
    enabled_entity_types: List[str],
    actor_limit: int,
    director_limit: int,
    batch_size: int,
    verbose: bool,
    validate_data: bool,
) -> None:
    """
    Async implementation of the suggestion population.

    Args:
        config: Search API configuration
        redis_url: Redis connection URL
        limit: Maximum number of movies to fetch
        clear: Whether to clear existing suggestions
        include_words: Whether to index individual words
        min_word_length: Minimum length for individual words
        include_movies: Whether to include movies
        include_actors: Whether to include actors
        include_directors: Whether to include directors
        enabled_entity_types: List of enabled entity types
        actor_limit: Maximum number of actors to load
        director_limit: Maximum number of directors to load
        batch_size: Number of operations to batch in Redis pipeline
        verbose: Enable verbose output
        validate_data: Whether to validate data consistency
    """
    start_time = datetime.now()

    ***REMOVED*** Initialize Redis suggestion engine
    console.print(f"Connecting to Redis at {redis_url}")
    suggestion_engine = SuggestionEngine(redis_url)
    await suggestion_engine.initialize()

    ***REMOVED*** Initialize Backend API client
    backend_client = BackendAPIClient(config)

    try:
        ***REMOVED*** Initialize Redis connection with basic configuration
        import redis.asyncio

        redis_client = redis.asyncio.Redis.from_url(
            redis_url, decode_responses=True, encoding="utf-8"
        )

        ***REMOVED*** Clear existing data if requested
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

                ***REMOVED*** Delete the sorted set
                await redis_client.delete("suggestions")

                ***REMOVED*** Delete all suggestion keys
                cursor = 0
                total_deleted = 0

                while True:
                    cursor, keys = await redis_client.scan(
                        cursor=cursor, match="suggestions:*", count=1000
                    )
                    if keys:
                        total_deleted += len(keys)
                        await redis_client.delete(*keys)

                    ***REMOVED*** Also delete entity keys
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

        ***REMOVED*** Process movies using Backend API
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            ***REMOVED*** Initialize counters
            movie_count = 0

            ***REMOVED*** Fetch and process movies if requested
            movie_count = 0
            if include_movies:
                ***REMOVED*** Fetch movie data from Backend API
                console.print(
                    f"Fetching {'ALL available' if limit is None else f'up to {limit}'} movies from Backend API..."
                )
                movies_task = progress.add_task("Fetching movies...", total=1)
                movies = await _fetch_movie_data_from_backend(backend_client, limit)
                progress.update(movies_task, completed=1)

                if not movies:
                    console.print("[yellow]No movies found in Backend API.[/yellow]")
                else:
                    console.print(f"Found {len(movies)} movies to process")

                    ***REMOVED*** Process movies
                    movie_task = progress.add_task("Processing movies...", total=len(movies))
                    pipeline = redis_client.pipeline()
                    ***REMOVED*** Use configurable batch size for better performance tuning

                    for i, movie in enumerate(movies):
                        title = movie["title"].lower()
                        movie_id = movie["id"]

                        ***REMOVED*** Add to sorted set for prefix matching
                        pipeline.zadd("suggestions", {title: i})

                        ***REMOVED*** Add key for direct lookup
                        pipeline.set(f"suggestions:{title}", movie_id)

                        ***REMOVED*** Store detailed movie data in JSON format
                        movie_data = {
                            "id": movie["id"],
                            "title": movie["title"],
                            "type": "movie",
                            "image_path": movie.get("poster_path"),
                            "year": movie.get("release_year"),
                            "popularity": movie.get("popularity"),
                            "vote_average": movie.get("vote_average"),
                            "original_title_format": movie["title"],
                            ***REMOVED*** Store additional movie fields for comprehensive search
                            "overview": movie.get("overview"),
                            "release_date": movie.get("release_date"),
                            "backdrop_url": movie.get("backdrop_url"),
                            "imdb_rating": movie.get("imdb_rating"),
                            "runtime": movie.get("runtime"),
                            "genres": movie.get("genres", []),
                            "tmdb_id": movie.get("tmdb_id"),
                            "imdb_id": movie.get("imdb_id"),
                        }

                        pipeline.set(f"entity:movie:{title}", json.dumps(movie_data))

                        ***REMOVED*** Add entity lookup by ID for efficient suggestion resolution
                        pipeline.set(f"entity:id:{movie_id}", json.dumps(movie_data))

                        ***REMOVED*** Add searchable variations of the title
                        if "(" in title and ")" in title:
                            ***REMOVED*** Get the main title before parentheses
                            main_title = title.split("(")[0].strip()
                            if main_title:
                                pipeline.zadd("suggestions", {main_title: i})
                                pipeline.set(f"suggestions:{main_title}", movie_id)
                                pipeline.set(f"entity:movie:{main_title}", json.dumps(movie_data))

                            ***REMOVED*** Also get what's inside the parentheses
                            for paren_part in re.findall(r"\((.*?)\)", title):
                                if paren_part and len(paren_part) > 3:
                                    paren_title = paren_part.strip().lower()
                                    pipeline.zadd("suggestions", {paren_title: i})
                                    pipeline.set(f"suggestions:{paren_title}", movie_id)

                        ***REMOVED*** Process words for improved partial matching
                        if include_words:
                            words = re.split(r"[\s\(\)\[\]\{\}\:\;\,\.\-\_\+\=]+", title)

                            for word in [w for w in words if w and len(w) >= min_word_length]:
                                ***REMOVED*** Add the full word
                                pipeline.zadd("suggestions", {word: i})
                                pipeline.set(f"suggestions:{word}", movie_id)

                                ***REMOVED*** For important words, also add specific prefixes
                                if len(word) >= 5:
                                    for prefix_len in range(min_word_length, min(len(word), 6)):
                                        prefix = word[:prefix_len]
                                        ***REMOVED*** Store prefix with score offset to prioritize full words
                                        pipeline.zadd("suggestions", {prefix: i + 100000})
                                        if not await redis_client.exists(f"suggestions:{prefix}"):
                                            pipeline.set(f"suggestions:{prefix}", movie_id)

                        movie_count += 1

                        ***REMOVED*** Execute pipeline in batches
                        if (i + 1) % batch_size == 0 or i == len(movies) - 1:
                            await pipeline.execute()
                            pipeline = redis_client.pipeline()

                        progress.update(movie_task, completed=i + 1)

            ***REMOVED*** Fetch and process actors if requested
            actor_count = 0
            if include_actors:
                actors_task = progress.add_task("Fetching actors...", total=1)
                actors = await _fetch_actor_data_from_backend(backend_client, actor_limit)
                progress.update(actors_task, completed=1)

                if not actors:
                    console.print("[yellow]No actors found in Backend API.[/yellow]")
                else:
                    console.print(f"Found {len(actors)} actors to process")
                    actor_task = progress.add_task("Processing actors...", total=len(actors))

                    for i, actor in enumerate(actors):
                        name = actor["name"].lower()
                        actor_id = actor["id"]

                        ***REMOVED*** Add to sorted set
                        pipeline.zadd("suggestions", {name: i + 10000})  ***REMOVED*** Offset for sorting

                        ***REMOVED*** Add key for direct lookup
                        pipeline.set(f"suggestions:{name}", actor_id)

                        ***REMOVED*** Store detailed actor data
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

                        ***REMOVED*** Execute pipeline in batches
                        if (i + 1) % batch_size == 0 or i == len(actors) - 1:
                            await pipeline.execute()
                            pipeline = redis_client.pipeline()

                        progress.update(actor_task, completed=i + 1)

            ***REMOVED*** Fetch and process directors if requested
            director_count = 0
            if include_directors:
                directors_task = progress.add_task("Fetching directors...", total=1)
                directors = await _fetch_director_data_from_backend(backend_client, director_limit)
                progress.update(directors_task, completed=1)

                if not directors:
                    console.print("[yellow]No directors found in Backend API.[/yellow]")
                else:
                    console.print(f"Found {len(directors)} directors to process")
                    director_task = progress.add_task(
                        "Processing directors...", total=len(directors)
                    )

                    for i, director in enumerate(directors):
                        name = director["name"].lower()
                        director_id = director["id"]

                        ***REMOVED*** Add to sorted set
                        pipeline.zadd("suggestions", {name: i + 20000})  ***REMOVED*** Offset for sorting

                        ***REMOVED*** Add key for direct lookup
                        pipeline.set(f"suggestions:{name}", director_id)

                        ***REMOVED*** Store detailed director data
                        director_data = {
                            "id": director["id"],
                            "name": director["name"],
                            "type": "director",
                            "image_path": director.get("profile_path"),
                            "popularity": director.get("popularity"),
                        }

                        pipeline.set(f"entity:director:{name}", json.dumps(director_data))
                        director_count += 1

                        ***REMOVED*** Execute pipeline in batches
                        if (i + 1) % batch_size == 0 or i == len(directors) - 1:
                            await pipeline.execute()
                            pipeline = redis_client.pipeline()

                        progress.update(director_task, completed=i + 1)

            ***REMOVED*** Verify results
            verify_task = progress.add_task("Verifying data...", total=1)

            ***REMOVED*** Count entries in sorted set
            zset_count = await redis_client.zcard("suggestions")

            ***REMOVED*** Count entity keys
            cursor = 0
            entity_count = 0
            while True:
                cursor, keys = await redis_client.scan(cursor=cursor, match="entity:*", count=1000)
                entity_count += len(keys)
                if cursor == 0:
                    break

            progress.update(verify_task, completed=1)

        ***REMOVED*** Validate data consistency if requested
        validation_results = {}
        if validate_data:
            validation_task = progress.add_task(
                "Validating data consistency...", total=len(enabled_entity_types)
            )

            for entity_type in enabled_entity_types:
                entity_keys = []
                cursor = 0
                while True:
                    cursor, keys = await redis_client.scan(
                        cursor=cursor, match=f"entity:{entity_type}:*", count=1000
                    )
                    entity_keys.extend(keys)
                    if cursor == 0:
                        break

                ***REMOVED*** Check if entity keys have corresponding suggestion keys
                valid_entities = 0
                invalid_entities = []

                for entity_key in entity_keys[: min(100, len(entity_keys))]:  ***REMOVED*** Sample validation
                    entity_name = entity_key.split(":", 2)[2] if ":" in entity_key else None
                    if entity_name:
                        suggestion_key = f"suggestions:{entity_name}"
                        if await redis_client.exists(suggestion_key):
                            valid_entities += 1
                        else:
                            invalid_entities.append(entity_name)

                validation_results[entity_type] = {
                    "total_entities": len(entity_keys),
                    "sampled": min(100, len(entity_keys)),
                    "valid": valid_entities,
                    "invalid": len(invalid_entities),
                    "invalid_samples": invalid_entities[:5],  ***REMOVED*** Show first 5 invalid
                }

                progress.update(validation_task, advance=1)

        ***REMOVED*** Show summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        console.print(
            f"\n[bold green]Successfully loaded entity suggestions into Redis:[/bold green]"
        )
        console.print(f"  • Movies: {movie_count:,}")
        console.print(f"  • Actors: {actor_count:,}")
        console.print(f"  • Directors: {director_count:,}")
        console.print(f"  • Total entities: {movie_count + actor_count + director_count:,}")
        console.print(f"  • Entries in sorted set: {zset_count:,}")
        console.print(f"  • Entity detail records: {entity_count:,}")
        console.print(f"  • Duration: {duration:.2f} seconds")

        ***REMOVED*** Display validation results if requested
        if validate_data:
            console.print("\n[bold blue]Data Validation Results:[/bold blue]")
            for entity_type, result in validation_results.items():
                console.print(f"  {entity_type}:")
                console.print(f"    Total entities: {result['total_entities']:,}")
                console.print(f"    Sampled for validation: {result['sampled']:,}")
                console.print(f"    Valid: {result['valid']:,}")
                console.print(f"    Invalid: {result['invalid']:,}")
                if result["invalid_samples"]:
                    samples = result["invalid_samples"]
                    if isinstance(samples, (list, tuple)):
                        console.print(f"    Invalid samples: {', '.join(str(s) for s in samples)}")
                    else:
                        console.print(f"    Invalid samples: {samples}")

    finally:
        ***REMOVED*** Close connections
        await redis_client.close()
        await suggestion_engine.shutdown()


async def _fetch_movie_data_from_backend(
    backend_client: BackendAPIClient, limit: Optional[int]
) -> List[Dict[str, Any]]:
    """
    Fetch movie data from the Backend API with pagination support.

    Args:
        backend_client: Backend API client instance
        limit: Maximum number of movies to fetch, or None to fetch all available

    Returns:
        List of movie data with complete information
    """
    try:
        movies: List[Dict[str, Any]] = []
        page = 1
        page_size = 100  ***REMOVED*** Backend API limit is 100

        ***REMOVED*** If no limit specified, use a very high number to fetch all
        effective_limit = limit if limit is not None else 999999

        while len(movies) < effective_limit:
            ***REMOVED*** Calculate how many more movies we need
            remaining = effective_limit - len(movies)
            current_page_size = min(remaining, 100)

            ***REMOVED*** Use the Backend API movies endpoint to get all movies
            ***REMOVED*** This is more reliable than searching for specific letters
            try:
                response = await backend_client.list_movies(
                    page=page,
                    limit=current_page_size,
                    sort_by="imdb_rating",
                    sort_desc=True,
                )
                page_movies = response.get("results", [])
            except Exception as e:
                logger.warning(f"Movies endpoint failed, trying search fallback: {e}")
                ***REMOVED*** Fallback to search if the main endpoint fails
                response = await backend_client.search_movies(
                    query="e",  ***REMOVED*** Most common letter
                    page=page,
                    limit=current_page_size,
                    sort_by="imdb_rating",
                    sort_desc=True,
                )
                page_movies = response.get("results", [])

            ***REMOVED*** If no movies returned, we've reached the end
            if not page_movies:
                break

            for movie in page_movies:
                movie_data = {
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "poster_path": movie.get("poster_url"),
                    "release_date": movie.get("release_date"),
                    "popularity": movie.get("popularity"),
                    "vote_average": movie.get("vote_average"),
                    "release_year": None,
                }

                ***REMOVED*** Extract year from release_date if available
                if movie_data["release_date"]:
                    try:
                        if isinstance(movie_data["release_date"], str):
                            movie_data["release_year"] = int(movie_data["release_date"][:4])
                    except (ValueError, IndexError):
                        pass

                movies.append(movie_data)

                ***REMOVED*** Stop if we've reached our limit (only when limit is specified)
                if limit is not None and len(movies) >= limit:
                    break

            page += 1

            ***REMOVED*** Safety check to prevent infinite loops (only when fetching all)
            if limit is None and page > 200:  ***REMOVED*** Max 200 pages = 20,000 movies for fetch-all
                logger.warning(
                    f"Reached maximum page limit (200) for fetch-all, stopping at {len(movies)} movies"
                )
                break
            elif limit is not None and page > 50:  ***REMOVED*** Original limit for specified limits
                logger.warning(f"Reached maximum page limit (50), stopping at {len(movies)} movies")
                break

        logger.info(f"Fetched {len(movies)} movies from Backend API using {page-1} page(s)")
        return movies

    except Exception as e:
        logger.error(f"Error fetching movie data from Backend API: {e}")
        return []


async def _fetch_actor_data_from_backend(
    backend_client: BackendAPIClient, limit: int
) -> List[Dict[str, Any]]:
    """
    Fetch actor data from the Backend API with pagination support.

    Args:
        backend_client: Backend API client instance
        limit: Maximum number of actors to fetch

    Returns:
        List of actor data with complete information
    """
    try:
        actors: List[Dict[str, Any]] = []
        page = 1

        while len(actors) < limit:
            ***REMOVED*** Calculate how many more actors we need
            remaining = limit - len(actors)
            current_page_size = min(remaining, 100)  ***REMOVED*** Backend API limit is 100

            ***REMOVED*** Fetch actors from Backend API
            response = await backend_client.list_actors(
                page=page,
                limit=current_page_size,
            )

            page_actors = response.get("actors", [])

            ***REMOVED*** If no actors returned, we've reached the end
            if not page_actors:
                break

            for actor in page_actors:
                actor_data = {
                    "id": actor.get("id"),
                    "name": actor.get("name"),
                    "profile_path": actor.get("profile_path"),
                    "popularity": actor.get("popularity"),
                }

                actors.append(actor_data)

                ***REMOVED*** Stop if we've reached our limit
                if len(actors) >= limit:
                    break

            page += 1

            ***REMOVED*** Safety check to prevent infinite loops
            if page > 50:  ***REMOVED*** Max 50 pages = 5000 actors
                logger.warning(f"Reached maximum page limit (50), stopping at {len(actors)} actors")
                break

        logger.info(f"Fetched {len(actors)} actors from Backend API using {page-1} page(s)")
        return actors

    except Exception as e:
        logger.error(f"Error fetching actor data from Backend API: {e}")
        return []


async def _fetch_director_data_from_backend(
    backend_client: BackendAPIClient, limit: int
) -> List[Dict[str, Any]]:
    """
    Fetch director data from the Backend API.

    Args:
        backend_client: Backend API client instance
        limit: Maximum number of directors to fetch

    Returns:
        List of director data with complete information
    """
    try:
        ***REMOVED*** Directors are not yet available via a direct endpoint in Backend API
        ***REMOVED*** They would need to be extracted from movie credits or a dedicated endpoint
        ***REMOVED*** TODO: Implement when Backend API adds a directors endpoint
        logger.info(
            f"Director fetching not yet implemented for Backend API (no dedicated endpoint)"
        )
        return []

    except Exception as e:
        logger.error(f"Error fetching director data from Backend API: {e}")
        return []


@app.command(name="test-suggestions")
def test_suggestions(
    query: str = typer.Argument(..., help="Test query to search for"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of suggestions to retrieve"),
    redis_url: str = typer.Option(
        None,
        "--redis-url",
        "-r",
        help="Redis URL (defaults to config or localhost)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """
    Test the Redis suggestion engine with a query.

    Examples:
        search-api cli redis test-suggestions "star"
        search-api cli redis test-suggestions "batman" --limit 10
    """
    ***REMOVED*** Get configuration
    config = get_search_settings()
    actual_redis_url = redis_url or config.redis_url or "redis://localhost:6379/0"

    console.print(f"[bold blue]Testing suggestions for query: '{query}'[/bold blue]")
    if verbose:
        console.print(f"Redis URL: {actual_redis_url}")
        console.print(f"Limit: {limit}")

    try:
        asyncio.run(_test_suggestions_async(actual_redis_url, query, limit, verbose))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error testing suggestions")
        raise typer.Exit(code=1)


async def _test_suggestions_async(redis_url: str, query: str, limit: int, verbose: bool) -> None:
    """Test suggestions asynchronously."""
    suggestion_engine = SuggestionEngine(redis_url)
    await suggestion_engine.initialize()

    try:
        ***REMOVED*** Test basic suggestions
        console.print(f"\n[bold green]Basic suggestions:[/bold green]")
        basic_suggestions = await suggestion_engine.get_suggestions(query, limit)

        if basic_suggestions:
            for i, suggestion in enumerate(basic_suggestions, 1):
                console.print(f"  {i}. {suggestion}")
        else:
            console.print("  No basic suggestions found")

        ***REMOVED*** Test entity suggestions
        console.print(f"\n[bold green]Entity suggestions:[/bold green]")
        entity_suggestions = await suggestion_engine.get_entity_suggestions(query, limit)

        if entity_suggestions:
            for i, suggestion_dict in enumerate(entity_suggestions, 1):
                console.print(
                    f"  {i}. {suggestion_dict.get('text', '')} ({suggestion_dict.get('type', 'unknown')})"
                )
                if verbose and suggestion_dict.get("additional_info"):
                    console.print(f"     Additional info: {suggestion_dict['additional_info']}")
        else:
            console.print("  No entity suggestions found")

        ***REMOVED*** Test ranked suggestions
        console.print(f"\n[bold green]Ranked suggestions:[/bold green]")
        ranked_suggestions = await suggestion_engine.get_ranked_suggestions(query, limit)

        if ranked_suggestions:
            for i, suggestion_dict in enumerate(ranked_suggestions, 1):
                text = suggestion_dict.get("text", "")
                suggestion_type = suggestion_dict.get("type", "unknown")
                search_type = suggestion_dict.get("search_type", "unknown")
                console.print(f"  {i}. {text} ({suggestion_type}, {search_type})")
                if verbose:
                    console.print(
                        f"     ID: {suggestion_dict.get('id')}, Popularity: {suggestion_dict.get('popularity')}"
                    )
        else:
            console.print("  No ranked suggestions found")

    finally:
        await suggestion_engine.shutdown()


@app.command(name="info")
def redis_info(
    redis_url: str = typer.Option(
        None,
        "--redis-url",
        "-r",
        help="Redis URL (defaults to config or localhost)",
    ),
) -> None:
    """
    Show Redis connection and suggestion data information.
    """
    ***REMOVED*** Get configuration
    config = get_search_settings()
    actual_redis_url = redis_url or config.redis_url or "redis://localhost:6379/0"

    try:
        asyncio.run(_redis_info_async(actual_redis_url))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error getting Redis info")
        raise typer.Exit(code=1)


async def _redis_info_async(redis_url: str) -> None:
    """Get Redis info asynchronously."""
    suggestion_engine = SuggestionEngine(redis_url)

    try:
        ***REMOVED*** Initialize Redis connection first
        await suggestion_engine.initialize()

        ***REMOVED*** Test Redis connection
        health = await suggestion_engine.health_check()

        console.print(f"[bold blue]Redis Connection Info:[/bold blue]")
        console.print(f"  Status: {health.get('status', 'unknown')}")
        console.print(f"  Redis URL: {health.get('redis_url', 'unknown')}")

        if health.get("status") == "healthy":
            import redis.asyncio

            redis_client = redis.asyncio.Redis.from_url(redis_url, decode_responses=True)

            ***REMOVED*** Get counts
            zset_count = await redis_client.zcard("suggestions")

            ***REMOVED*** Count entity keys
            cursor = 0
            entity_count = 0
            suggestion_count = 0

            while True:
                cursor, keys = await redis_client.scan(cursor=cursor, match="*", count=1000)
                for key in keys:
                    if key.startswith("entity:"):
                        entity_count += 1
                    elif key.startswith("suggestions:"):
                        suggestion_count += 1
                if cursor == 0:
                    break

            console.print(f"\n[bold green]Redis Data Summary:[/bold green]")
            console.print(f"  Sorted set entries: {zset_count:,}")
            console.print(f"  Entity records: {entity_count:,}")
            console.print(f"  Suggestion keys: {suggestion_count:,}")
            console.print(f"  Features: {health.get('features', {})}")

            await redis_client.close()
        else:
            console.print(f"  Error: {health.get('error', 'unknown error')}")

    finally:
        await suggestion_engine.shutdown()
