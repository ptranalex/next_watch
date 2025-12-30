"""CLI commands for cache warming operations."""

import asyncio
from typing import Any

import structlog
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cache import CacheManager, get_global_collector
from cache.warming import (
    WarmingConfig,
    WarmingEngine,
    WarmingStats,
    WarmingStrategy,
    get_global_warming_engine,
)

logger = structlog.get_logger(__name__)

console = Console()
warming_app = typer.Typer(help="Cache warming commands")


@warming_app.command("start")
def start_warming(
    strategy: str | None = typer.Option(
        "all",
        help="Warming strategy (metrics_driven, popular_content, user_specific, scheduled, all)",
    ),
    limit: int = typer.Option(50, help="Maximum number of targets to warm"),
    dry_run: bool = typer.Option(False, help="Show what would be warmed without executing"),
    user_ids: str | None = typer.Option(
        None, help="Comma-separated user IDs for user-specific warming"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Start cache warming process."""

    async def _start_warming() -> None:
        try:
            # Configure logging if verbose mode is enabled
            if verbose:
                logger.info("Verbose logging enabled")

            # Use global warming engine if available, otherwise create default
            engine = get_global_warming_engine()
            if engine is None:
                # Initialize default warming engine
                cache_manager = CacheManager.from_settings()
                metrics_collector = get_global_collector()
                config = WarmingConfig()

                engine = WarmingEngine(
                    cache_manager=cache_manager,
                    metrics_collector=metrics_collector,
                    config=config,
                )

            # Prepare context
            context = {}
            if user_ids:
                context["user_ids"] = [int(uid.strip()) for uid in user_ids.split(",")]

            console.print(f"[green]Starting {strategy} warming with limit {limit}[/green]")
            if dry_run:
                console.print("[yellow]Dry run mode - no actual warming will be performed[/yellow]")

            # Execute warming based on strategy
            if strategy == "all":
                results = await engine.warm_all_strategies(
                    limit_per_strategy=limit, dry_run=dry_run, context=context
                )
                _display_all_strategy_results(results, dry_run)
            else:
                # Map string to enum
                strategy_map = {
                    "metrics_driven": WarmingStrategy.METRICS_DRIVEN,
                    "popular_content": WarmingStrategy.POPULAR_CONTENT,
                    "user_specific": WarmingStrategy.USER_SPECIFIC,
                    "scheduled": WarmingStrategy.SCHEDULED,
                }

                if strategy not in strategy_map:
                    console.print(f"[red]Unknown strategy: {strategy}[/red]")
                    console.print(f"Available strategies: {', '.join(strategy_map.keys())}")
                    return

                warming_strategy = strategy_map[strategy]
                stats = await engine.warm_by_strategy(
                    strategy=warming_strategy,
                    limit=limit,
                    dry_run=dry_run,
                    context=context,
                )
                _display_warming_stats(stats, dry_run)

        except Exception as e:
            console.print(f"[red]Error during warming: {e}[/red]")

    asyncio.run(_start_warming())


@warming_app.command("status")
def warming_status() -> None:
    """Show current warming status."""

    async def _show_status() -> None:
        try:
            # Use global warming engine if available, otherwise create default
            engine = get_global_warming_engine()
            config = None

            if engine is None:
                # Initialize default warming engine
                cache_manager = CacheManager.from_settings()
                metrics_collector = get_global_collector()
                config = WarmingConfig()

                engine = WarmingEngine(
                    cache_manager=cache_manager,
                    metrics_collector=metrics_collector,
                    config=config,
                )
            else:
                # Use config from global engine
                config = engine.config

            # Get available strategies
            available_strategies = engine.get_available_strategies()

            # Status table
            status_table = Table(title="🔥 Warming System Status")
            status_table.add_column("Strategy", style="cyan")
            status_table.add_column("Status", style="green")
            status_table.add_column("Description", style="white")

            for strategy in WarmingStrategy:
                if strategy in available_strategies:
                    info = engine.get_strategy_info(strategy)
                    status = "[green]Enabled[/green]"
                    description = (
                        info.get("description", "No description") if info else "No description"
                    )
                else:
                    status = "[red]Disabled[/red]"
                    description = "Strategy not enabled in configuration"

                status_table.add_row(
                    strategy.value.replace("_", " ").title(),
                    status,
                    description[:60] + "..." if len(description) > 60 else description,
                )

            console.print(status_table)

            # Configuration summary
            config_panel = Panel(
                f"Max Concurrent: {config.max_concurrent_operations}\n"
                f"Max Items Per Strategy: {config.max_items_per_strategy}\n"
                f"Operation Timeout: {config.operation_timeout_seconds}s\n"
                f"Automatic Warming: {'Enabled' if config.enable_automatic_warming else 'Disabled'}",
                title="Configuration",
                border_style="blue",
            )
            console.print(config_panel)

        except Exception as e:
            console.print(f"[red]Error getting warming status: {e}[/red]")

    asyncio.run(_show_status())


@warming_app.command("config")
def show_config() -> None:
    """Show warming configuration."""
    # Use global warming engine config if available, otherwise default
    engine = get_global_warming_engine()
    config = engine.config if engine else WarmingConfig()

    # General configuration
    general_table = Table(title="🔥 General Configuration")
    general_table.add_column("Setting", style="cyan")
    general_table.add_column("Value", style="green")

    general_table.add_row("Max Concurrent Operations", str(config.max_concurrent_operations))
    general_table.add_row("Max Items Per Strategy", str(config.max_items_per_strategy))
    general_table.add_row("Operation Timeout", f"{config.operation_timeout_seconds}s")
    general_table.add_row("Max Duration", f"{config.max_warming_duration_minutes}min")
    general_table.add_row(
        "Automatic Warming",
        "Enabled" if config.enable_automatic_warming else "Disabled",
    )

    console.print(general_table)

    # Strategy configuration
    strategy_table = Table(title="🔧 Strategy Configuration")
    strategy_table.add_column("Strategy", style="cyan")
    strategy_table.add_column("Enabled", style="green")
    strategy_table.add_column("Weight", style="yellow")

    strategies = [
        ("Metrics Driven", config.enable_metrics_driven, config.metrics_driven_weight),
        (
            "Popular Content",
            config.enable_popular_content,
            config.popular_content_weight,
        ),
        ("User Specific", config.enable_user_specific, config.user_specific_weight),
        ("Scheduled", config.enable_scheduled, config.scheduled_weight),
    ]

    for name, enabled, weight in strategies:
        strategy_table.add_row(
            name, "[green]Yes[/green]" if enabled else "[red]No[/red]", f"{weight:.1f}"
        )

    console.print(strategy_table)

    # Thresholds configuration
    threshold_table = Table(title="📊 Threshold Configuration")
    threshold_table.add_column("Threshold", style="cyan")
    threshold_table.add_column("Value", style="green")

    threshold_table.add_row("Min Miss Rate", f"{config.min_miss_rate_threshold:.1%}")
    threshold_table.add_row("Min Avg Miss Time", f"{config.min_avg_miss_time_ms:.1f}ms")
    threshold_table.add_row("Min Total Calls", str(config.min_total_calls))
    threshold_table.add_row("Popular Content Refresh", f"{config.popular_content_refresh_hours}h")
    threshold_table.add_row("Max Users Per Batch", str(config.max_users_per_batch))
    threshold_table.add_row(
        "Recommendation Confidence", f"{config.recommendation_confidence_threshold:.1%}"
    )

    console.print(threshold_table)


@warming_app.command("candidates")
def show_candidates(
    limit: int = typer.Option(20, help="Maximum number of candidates to show"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed metrics"),
) -> None:
    """Show warming candidates based on current metrics."""

    async def _show_candidates() -> None:
        try:
            # For now, just show placeholder
            console.print("[yellow]Warming candidates feature coming soon[/yellow]")
        except Exception as e:
            console.print(f"[red]Error getting warming candidates: {e}[/red]")

    asyncio.run(_show_candidates())


def _display_warming_stats(stats: WarmingStats, dry_run: bool = False) -> None:
    """Display warming statistics in a formatted table."""

    title = "🔥 Warming Results (Dry Run)" if dry_run else "🔥 Warming Results"

    stats_table = Table(title=title)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")

    stats_table.add_row("Total Targets", str(stats.total_targets))
    stats_table.add_row("Successful", str(stats.successful_targets))
    stats_table.add_row("Failed", str(stats.failed_targets))
    stats_table.add_row("Success Rate", f"{stats.success_rate:.1%}")

    if stats.total_execution_time_ms > 0:
        stats_table.add_row("Total Time", f"{stats.total_execution_time_ms:.1f}ms")
        stats_table.add_row("Average Time", f"{stats.average_execution_time_ms:.1f}ms")

    console.print(stats_table)

    # Show status message
    if stats.total_targets == 0:
        console.print("[yellow]No warming targets identified[/yellow]")
    elif stats.success_rate == 1.0:
        console.print("[green]✅ All warming operations completed successfully![/green]")
    elif stats.success_rate > 0.8:
        console.print("[yellow]⚠️  Most warming operations completed successfully[/yellow]")
    else:
        console.print("[red]❌ Many warming operations failed[/red]")


def _display_all_strategy_results(
    results: dict[WarmingStrategy, WarmingStats], dry_run: bool = False
) -> None:
    """Display results from all warming strategies."""

    title = "🔥 All Strategies Results (Dry Run)" if dry_run else "🔥 All Strategies Results"

    # Summary table
    summary_table = Table(title=title)
    summary_table.add_column("Strategy", style="cyan")
    summary_table.add_column("Targets", style="green")
    summary_table.add_column("Successful", style="green")
    summary_table.add_column("Failed", style="red")
    summary_table.add_column("Success Rate", style="yellow")
    summary_table.add_column("Total Time", style="blue")

    total_targets = 0
    total_successful = 0
    total_failed = 0
    total_time = 0.0

    for strategy, stats in results.items():
        total_targets += stats.total_targets
        total_successful += stats.successful_targets
        total_failed += stats.failed_targets
        total_time += stats.total_execution_time_ms

        summary_table.add_row(
            strategy.value.replace("_", " ").title(),
            str(stats.total_targets),
            str(stats.successful_targets),
            str(stats.failed_targets),
            f"{stats.success_rate:.1%}",
            (
                f"{stats.total_execution_time_ms:.1f}ms"
                if stats.total_execution_time_ms > 0
                else "N/A"
            ),
        )

    # Add totals row
    overall_success_rate = total_successful / total_targets if total_targets > 0 else 0.0
    summary_table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_targets}[/bold]",
        f"[bold]{total_successful}[/bold]",
        f"[bold]{total_failed}[/bold]",
        f"[bold]{overall_success_rate:.1%}[/bold]",
        f"[bold]{total_time:.1f}ms[/bold]" if total_time > 0 else "[bold]N/A[/bold]",
    )

    console.print(summary_table)

    # Overall status message
    if total_targets == 0:
        console.print("[yellow]No warming targets identified across all strategies[/yellow]")
    elif overall_success_rate == 1.0:
        console.print(
            "[green]✅ All warming operations completed successfully across all strategies![/green]"
        )
    elif overall_success_rate > 0.8:
        console.print("[yellow]⚠️  Most warming operations completed successfully[/yellow]")
    else:
        console.print("[red]❌ Many warming operations failed[/red]")


def _show_warming_candidates(
    all_metrics: dict[str, Any],
    config: WarmingConfig,
    limit: int = 20,
    verbose: bool = False,
) -> None:
    """Show warming candidates based on metrics."""
    console.print(f"[blue]Would show {limit} warming candidates[/blue]")
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
