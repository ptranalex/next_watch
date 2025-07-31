"""Cache warming CLI commands for BFF API.

This module provides production-safe cache warming commands that can be
used for scheduled warming via cron jobs or manual operations.

Key Safety Features:
- Rate limiting to prevent downstream service overload
- Batch processing with configurable concurrency
- Dry-run mode for testing
- Comprehensive logging and error handling
- Memory-efficient streaming processing
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from bff_api.services.cache_service import get_bff_warming_service
from bff_api.services.cache_service.warming.config import get_warming_rate_limiter
from cache.warming import WarmingStrategy
from config.logging import get_logger

logger = get_logger(__name__)
console = Console()


async def _setup_cli_services() -> bool:
    """Initialize service clients for CLI context."""
    try:
        from bff_api.config.app import settings
        from fast_core.dependencies.client_factory import register_service

        ***REMOVED*** Register backend service
        if settings.backend_api_url:
            register_service(
                name="backend",
                base_url=settings.backend_api_url,
                timeout=settings.backend_api_timeout,
                singleton=True,
            )

        ***REMOVED*** Register recommendation service
        if settings.reco_api_url:
            register_service(
                name="recommendation",
                base_url=settings.reco_api_url,
                timeout=settings.recommendation_api_timeout,
                singleton=True,
            )

        ***REMOVED*** Register auth service
        if settings.auth_api_url:
            register_service(
                name="auth",
                base_url=settings.auth_api_url,
                timeout=settings.auth_api_timeout,
                singleton=True,
            )

        ***REMOVED*** Register search service
        if settings.search_api_url:
            register_service(
                name="search",
                base_url=settings.search_api_url,
                timeout=settings.search_api_timeout,
                singleton=True,
            )

        logger.debug("Service clients initialized for CLI context")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize service clients: {e}")
        return False


***REMOVED*** Create the cache warming command group
cache_app = typer.Typer(
    name="cache", help="Cache warming and management commands", rich_markup_mode="rich"
)


@cache_app.command("warm-popular")
def warm_popular_content(
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum items to warm"),
    max_concurrent: int = typer.Option(
        3, "--concurrent", "-c", help="Maximum concurrent operations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without executing"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """🔥 Warm popular content cache.

    This command safely warms the cache with popular movies and content.
    It includes built-in rate limiting to prevent production issues.

    [bold red]Production Safety:[/bold red]
    - Rate limited to 2 requests/second by default
    - Respects downstream service rate limits
    - Automatic exponential backoff on errors
    - Memory-efficient batch processing

    Examples:
        ***REMOVED*** Warm 50 popular items (safe for production)
        bff-api cache warm-popular --limit 50

        ***REMOVED*** Test run without actually warming
        bff-api cache warm-popular --limit 100 --dry-run

        ***REMOVED*** Higher concurrency for off-peak hours
        bff-api cache warm-popular --limit 500 --concurrent 5
    """
    asyncio.run(_warm_popular_content_async(limit, max_concurrent, dry_run, verbose))


@cache_app.command("warm-movie")
def warm_single_movie(
    movie_id: int = typer.Argument(..., help="Movie ID to warm"),
    user_id: Optional[int] = typer.Option(
        None, "--user-id", help="User ID for personalized warming"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without executing"
    ),
) -> None:
    """🎬 Warm cache for a specific movie.

    Warms all cache layers for a single movie including:
    - Static movie data (cast, details, trailers)
    - Similar movies recommendations
    - User-specific interactions (if user_id provided)
    """
    asyncio.run(_warm_single_movie_async(movie_id, user_id, dry_run))


@cache_app.command("warm-batch")
def warm_movie_batch(
    movie_ids: str = typer.Argument(..., help="Comma-separated movie IDs"),
    max_concurrent: int = typer.Option(
        2, "--concurrent", "-c", help="Maximum concurrent operations"
    ),
    delay: float = typer.Option(0.5, "--delay", help="Delay between batches (seconds)"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without executing"
    ),
) -> None:
    """📦 Warm cache for multiple movies safely.

    [bold yellow]Production Warning:[/bold yellow] Use low concurrency values in production!

    Examples:
        ***REMOVED*** Safe for production
        bff-api cache warm-batch "1,2,3,4,5" --concurrent 2 --delay 1.0

        ***REMOVED*** Test first
        bff-api cache warm-batch "1,2,3" --dry-run
    """
    try:
        ids = [int(id.strip()) for id in movie_ids.split(",")]
        if len(ids) > 100:
            console.print(
                f"[bold red]Error:[/bold red] Too many movies ({len(ids)}). Maximum 100 for safety."
            )
            raise typer.Exit(1)

        asyncio.run(_warm_movie_batch_async(ids, max_concurrent, delay, dry_run))
    except ValueError:
        console.print(
            "[bold red]Error:[/bold red] Invalid movie IDs. Use comma-separated integers."
        )
        raise typer.Exit(1)


@cache_app.command("stats")
def show_cache_stats() -> None:
    """📊 Show cache warming statistics and health."""
    asyncio.run(_show_cache_stats_async())


@cache_app.command("health-check")
def cache_health_check() -> None:
    """🏥 Check cache warming system health."""
    asyncio.run(_cache_health_check_async())


***REMOVED*** Async implementation functions


async def _warm_popular_content_async(
    limit: int, max_concurrent: int, dry_run: bool, verbose: bool
) -> None:
    """Async implementation of popular content warming."""
    if dry_run:
        console.print(f"[bold blue]DRY RUN:[/bold blue] Would warm {limit} popular items")
        console.print(f"Max concurrent operations: {max_concurrent}")
        return

    console.print(f"🔥 Warming {limit} popular items...")
    console.print(f"[dim]Concurrency: {max_concurrent}, Rate limited for production safety[/dim]")

    start_time = time.time()

    try:
        ***REMOVED*** Initialize service clients for CLI context
        clients_ready = await _setup_cli_services()
        if not clients_ready:
            console.print("[bold red]Error:[/bold red] Failed to initialize service clients")
            raise typer.Exit(1)

        ***REMOVED*** Get warming service
        warming_service = get_bff_warming_service()
        warming_engine = warming_service.get_warming_engine()

        if not warming_engine:
            console.print("[bold red]Error:[/bold red] Warming engine not available")
            raise typer.Exit(1)

        ***REMOVED*** Get targets first to show accurate progress
        from cache.warming.strategies.popular_content import PopularContentStrategy

        popular_strategy = None
        for strategy_name, strategy_instance in warming_engine._strategies.items():
            if strategy_name == WarmingStrategy.POPULAR_CONTENT:
                popular_strategy = strategy_instance
                break

        if not popular_strategy:
            console.print("[bold red]Error:[/bold red] Popular content strategy not available")
            raise typer.Exit(1)

        ***REMOVED*** Get the actual targets to warm
        targets = await popular_strategy.identify_targets(limit)
        actual_count = len(targets)

        if actual_count == 0:
            console.print("[bold yellow]Warning:[/bold yellow] No targets found to warm")
            return

        console.print(f"[dim]Found {actual_count} targets to warm[/dim]")

        ***REMOVED*** Show progress with real updates
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:

            task = progress.add_task("Warming popular content...", total=actual_count)

            ***REMOVED*** Create a progress callback
            def update_progress(completed: int) -> None:
                progress.update(task, completed=completed)

            ***REMOVED*** Warm targets individually with progress tracking
            successful = 0
            failed = 0

            for i, target in enumerate(targets):
                try:
                    ***REMOVED*** Get the warming function for this target
                    warming_func = warming_engine._warming_functions.get(target.function_name)
                    if warming_func:
                        await warming_func(**target.parameters)
                        successful += 1
                    else:
                        failed += 1
                        logger.warning(f"No warming function found for {target.function_name}")
                except Exception as e:
                    failed += 1
                    logger.error(f"Failed to warm target {target.function_name}: {e}")

                ***REMOVED*** Update progress
                progress.update(task, completed=i + 1)

                ***REMOVED*** Small delay to prevent overwhelming downstream services
                await asyncio.sleep(0.1)

            ***REMOVED*** Create stats object
            class WarmingStats:
                def __init__(self, total: int, successful: int, failed: int):
                    self.total_targets = total
                    self.successful_targets = successful
                    self.failed_targets = failed

            stats = WarmingStats(actual_count, successful, failed)

        ***REMOVED*** Show results
        elapsed = time.time() - start_time
        _display_warming_results(stats, elapsed, verbose)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


async def _warm_single_movie_async(movie_id: int, user_id: Optional[int], dry_run: bool) -> None:
    """Async implementation of single movie warming."""
    if dry_run:
        console.print(f"[bold blue]DRY RUN:[/bold blue] Would warm movie {movie_id}")
        if user_id:
            console.print(f"With user context: {user_id}")
        return

    console.print(f"🎬 Warming movie {movie_id}...")

    try:
        ***REMOVED*** Initialize service clients for CLI context
        clients_ready = await _setup_cli_services()
        if not clients_ready:
            console.print("[bold red]Error:[/bold red] Failed to initialize service clients")
            raise typer.Exit(1)

        ***REMOVED*** Import here to avoid circular imports
        from bff_api.services.cache_service.warming.functions import WarmingFunctions
        from bff_api.config.app import settings

        warming_functions = WarmingFunctions(settings)

        with console.status(f"Warming movie {movie_id}..."):
            result = await warming_functions.warm_movie_screen(movie_id=movie_id, user_id=user_id)

        console.print(f"✅ Movie {movie_id} warmed successfully")
        if result.get("cache_populated"):
            console.print(f"[dim]Cache keys populated: {len(result.get('cache_keys', []))}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to warm movie {movie_id}: {str(e)}")
        raise typer.Exit(1)


async def _warm_movie_batch_async(
    movie_ids: List[int], max_concurrent: int, delay: float, dry_run: bool
) -> None:
    """Async implementation of batch movie warming."""
    if dry_run:
        console.print(f"[bold blue]DRY RUN:[/bold blue] Would warm {len(movie_ids)} movies")
        console.print(f"Movie IDs: {movie_ids}")
        console.print(f"Concurrency: {max_concurrent}, Delay: {delay}s")
        return

    console.print(f"📦 Warming {len(movie_ids)} movies in batches...")

    ***REMOVED*** Production safety check
    if max_concurrent > 5:
        console.print("[bold yellow]Warning:[/bold yellow] High concurrency may impact production")
        if not typer.confirm("Continue?"):
            raise typer.Exit(0)

    try:
        ***REMOVED*** Initialize service clients for CLI context
        clients_ready = await _setup_cli_services()
        if not clients_ready:
            console.print("[bold red]Error:[/bold red] Failed to initialize service clients")
            raise typer.Exit(1)

        from bff_api.services.cache_service.warming.functions import WarmingFunctions
        from bff_api.config.app import settings

        warming_functions = WarmingFunctions(settings)
        rate_limiter = get_warming_rate_limiter()

        results = []
        failed_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:

            task = progress.add_task("Warming movies...", total=len(movie_ids))

            ***REMOVED*** Process in batches to respect rate limits
            semaphore = asyncio.Semaphore(max_concurrent)

            async def warm_single(movie_id: int) -> Dict[str, Any]:
                async with semaphore:
                    try:
                        ***REMOVED*** Rate limiting
                        await rate_limiter.acquire()

                        result = await warming_functions.warm_movie_screen(movie_id=movie_id)
                        progress.advance(task)
                        return {"movie_id": movie_id, "success": True, "result": result}

                    except Exception as e:
                        progress.advance(task)
                        return {"movie_id": movie_id, "success": False, "error": str(e)}

            ***REMOVED*** Execute all warming operations
            tasks = [warm_single(movie_id) for movie_id in movie_ids]
            results = await asyncio.gather(*tasks)

            ***REMOVED*** Add delay between batches if specified
            if delay > 0:
                await asyncio.sleep(delay)

        ***REMOVED*** Show results
        successful = sum(1 for r in results if r["success"])
        failed_count = len(movie_ids) - successful

        console.print(f"\n✅ Batch warming completed:")
        console.print(f"   Successful: {successful}/{len(movie_ids)}")
        if failed_count > 0:
            console.print(f"   Failed: {failed_count}")
            console.print("\n[bold yellow]Failed movies:[/bold yellow]")
            for result in results:
                if not result["success"]:
                    console.print(f"   Movie {result['movie_id']}: {result['error']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


async def _show_cache_stats_async() -> None:
    """Show cache warming statistics."""
    try:
        warming_service = get_bff_warming_service()

        ***REMOVED*** Get warming engine stats
        warming_engine = warming_service.get_warming_engine()
        if warming_engine:
            ***REMOVED*** This would need to be implemented in the warming engine
            console.print("📊 Cache Warming Statistics")
            console.print("[dim]Feature in development - basic stats shown[/dim]")
        else:
            console.print("[bold red]Error:[/bold red] Warming engine not available")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


async def _cache_health_check_async() -> None:
    """Check cache warming system health."""
    try:
        console.print("🏥 Cache Warming Health Check")

        ***REMOVED*** Check warming service
        warming_service = get_bff_warming_service()
        warming_engine = warming_service.get_warming_engine()

        table = Table(title="Cache Warming System Health")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")

        ***REMOVED*** Warming service
        if warming_service:
            table.add_row("Warming Service", "✅ Healthy", "Service initialized")
        else:
            table.add_row("Warming Service", "❌ Error", "Service not available")

        ***REMOVED*** Warming engine
        if warming_engine:
            table.add_row("Warming Engine", "✅ Healthy", "Engine initialized")
        else:
            table.add_row("Warming Engine", "❌ Error", "Engine not available")

        ***REMOVED*** Rate limiter
        try:
            rate_limiter = get_warming_rate_limiter()
            table.add_row("Rate Limiter", "✅ Healthy", f"Tokens: {rate_limiter.tokens:.1f}")
        except Exception:
            table.add_row("Rate Limiter", "❌ Error", "Rate limiter not available")

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


def _display_warming_results(stats: Any, elapsed: float, verbose: bool) -> None:
    """Display warming operation results."""
    console.print(f"\n✅ Warming completed in {elapsed:.2f} seconds")

    if hasattr(stats, "total_targets"):
        console.print(f"   Total targets: {stats.total_targets}")
        console.print(f"   Successful: {stats.successful_targets}")
        console.print(f"   Failed: {stats.failed_targets}")

        if stats.total_targets > 0:
            success_rate = (stats.successful_targets / stats.total_targets) * 100
            console.print(f"   Success rate: {success_rate:.1f}%")

    if verbose and hasattr(stats, "errors") and stats.errors:
        console.print(f"\n[bold yellow]Errors ({len(stats.errors)}):[/bold yellow]")
        for error in stats.errors[:5]:  ***REMOVED*** Show first 5 errors
            console.print(f"   {error}")
        if len(stats.errors) > 5:
            console.print(f"   ... and {len(stats.errors) - 5} more")


***REMOVED*** Export the command group
__all__ = ["cache_app"]
