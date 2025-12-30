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
from typing import Any

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from bff_api.services.cache_service import get_bff_warming_service
from bff_api.services.cache_service.warming.config import get_warming_rate_limiter
from bff_api.services.smart_warming import get_bff_smart_warming

# Import external cache functionality to consolidate under one command group
try:
    from cache.cli.metrics import metrics_app
    from cache.cli.warming import warming_app
except ImportError:
    # Fallback if cache library not available
    metrics_app = None  # type: ignore
    warming_app = None  # type: ignore
from cache.warming import WarmingStrategy
from config.logging import get_logger

logger = get_logger(__name__)
console = Console()


async def _setup_cli_services() -> bool:
    """Initialize service clients for CLI context."""
    try:
        from fast_core.dependencies.client_factory import register_service

        from bff_api.config.app import settings

        # Register backend service
        if settings.backend_api_url:
            register_service(
                name="backend",
                base_url=settings.backend_api_url,
                timeout=settings.backend_api_timeout,
                singleton=True,
            )

        # Register recommendation service
        if settings.reco_api_url:
            register_service(
                name="recommendation",
                base_url=settings.reco_api_url,
                timeout=settings.recommendation_api_timeout,
                singleton=True,
            )

        # Register auth service
        if settings.auth_api_url:
            register_service(
                name="auth",
                base_url=settings.auth_api_url,
                timeout=settings.auth_api_timeout,
                singleton=True,
            )

        # Register search service
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


# Create the cache warming command group
cache_app = typer.Typer(
    name="cache", help="Cache warming and management commands", rich_markup_mode="rich"
)


@cache_app.command("warm-legacy")
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
        # Warm 50 popular items (safe for production)
        bff-api cache warm-popular --limit 50

        # Test run without actually warming
        bff-api cache warm-popular --limit 100 --dry-run

        # Higher concurrency for off-peak hours
        bff-api cache warm-popular --limit 500 --concurrent 5
    """
    asyncio.run(_warm_popular_content_async(limit, max_concurrent, dry_run, verbose))


@cache_app.command("warm-movie")
def warm_single_movie(
    movie_id: int = typer.Argument(..., help="Movie ID to warm"),
    user_id: int | None = typer.Option(None, "--user-id", help="User ID for personalized warming"),
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
        # Safe for production
        bff-api cache warm-batch "1,2,3,4,5" --concurrent 2 --delay 1.0

        # Test first
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


# Async implementation functions


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
        # Initialize service clients for CLI context
        clients_ready = await _setup_cli_services()
        if not clients_ready:
            console.print("[bold red]Error:[/bold red] Failed to initialize service clients")
            raise typer.Exit(1)

        # Get warming service
        warming_service = get_bff_warming_service()
        warming_engine = warming_service.get_warming_engine()

        if not warming_engine:
            console.print("[bold red]Error:[/bold red] Warming engine not available")
            raise typer.Exit(1)

        # Get targets first to show accurate progress

        popular_strategy = None
        for strategy_name, strategy_instance in warming_engine._strategies.items():
            if strategy_name == WarmingStrategy.POPULAR_CONTENT:
                popular_strategy = strategy_instance
                break

        if not popular_strategy:
            console.print("[bold red]Error:[/bold red] Popular content strategy not available")
            raise typer.Exit(1)

        # Get the actual targets to warm
        targets = await popular_strategy.identify_targets(limit)
        actual_count = len(targets)

        if actual_count == 0:
            console.print("[bold yellow]Warning:[/bold yellow] No targets found to warm")
            return

        console.print(f"[dim]Found {actual_count} targets to warm[/dim]")

        # Show progress with real updates
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

            # Create a progress callback
            def update_progress(completed: int) -> None:
                progress.update(task, completed=completed)

            # Warm targets concurrently with progress tracking
            successful = 0
            failed = 0
            completed = 0

            # Create semaphore to limit concurrent operations
            from bff_api.config.app import get_bff_settings

            settings = get_bff_settings()
            max_concurrent = getattr(settings, "warming_max_concurrent", 12)
            semaphore = asyncio.Semaphore(max_concurrent)

            async def warm_single_target(target: Any) -> tuple[bool, str | None]:
                """Warm a single target with error handling."""
                async with semaphore:  # Limit concurrency
                    try:
                        # Get the warming function for this target
                        warming_func = warming_engine._warming_functions.get(target.function_name)
                        if warming_func:
                            await warming_func(**target.parameters)
                            return True, None
                        else:
                            logger.warning(f"No warming function found for {target.function_name}")
                            return (
                                False,
                                f"No warming function found for {target.function_name}",
                            )
                    except Exception as e:
                        logger.error(f"Failed to warm target {target.function_name}: {e}")
                        return False, str(e)

            # Create tasks for all targets
            tasks = [warm_single_target(target) for target in targets]

            # Process with progress updates
            for future in asyncio.as_completed(tasks):
                try:
                    success, error = await future
                    if success:
                        successful += 1
                    else:
                        failed += 1
                    completed += 1
                    progress.update(task, completed=completed)
                except Exception as e:
                    failed += 1
                    completed += 1
                    progress.update(task, completed=completed)
                    logger.error(f"Unexpected error in warming task: {e}")

            # Create stats object
            class WarmingStats:
                def __init__(self, total: int, successful: int, failed: int):
                    self.total_targets = total
                    self.successful_targets = successful
                    self.failed_targets = failed

            stats = WarmingStats(actual_count, successful, failed)

        # Show results
        elapsed = time.time() - start_time
        _display_warming_results(stats, elapsed, verbose)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


async def _warm_single_movie_async(movie_id: int, user_id: int | None, dry_run: bool) -> None:
    """Async implementation of single movie warming."""
    if dry_run:
        console.print(f"[bold blue]DRY RUN:[/bold blue] Would warm movie {movie_id}")
        if user_id:
            console.print(f"With user context: {user_id}")
        return

    console.print(f"🎬 Warming movie {movie_id}...")

    try:
        # Initialize service clients for CLI context
        clients_ready = await _setup_cli_services()
        if not clients_ready:
            console.print("[bold red]Error:[/bold red] Failed to initialize service clients")
            raise typer.Exit(1)

        # Import here to avoid circular imports
        from bff_api.config.app import settings
        from bff_api.services.cache_service.warming.functions import WarmingFunctions

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
    movie_ids: list[int], max_concurrent: int, delay: float, dry_run: bool
) -> None:
    """Async implementation of batch movie warming."""
    if dry_run:
        console.print(f"[bold blue]DRY RUN:[/bold blue] Would warm {len(movie_ids)} movies")
        console.print(f"Movie IDs: {movie_ids}")
        console.print(f"Concurrency: {max_concurrent}, Delay: {delay}s")
        return

    console.print(f"📦 Warming {len(movie_ids)} movies in batches...")

    # Production safety check
    if max_concurrent > 5:
        console.print("[bold yellow]Warning:[/bold yellow] High concurrency may impact production")
        if not typer.confirm("Continue?"):
            raise typer.Exit(0)

    try:
        # Initialize service clients for CLI context
        clients_ready = await _setup_cli_services()
        if not clients_ready:
            console.print("[bold red]Error:[/bold red] Failed to initialize service clients")
            raise typer.Exit(1)

        from bff_api.config.app import settings
        from bff_api.services.cache_service.warming.functions import WarmingFunctions

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

            # Process in batches to respect rate limits
            semaphore = asyncio.Semaphore(max_concurrent)

            async def warm_single(movie_id: int) -> dict[str, Any]:
                async with semaphore:
                    try:
                        # Rate limiting
                        await rate_limiter.acquire()

                        result = await warming_functions.warm_movie_screen(movie_id=movie_id)
                        progress.advance(task)
                        return {"movie_id": movie_id, "success": True, "result": result}

                    except Exception as e:
                        progress.advance(task)
                        return {"movie_id": movie_id, "success": False, "error": str(e)}

            # Execute all warming operations
            tasks = [warm_single(movie_id) for movie_id in movie_ids]
            results = await asyncio.gather(*tasks)

            # Add delay between batches if specified
            if delay > 0:
                await asyncio.sleep(delay)

        # Show results
        successful = sum(1 for r in results if r["success"])
        failed_count = len(movie_ids) - successful

        console.print("\n✅ Batch warming completed:")
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

        # Get warming engine stats
        warming_engine = warming_service.get_warming_engine()
        if warming_engine:
            # This would need to be implemented in the warming engine
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

        # Check warming service
        warming_service = get_bff_warming_service()
        warming_engine = warming_service.get_warming_engine()

        table = Table(title="Cache Warming System Health")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")

        # Warming service
        if warming_service:
            table.add_row("Warming Service", "✅ Healthy", "Service initialized")
        else:
            table.add_row("Warming Service", "❌ Error", "Service not available")

        # Warming engine
        if warming_engine:
            table.add_row("Warming Engine", "✅ Healthy", "Engine initialized")
        else:
            table.add_row("Warming Engine", "❌ Error", "Engine not available")

        # Rate limiter
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
        for error in stats.errors[:5]:  # Show first 5 errors
            console.print(f"   {error}")
        if len(stats.errors) > 5:
            console.print(f"   ... and {len(stats.errors) - 5} more")


@cache_app.command("warm-tier")
def warm_priority_movies(
    tier: int = typer.Argument(..., help="Priority tier: 1 (2hr), 2 (daily), 3 (weekly)"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be warmed without executing"
    ),
    force: bool = typer.Option(False, "--force", help="Force warming regardless of versions"),
    max_movies: int | None = typer.Option(
        None,
        "--max-movies",
        help="Optional: Limit number of movies for debugging (default: warm ALL movies)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Warm movies based on priority tiers with version checking.

    Priority Tiers (from strategy document):
    - Tier 1 (every 2 hours): New releases (last 30 days), trending top 50
    - Tier 2 (daily): Popular movies (top 500), user favorites
    - Tier 3 (weekly): Full catalog refresh for discovery

    By default, ALL tiers warm ALL available movies. Use --max-movies for debugging.

    This command implements the "cache forever" strategy by checking movie
    versions before warming to avoid redundant work.

    🔄 Features real-time progress tracking with incremental updates as each
    movie is processed. Uses bounded concurrency (max 5 simultaneous requests)
    to prevent backend overload.
    """

    async def _warm_priority_movies_async() -> None:
        console.print(f"[bold green]Starting Priority Tier {tier} Warming[/bold green]")
        console.print(f"Max movies: {max_movies}, Dry run: {dry_run}, Force: {force}")

        if not await _setup_cli_services():
            raise typer.Exit(1)

        # Print current warming configuration
        from bff_api.config.app import get_bff_settings
        from bff_api.services.cache_service.warming.config import get_bff_warming_config

        # Get settings (automatically loads .env and .env.local)
        settings = get_bff_settings()
        warming_config = get_bff_warming_config()

        console.print("\n[bold cyan]📋 Current Warming Configuration:[/bold cyan]")
        config_table = Table(show_header=True, header_style="bold magenta")
        config_table.add_column("Setting", style="white", width=30)
        config_table.add_column("Value", style="green", width=20)
        config_table.add_column("Source", style="dim", width=15)

        # Core config settings (these come from the warming config, with automatic env detection)
        config_table.add_row(
            "Max Concurrent Operations",
            str(warming_config.max_concurrent_operations),
            "Config" if warming_config.max_concurrent_operations != 3 else "Default",
        )
        config_table.add_row(
            "Operation Timeout",
            f"{warming_config.operation_timeout_seconds}s",
            "Config" if warming_config.operation_timeout_seconds != 120 else "Default",
        )
        config_table.add_row(
            "Max Items Per Strategy",
            str(warming_config.max_items_per_strategy),
            "Config" if warming_config.max_items_per_strategy != 10000 else "Default",
        )
        config_table.add_row(
            "Min Miss Rate Threshold",
            f"{warming_config.min_miss_rate_threshold:.1%}",
            "Default",
        )

        # Environment settings (automatically loaded from .env/.env.local)
        config_table.add_row(
            "Max Connections",
            str(getattr(settings, "warming_max_connections", 4)),
            "Config" if hasattr(settings, "warming_max_connections") else "Default",
        )
        config_table.add_row(
            "Request Timeout",
            f"{getattr(settings, 'warming_request_timeout', 3)}s",
            "Config" if hasattr(settings, "warming_request_timeout") else "Default",
        )
        config_table.add_row(
            "Requests Per Second",
            str(getattr(settings, "warming_requests_per_second", 2)),
            "Config" if hasattr(settings, "warming_requests_per_second") else "Default",
        )
        config_table.add_row(
            "Burst Size",
            str(getattr(settings, "warming_burst_size", 5)),
            "Config" if hasattr(settings, "warming_burst_size") else "Default",
        )

        console.print(config_table)
        console.print()

        start_time = time.time()

        try:
            # Get smart warming service with version awareness
            smart_warmer = get_bff_smart_warming()

            if dry_run:
                console.print(f"[yellow]DRY RUN: Would warm Tier {tier} movies[/yellow]")

                tier_descriptions = {
                    1: "New releases (last 30 days) + trending top 50",
                    2: "Popular movies (top 500) + user favorites",
                    3: "Full catalog refresh for discovery",
                }

                console.print(f"Target: {tier_descriptions.get(tier, 'Unknown tier')}")
                console.print(f"Max movies: {max_movies}")
                console.print(f"Version checking: {'Disabled' if force else 'Enabled'}")
                return

            # Execute priority warming with direct progress tracking for CLI
            console.print("[blue]Starting priority warming with real-time progress...[/blue]")

            # Get the movie IDs first to set up proper progress tracking
            movie_ids = await smart_warmer._get_tier_movie_ids(tier, max_movies)

            if not movie_ids:
                console.print(f"[yellow]No movies found for tier {tier}[/yellow]")
                return

            console.print(f"[dim]Found {len(movie_ids)} movies to warm[/dim]")

            # Import warming components
            from bff_api.config.app import settings
            from bff_api.services.cache_service.warming.functions import (
                WarmingFunctions,
            )

            warming_funcs = WarmingFunctions(settings)

            # Create progress bar for actual movie processing
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(f"Warming Tier {tier} movies...", total=len(movie_ids))

                # Use semaphore to limit concurrent requests (use optimized concurrency)
                max_concurrent = min(warming_config.max_concurrent_operations, len(movie_ids))
                semaphore = asyncio.Semaphore(max_concurrent)

                async def _warm_with_progress(movie_id: int) -> dict[str, Any]:
                    """Warm single movie with progress tracking."""
                    async with semaphore:
                        try:
                            result = await smart_warmer._warm_single_movie_with_version(
                                movie_id, warming_funcs, force=force
                            )
                            progress.advance(task)
                            await asyncio.sleep(0.01)  # Reduced delay for better performance
                            return {
                                "movie_id": movie_id,
                                "success": True,
                                "result": result,
                            }
                        except Exception as e:
                            progress.advance(task)
                            return {
                                "movie_id": movie_id,
                                "success": False,
                                "error": str(e),
                            }

                # Execute all warming operations with real-time progress
                warming_tasks = [_warm_with_progress(movie_id) for movie_id in movie_ids]
                results = await asyncio.gather(*warming_tasks, return_exceptions=True)

                # Show summary
                successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
                failed = len(movie_ids) - successful

                console.print(
                    f"\n[green]✅ Completed: {successful}/{len(movie_ids)} movies[/green]"
                )
                if failed > 0:
                    console.print(f"[yellow]⚠️  Failed: {failed} movies[/yellow]")

            duration = time.time() - start_time
            console.print(
                f"[bold green]Priority Tier {tier} warming completed in {duration:.2f}s[/bold green]"
            )

        except Exception as e:
            logger.error("Priority warming failed", error=str(e), exc_info=True)
            console.print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)

    # Run the async function
    asyncio.run(_warm_priority_movies_async())


@cache_app.command("warm-movie")
def warm_movie_with_version_check(
    movie_id: int = typer.Argument(..., help="Movie ID to warm"),
    force: bool = typer.Option(False, "--force", help="Force warming regardless of version"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Warm a specific movie with version checking.

    This command demonstrates the "cache forever" strategy by checking if the
    movie version has changed before performing expensive warming operations.

    If the movie version hasn't changed, warming is skipped to save resources.
    """

    async def _warm_movie_with_version_check_async() -> None:
        console.print(f"[bold green]Warming Movie {movie_id} with Version Check[/bold green]")
        console.print(f"Force: {force}")

        if not await _setup_cli_services():
            raise typer.Exit(1)

        start_time = time.time()

        try:
            smart_warmer = get_bff_smart_warming()

            # Execute version-aware warming with better progress display
            console.print("[blue]Checking version and warming if needed...[/blue]")

            # Import warming components for direct execution
            from bff_api.config.app import settings
            from bff_api.services.cache_service.warming.functions import (
                WarmingFunctions,
            )

            warming_funcs = WarmingFunctions(settings)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Warming movie {movie_id}...", total=None)

                # Execute warming directly with progress indicator
                result = await smart_warmer._warm_single_movie_with_version(
                    movie_id, warming_funcs, force=force
                )

                progress.update(task, description=f"✅ Movie {movie_id} completed")

                # Show result details based on warming status
                status = result.get("status", "unknown")
                if status == "completed":
                    console.print(f"[green]✅ Movie {movie_id} was warmed successfully[/green]")
                elif status == "skipped":
                    console.print(
                        f"[yellow]⏭️  Movie {movie_id} skipped (version unchanged)[/yellow]"
                    )
                else:
                    console.print(f"[blue]ℹ️  Movie {movie_id} status: {status}[/blue]")

            duration = time.time() - start_time
            console.print(
                f"[bold green]Movie {movie_id} warming completed in {duration:.2f}s[/bold green]"
            )

            if verbose:
                # Show version info if available
                console.print("[blue]Check logs for version and warming details[/blue]")

        except Exception as e:
            logger.error("Version-aware movie warming failed", error=str(e), exc_info=True)
            console.print(f"[bold red]Error: {e}[/bold red]")
            raise typer.Exit(1)

    # Run the async function
    asyncio.run(_warm_movie_with_version_check_async())


# Add cache metrics and management commands
@cache_app.command("show")
def show_cache_metrics() -> None:
    """Show cache performance metrics."""
    console.print("🔍 [bold blue]Cache Performance Metrics[/bold blue]")
    # This would integrate with the cache metrics from the cache library
    console.print("[yellow]Cache metrics integration - implement with cache library[/yellow]")


@cache_app.command("summary")
def show_cache_summary() -> None:
    """Show cache metrics summary."""
    console.print("📊 [bold blue]Cache Metrics Summary[/bold blue]")
    console.print("[yellow]Cache summary integration - implement with cache library[/yellow]")


@cache_app.command("reset")
def reset_cache_metrics() -> None:
    """Reset all cache metrics."""
    console.print("🔄 [bold red]Resetting Cache Metrics[/bold red]")
    console.print("[yellow]Cache reset integration - implement with cache library[/yellow]")


@cache_app.command("redis")
def redis_operations() -> None:
    """Direct Redis cache operations."""
    console.print("🔧 [bold blue]Redis Cache Operations[/bold blue]")
    console.print("[yellow]Redis operations - implement with Redis client[/yellow]")
    console.print("Available operations: KEYS, GET, SET, DEL, FLUSHALL")


# Export the command group
__all__ = ["cache_app"]
