"""CLI commands for managing the recommendation cache."""

import asyncio
import logging
import time
from typing import Any, cast

import typer
from config.logging import configure_logging
from rich.console import Console
from rich.table import Table
from typer import Typer

from recommendation_api.config import settings
from recommendation_api.services.cache_service import get_cache_service

# Create Typer app
app: Typer = typer.Typer(
    name="cache",
    help="Manage the recommendation cache",
    add_completion=False,
)

# Create console for rich output
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
    ttl: int | None = typer.Option(
        None, "--ttl", "-t", help="Cache TTL in seconds (default: from config)"
    ),
    batch_size: int = typer.Option(
        100, "--batch-size", "-b", help="Number of movies to process in each batch"
    ),
    movie_ids: list[int] | None = typer.Option(
        None, "--movie-id", "-m", help="Specific movie IDs to process (comma-separated)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
    force: bool = typer.Option(False, "--force", help="Process movies even if already cached"),
) -> None:
    """Precompute similar movies and store them in the Redis cache.

    This command processes movies in batches, finds similar movies for each one,
    and stores the results in Redis for fast retrieval.
    """
    # Configure logging for this command
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "ERROR"
    else:
        log_level = "WARNING"  # Default to WARNING to reduce noise

    configure_logging(log_level=log_level, verbose=verbose)

    # Suppress noisy logs unless in verbose mode
    noisy_loggers = [
        "httpx",
        "qdrant_client",
        "sentence_transformers",
        "recommendation_api.repositories.vector.repository",
        "recommendation_api.repositories.vector.client",
        "recommendation_api.services.vector_service",
        "recommendation_api.repositories.redis.repository",
        "recommendation_api.services.clients.base",
    ]

    if verbose:
        # In verbose mode, show more details but still suppress the noisiest ones
        for logger_name in ["httpx", "qdrant_client", "sentence_transformers"]:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    else:
        # In normal mode, suppress all noisy loggers
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)

    # Use asyncio to run the async function
    asyncio.run(
        _run_precompute(
            limit=limit,
            min_score=min_score,
            ttl=ttl,
            batch_size=batch_size,
            movie_ids=movie_ids,
            verbose=verbose,
            quiet=quiet,
            force=force,
            noisy_loggers=noisy_loggers,
        )
    )


async def _run_precompute(
    limit: int,
    min_score: float,
    ttl: int | None,
    batch_size: int,
    movie_ids: list[int] | None,
    verbose: bool,
    quiet: bool,
    force: bool,
    noisy_loggers: list[str],
) -> None:
    """Async implementation of precompute command."""
    # Configure logging levels
    temp_loggers = {}
    if not verbose:
        for logger_name in noisy_loggers:
            logger = logging.getLogger(logger_name)
            temp_loggers[logger_name] = logger.level
            logger.setLevel(logging.CRITICAL)

    # Create a custom progress tracking class
    class ProgressTracker:
        def __init__(self, console, quiet=False):
            self.console = console
            self.quiet = quiet
            self.start_time: float | None = None
            self.last_update = 0
            self.total_movies = 0
            self.processed = 0
            self.skipped = 0
            self.failed = 0
            # Track processing times separately
            self.processing_start_time = None
            self.total_processing_time = 0
            self.processing_count = 0

        def start(self, total_movies):
            self.start_time = time.time()
            self.total_movies = total_movies
            if not self.quiet:
                self.console.print(
                    f"[cyan]Starting precomputation for {total_movies} movies...[/cyan]"
                )

        def start_processing(self):
            """Mark the start of actual processing (not skipping)"""
            self.processing_start_time = time.time()

        def end_processing(self):
            """Mark the end of actual processing"""
            if self.processing_start_time:
                self.total_processing_time += time.time() - self.processing_start_time
                self.processing_count += 1
                self.processing_start_time = None

        def update(self, processed, skipped, failed):
            self.processed = processed
            self.skipped = skipped
            self.failed = failed

            if not self.quiet:
                current_time = time.time()
                # Update every 2 seconds or every 5% of progress
                # Also reduce frequency if lots of skipping is happening
                base_interval = 2.0
                progress_interval = self.total_movies * 0.05 / 100

                # If mostly skipping (>80% skips), increase interval to reduce noise
                total_processed = processed + skipped + failed
                if total_processed > 10:  # Only after processing some movies
                    skip_ratio = skipped / total_processed
                    if skip_ratio > 0.8:  # If >80% are skips
                        base_interval = 5.0  # Update every 5 seconds instead

                update_interval = max(base_interval, progress_interval)

                if current_time - self.last_update >= update_interval:
                    self.last_update = current_time

                    total_processed = processed + skipped + failed
                    progress_pct = (
                        (total_processed / self.total_movies * 100) if self.total_movies > 0 else 0
                    )
                    if self.start_time is None:
                        self.start_time = current_time
                    elapsed = current_time - self.start_time

                    # Calculate overall throughput (including skips)
                    overall_rate = total_processed / elapsed if elapsed > 0 else 0

                    # Calculate actual processing rate (excluding skips)
                    processing_rate = 0
                    if self.processing_count > 0 and self.total_processing_time > 0:
                        processing_rate = self.processing_count / self.total_processing_time

                    # Estimate remaining work
                    remaining_total = self.total_movies - total_processed

                    # Estimate how many of the remaining movies actually need processing
                    # based on the current skip ratio
                    if total_processed > 10:  # Only after processing some movies
                        current_skip_ratio = skipped / total_processed
                        # Assume similar skip ratio for remaining movies
                        estimated_remaining_skips = remaining_total * current_skip_ratio
                        estimated_remaining_to_process = remaining_total - estimated_remaining_skips
                    else:
                        # Early in the process, be more conservative
                        estimated_remaining_to_process = (
                            remaining_total * 0.5
                        )  # Assume 50% need processing

                    # Calculate ETA based on processing rate for remaining work
                    eta = 0
                    if processing_rate > 0 and estimated_remaining_to_process > 0:
                        # Time for actual processing
                        processing_time = estimated_remaining_to_process / processing_rate
                        # Time for skips (much faster, assume 50 movies/s for cache checks)
                        estimated_remaining_skips = remaining_total - estimated_remaining_to_process
                        skip_time = estimated_remaining_skips / 50.0  # Fast cache check rate
                        eta = processing_time + skip_time
                    elif overall_rate > 0:
                        # Fallback to overall rate if no processing data yet
                        eta = remaining_total / overall_rate

                    # Format the display message
                    rate_display = f"{overall_rate:.1f} movies/s"
                    if processing_rate > 0:
                        rate_display += f" (processing: {processing_rate:.1f}/s)"

                    eta_display = f"{int(eta // 60)}m{int(eta % 60):02d}s"

                    # Add estimated remaining work info for better context
                    if processing_rate > 0 and total_processed > 10:
                        current_skip_ratio = skipped / total_processed
                        eta_display += f" (~{estimated_remaining_to_process:.0f} to process)"

                        self.console.print(
                            f"[yellow]Progress: {progress_pct:.1f}% "
                            f"({total_processed}/{self.total_movies}) - "
                            f"Processed: {processed}, Skipped: {skipped}, Failed: {failed} - "
                            f"Rate: {rate_display} - "
                            f"ETA: {eta_display}[/yellow]"
                        )

    cache_service = None
    try:
        # Initialize cache service
        if not quiet:
            console.print("[cyan]Initializing cache service...[/cyan]")
        cache_service = cast(Any, get_cache_service())

        # Create progress tracker
        progress_tracker = ProgressTracker(console, quiet)

        # Get the movie IDs to process
        if movie_ids:
            total_movies = len(movie_ids)
            if not quiet:
                console.print(f"[cyan]Processing {total_movies} specific movies[/cyan]")
        else:
            if not quiet:
                console.print("[cyan]Fetching movie list from API...[/cyan]")
            all_movie_ids = await cache_service.get_all_movie_ids_from_api()

            if not all_movie_ids:
                if not quiet:
                    console.print("[red]No movies found from API[/red]")
                raise typer.Exit(code=1)

            movie_ids_list: list[int] = cast(list[int], all_movie_ids)
            total_movies = len(movie_ids_list)
            movie_ids = movie_ids_list

        # Start progress tracking
        progress_tracker.start(total_movies)

        # Process movies with custom progress display
        start_time = time.time()
        processed = 0
        skipped = 0
        failed = 0

        # Process movies in batches
        movie_ids_list2: list[int] = cast(list[int], movie_ids)
        for i in range(0, total_movies, batch_size):
            batch = movie_ids_list2[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_movies - 1) // batch_size + 1

            if not quiet:
                console.print(
                    f"[dim]Processing batch {batch_num}/{total_batches} ({len(batch)} movies)[/dim]"
                )

            # Batch check which movies are already cached (if not forcing)
            cached_status = {}
            if not force:
                cached_status = cache_service.redis_repo.batch_check_cached_movies(batch)

            # Process each movie in the batch
            for movie_id in batch:
                try:
                    # Check if already cached (if not forcing)
                    if not force and cached_status.get(movie_id, False):
                        skipped += 1
                        continue

                    # Start timing actual processing
                    progress_tracker.start_processing()

                    # Get similar movies (this will cache them automatically)
                    (
                        similar_movies,
                        _,
                    ) = await cache_service.recommendation_service.get_similar_movies(
                        movie_id=movie_id,
                        limit=limit,
                        min_score=min_score,
                    )

                    # End timing actual processing
                    progress_tracker.end_processing()

                    if similar_movies:
                        processed += 1
                    else:
                        skipped += 1

                except Exception as e:
                    # End timing if it was started
                    progress_tracker.end_processing()
                    failed += 1
                    if verbose:
                        console.print(f"[red]Failed to process movie {movie_id}: {e}[/red]")

                # Update progress display
                progress_tracker.update(processed, skipped, failed)

        elapsed_time = time.time() - start_time

        # Prepare final results
        results = {
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "total": total_movies,
            "elapsed_time": elapsed_time,
            "movies_per_second": total_movies / elapsed_time if elapsed_time > 0 else 0,
            "processing_rate": (
                progress_tracker.processing_count / progress_tracker.total_processing_time
                if progress_tracker.total_processing_time > 0
                else 0
            ),
        }

        # Print results
        if not quiet:
            console.print("\n[bold green]✓ Precomputation completed![/bold green]")

            # Create a table for results
            table = Table(title="Precomputation Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total Movies", str(results["total"]))
            table.add_row("Processed", str(results["processed"]))
            table.add_row("Skipped", str(results["skipped"]))
            table.add_row("Failed", str(results["failed"]))
            table.add_row("Elapsed Time", f"{results['elapsed_time']:.2f} seconds")
            table.add_row("Overall Throughput", f"{results['movies_per_second']:.2f} movies/second")
            if results["processing_rate"] > 0:
                table.add_row("Processing Rate", f"{results['processing_rate']:.2f} movies/second")
                table.add_row(
                    "Processing Time", f"{progress_tracker.total_processing_time:.2f} seconds"
                )

            console.print(table)

            # Add completion message based on results
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

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1) from e

    finally:
        # Restore log levels
        if not verbose:
            for logger_name, level in temp_loggers.items():
                logging.getLogger(logger_name).setLevel(level)

        # Clean up cache service
        if cache_service:
            await cache_service.close()


@app.command("info")
def get_cache_info(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Get information about the recommendation cache."""
    # Configure logging for this command
    log_level = "WARNING" if not verbose else "INFO"
    if quiet:
        log_level = "ERROR"

    configure_logging(log_level=log_level, verbose=verbose)

    # Suppress noisy logs
    if not verbose:
        noisy_loggers = [
            "httpx",
            "qdrant_client",
            "sentence_transformers",
            "recommendation_api.repositories.redis.repository",
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)

    # Use asyncio to run the async function
    asyncio.run(_run_cache_info(verbose=verbose, quiet=quiet))


async def _run_cache_info(verbose: bool, quiet: bool) -> None:
    """Async implementation of cache info command."""
    cache_service = None
    try:
        # Initialize cache service
        if not quiet:
            console.print("[cyan]Getting cache information...[/cyan]")

        cache_service = cast(Any, get_cache_service())

        # Get cache stats
        if not quiet:
            with console.status(
                "[bold green]Retrieving cache statistics...[/bold green]", spinner="dots"
            ):
                stats = cache_service.get_cache_stats()
        else:
            stats = cache_service.get_cache_stats()

        if "error" in stats:
            console.print(f"[bold red]Error:[/bold red] {stats['error']}")
            raise typer.Exit(code=1)

        # Create a table for basic stats
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
        table.add_row("TTL", f"{settings.cache_ttl_default} seconds")
        table.add_row("Caching Enabled", "Yes" if settings.enable_caching else "No")

        console.print(table)

        # Show more detailed information if verbose
        if verbose and redis_info.get("similar_movies_sample"):
            console.print("\n[bold]Sample of cached similar movies:[/bold]")
            for key in redis_info["similar_movies_sample"]:
                console.print(f"  • {key}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1) from e

    finally:
        # Clean up cache service
        if cache_service:
            await cache_service.close()


@app.command("clear")
def clear_cache(
    force: bool = typer.Option(False, "--force", help="Force clearing without confirmation"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Clear the Redis recommendation cache."""
    # Configure logging for this command
    log_level = "WARNING" if not verbose else "INFO"
    if quiet:
        log_level = "ERROR"

    configure_logging(log_level=log_level, verbose=verbose)

    # Suppress noisy logs
    if not verbose:
        noisy_loggers = [
            "httpx",
            "qdrant_client",
            "sentence_transformers",
            "recommendation_api.repositories.redis.repository",
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)

    # Confirm clearing unless force flag is set
    if not force and not quiet:
        confirm = typer.confirm("Are you sure you want to clear the recommendation cache?")
        if not confirm:
            console.print("Operation cancelled.")
            raise typer.Exit(code=0)

    # Use asyncio to run the async function
    asyncio.run(_run_clear_cache(verbose=verbose, quiet=quiet))


async def _run_clear_cache(verbose: bool, quiet: bool) -> None:
    """Async implementation of clear cache command."""
    cache_service = None
    try:
        # Initialize cache service
        if not quiet:
            console.print("[cyan]Initializing cache service...[/cyan]")

        cache_service = cast(Any, get_cache_service())

        # Clear cache
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

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1) from e

    finally:
        # Clean up cache service
        if cache_service:
            await cache_service.close()
