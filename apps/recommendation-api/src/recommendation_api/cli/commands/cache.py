"""CLI commands for managing the recommendation cache."""

import logging
import time
from typing import Optional, List, Tuple
from pathlib import Path

import typer
from typer import Typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

from recommendation_api.db import get_db_context, get_all_movie_ids
from recommendation_api.services.cache_service import get_cache_service
from recommendation_api.repositories.redis import get_redis_repository
from recommendation_api.config import settings
from recommendation_api.config.logging import configure_logging

***REMOVED*** Create Typer app
app: Typer = typer.Typer(
    name="cache",
    help="Manage the recommendation cache",
    add_completion=False,
)

***REMOVED*** Create console for rich output
console = Console()
logger = logging.getLogger(__name__)


@app.command("precompute")
def precompute_similar_movies(
    limit: int = typer.Option(
        50, "--limit", "-l", help="Maximum number of similar movies per movie"
    ),
    min_score: float = typer.Option(
        0.01, "--min-score", "-s", help="Minimum similarity score threshold"
    ),
    ttl: Optional[int] = typer.Option(
        None, "--ttl", "-t", help="Cache TTL in seconds (default: from config)"
    ),
    batch_size: int = typer.Option(
        100, "--batch-size", "-b", help="Number of movies to process in each batch"
    ),
    movie_ids: Optional[List[int]] = typer.Option(
        None, "--movie-id", "-m", help="Specific movie IDs to process (comma-separated)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
):
    """Precompute similar movies and store them in the Redis cache.

    This command processes movies in batches, finds similar movies for each one,
    and stores the results in Redis for fast retrieval.
    """
    ***REMOVED*** Configure logging for this command
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "ERROR"
    else:
        log_level = "WARNING"  ***REMOVED*** Default to WARNING to reduce noise

    configure_logging(log_level=log_level, verbose=verbose)

    ***REMOVED*** Suppress noisy logs unless in verbose mode
    noisy_loggers = [
        "httpx",
        "qdrant_client",
        "sentence_transformers",
        "recommendation_api.repositories.vector.repository",
        "recommendation_api.repositories.vector.client",
        "recommendation_api.services.vector_service",
        "recommendation_api.services.cache_service",
        "recommendation_api.repositories.redis.repository",
    ]

    if verbose:
        ***REMOVED*** In verbose mode, show more details but still suppress the noisiest ones
        for logger_name in ["httpx", "qdrant_client", "sentence_transformers"]:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    else:
        ***REMOVED*** In normal mode, suppress all noisy loggers
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)

    ***REMOVED*** Validate Redis connection
    console.print("[cyan]Checking Redis connection...[/cyan]")
    redis_repo = get_redis_repository()
    if not redis_repo.ping():
        console.print("[bold red]Error:[/bold red] Could not connect to Redis")
        raise typer.Exit(code=1)

    console.print("[green]✓ Redis connection successful[/green]")

    with get_db_context() as session:
        ***REMOVED*** Initialize cache service
        cache_service = get_cache_service(session)

        ***REMOVED*** Convert movie_ids to list if provided
        movie_id_list = None
        if movie_ids:
            movie_id_list = [int(movie_id) for movie_id in movie_ids]
            console.print(
                f"[cyan]Processing [bold]{len(movie_id_list)}[/bold] specific movies[/cyan]"
            )
        else:
            console.print("[cyan]Processing [bold]all[/bold] movies from database[/cyan]")

        ***REMOVED*** Get total count for progress tracking
        if movie_id_list:
            total_movies = len(movie_id_list)
        else:
            ***REMOVED*** Get all movie IDs to calculate total
            all_movie_ids = get_all_movie_ids(session)
            total_movies = len(all_movie_ids)

        total_batches = (total_movies + batch_size - 1) // batch_size
        console.print(
            f"[dim]Will process {total_movies} movies in {total_batches} batches of {batch_size}[/dim]"
        )

        ***REMOVED*** Track progress manually for better control
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        start_time = time.time()

        ***REMOVED*** Temporarily suppress logs during precomputation unless verbose
        if not verbose:
            temp_loggers = {}
            for logger_name in noisy_loggers:
                logger = logging.getLogger(logger_name)
                temp_loggers[logger_name] = logger.level
                logger.setLevel(logging.CRITICAL)

        try:
            if not quiet:
                ***REMOVED*** Use rich Progress for better progress tracking
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    TextColumn("•"),
                    TextColumn("[cyan]{task.fields[processed]}[/cyan] processed"),
                    TextColumn("•"),
                    TextColumn("[blue]{task.fields[skipped]}[/blue] skipped"),
                    TextColumn("•"),
                    TextColumn("[red]{task.fields[failed]}[/red] failed"),
                    TextColumn("•"),
                    TextColumn("[green]{task.fields[speed]:.1f}[/green] movies/s"),
                    console=console,
                    transient=False,
                ) as progress:

                    task = progress.add_task(
                        "[cyan]Precomputing similar movies...",
                        total=total_movies,
                        processed=0,
                        skipped=0,
                        failed=0,
                        speed=0.0,
                    )

                    ***REMOVED*** Process in batches with custom progress tracking
                    current_batch = 0
                    batch_movie_ids = movie_id_list if movie_id_list else get_all_movie_ids(session)

                    for i in range(0, len(batch_movie_ids), batch_size):
                        current_batch += 1
                        batch = batch_movie_ids[i : i + batch_size]

                        ***REMOVED*** Update task description with batch info
                        progress.update(
                            task,
                            description=f"[cyan]Processing batch {current_batch}/{total_batches} ({len(batch)} movies)...",
                        )

                        ***REMOVED*** Process this batch
                        batch_results = cache_service.precompute_similar_movies(
                            movie_ids=batch,
                            limit=limit,
                            min_score=min_score,
                            ttl=ttl,
                            batch_size=len(batch),  ***REMOVED*** Process the whole batch at once
                        )

                        ***REMOVED*** Update counters
                        processed_count += batch_results.get("processed", 0)
                        skipped_count += batch_results.get("skipped", 0)
                        failed_count += batch_results.get("failed", 0)

                        ***REMOVED*** Calculate speed
                        elapsed = time.time() - start_time
                        speed = (
                            (processed_count + skipped_count + failed_count) / elapsed
                            if elapsed > 0
                            else 0
                        )

                        ***REMOVED*** Update progress
                        progress.update(
                            task,
                            advance=len(batch),
                            processed=processed_count,
                            skipped=skipped_count,
                            failed=failed_count,
                            speed=speed,
                        )

                        ***REMOVED*** Show batch summary in verbose mode
                        if verbose:
                            console.print(
                                f"[dim]Batch {current_batch}: "
                                f"{batch_results.get('processed', 0)} processed, "
                                f"{batch_results.get('skipped', 0)} skipped, "
                                f"{batch_results.get('failed', 0)} failed[/dim]"
                            )

                    ***REMOVED*** Final update
                    progress.update(task, description="[green]✓ Precomputation completed!")

                ***REMOVED*** Prepare results for display
                elapsed_time = time.time() - start_time
                results = {
                    "total": total_movies,
                    "processed": processed_count,
                    "skipped": skipped_count,
                    "failed": failed_count,
                    "elapsed_time": elapsed_time,
                    "movies_per_second": (
                        (processed_count + skipped_count + failed_count) / elapsed_time
                        if elapsed_time > 0
                        else 0
                    ),
                }
            else:
                ***REMOVED*** Silent processing in quiet mode - use original method
                results = cache_service.precompute_similar_movies(
                    movie_ids=movie_id_list,
                    limit=limit,
                    min_score=min_score,
                    ttl=ttl,
                    batch_size=batch_size,
                )
        finally:
            ***REMOVED*** Restore log levels
            if not verbose:
                for logger_name, level in temp_loggers.items():
                    logging.getLogger(logger_name).setLevel(level)

        ***REMOVED*** Print results
        console.print("\n[bold green]✓ Precomputation completed![/bold green]")

        ***REMOVED*** Create a table for results
        table = Table(title="Precomputation Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Movies", str(results["total"]))
        table.add_row("Processed", str(results["processed"]))
        table.add_row("Skipped", str(results["skipped"]))
        table.add_row("Failed", str(results["failed"]))
        table.add_row("Elapsed Time", f"{results['elapsed_time']:.2f} seconds")
        table.add_row("Processing Speed", f"{results['movies_per_second']:.2f} movies/second")

        console.print(table)

        ***REMOVED*** Add completion message based on results
        if results["failed"] > 0:
            console.print(f"\n[yellow]⚠ Completed with {results['failed']} failures[/yellow]")
            if not verbose:
                console.print("[dim]Use --verbose to see detailed error information.[/dim]")
        elif results["processed"] > 0:
            console.print(
                f"\n[green]Successfully cached similar movies for {results['processed']} movies[/green]"
            )
        else:
            console.print("\n[blue]ℹ No movies were processed[/blue]")


@app.command("info")
def get_cache_info(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
):
    """Get information about the recommendation cache."""
    ***REMOVED*** Configure logging for this command
    log_level = "WARNING" if not verbose else "INFO"
    if quiet:
        log_level = "ERROR"

    configure_logging(log_level=log_level, verbose=verbose)

    ***REMOVED*** Suppress noisy logs
    if not verbose:
        noisy_loggers = [
            "httpx",
            "qdrant_client",
            "sentence_transformers",
            "recommendation_api.repositories.redis.repository",
            "recommendation_api.services.cache_service",
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)

    ***REMOVED*** Validate Redis connection
    if not quiet:
        console.print("[cyan]Checking Redis connection...[/cyan]")

    redis_repo = get_redis_repository()
    if not redis_repo.ping():
        console.print("[bold red]Error:[/bold red] Could not connect to Redis")
        raise typer.Exit(code=1)

    with get_db_context() as session:
        ***REMOVED*** Initialize cache service
        cache_service = get_cache_service(session)

        ***REMOVED*** Get cache stats
        if not quiet:
            with console.status(
                "[bold green]Getting cache information...[/bold green]", spinner="dots"
            ):
                stats = cache_service.get_cache_stats()
        else:
            stats = cache_service.get_cache_stats()

        if "error" in stats:
            console.print(f"[bold red]Error:[/bold red] {stats['error']}")
            raise typer.Exit(code=1)

        ***REMOVED*** Create a table for basic stats
        table = Table(title="Cache Information")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        redis_info = stats["redis_info"]

        table.add_row("Status", "Connected ✅" if stats["is_connected"] else "Disconnected ❌")
        table.add_row("Redis URL", settings.redis_url)
        table.add_row("Similar Movies Count", str(redis_info.get("similar_movies_count", "N/A")))
        table.add_row("Memory Used", str(redis_info.get("memory_used", "N/A")))
        table.add_row("Total Keys", str(redis_info.get("total_keys", "N/A")))
        table.add_row("Uptime (days)", str(redis_info.get("uptime_days", "N/A")))
        table.add_row("TTL", f"{settings.redis_ttl} seconds")
        table.add_row("Caching Enabled", "Yes" if settings.enable_caching else "No")

        console.print(table)

        ***REMOVED*** Show more detailed information if verbose
        if verbose and redis_info.get("similar_movies_sample"):
            console.print("\n[bold]Sample of cached similar movies:[/bold]")
            for key in redis_info["similar_movies_sample"]:
                console.print(f"  • {key}")


@app.command("clear")
def clear_cache(
    force: bool = typer.Option(False, "--force", help="Force clearing without confirmation"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
):
    """Clear the Redis recommendation cache."""
    ***REMOVED*** Configure logging for this command
    log_level = "WARNING" if not verbose else "INFO"
    if quiet:
        log_level = "ERROR"

    configure_logging(log_level=log_level, verbose=verbose)

    ***REMOVED*** Suppress noisy logs
    if not verbose:
        noisy_loggers = [
            "httpx",
            "qdrant_client",
            "sentence_transformers",
            "recommendation_api.repositories.redis.repository",
            "recommendation_api.services.cache_service",
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)

    ***REMOVED*** Validate Redis connection
    if not quiet:
        console.print("[cyan]Checking Redis connection...[/cyan]")

    redis_repo = get_redis_repository()
    if not redis_repo.ping():
        console.print("[bold red]Error:[/bold red] Could not connect to Redis")
        raise typer.Exit(code=1)

    ***REMOVED*** Confirm clearing unless force flag is set
    if not force and not quiet:
        confirm = typer.confirm("Are you sure you want to clear the recommendation cache?")
        if not confirm:
            console.print("Operation cancelled.")
            raise typer.Exit(code=0)

    with get_db_context() as session:
        ***REMOVED*** Initialize cache service
        cache_service = get_cache_service(session)

        ***REMOVED*** Clear cache
        if not quiet:
            with console.status("[bold yellow]Clearing cache...[/bold yellow]", spinner="dots"):
                result = cache_service.clear_similar_movies_cache()
        else:
            result = cache_service.clear_similar_movies_cache()

        if "error" in result:
            console.print(f"[bold red]Error:[/bold red] {result['error']}")
            raise typer.Exit(code=1)

        console.print(
            f"[bold green]✓ Cache cleared![/bold green] Deleted {result['deleted_keys']} keys in {result['elapsed_time']:.2f} seconds"
        )
