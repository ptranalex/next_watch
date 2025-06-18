"""CLI commands for cache metrics."""

import json
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..metrics.collector import get_global_collector

console = Console()
metrics_app = typer.Typer(name="metrics", help="Cache metrics commands")


@metrics_app.command("show")
def show_metrics(
    function_name: Optional[str] = typer.Option(
        None, "--function", "-f", help="Show metrics for specific function"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Show cache performance metrics."""
    collector = get_global_collector()

    if function_name:
        ***REMOVED*** Show metrics for specific function
        func_metrics = collector.get_function_metrics(function_name)
        if not func_metrics:
            console.print(f"[red]No metrics found for function: {function_name}[/red]")
            raise typer.Exit(1)

        if json_output:
            console.print(json.dumps(func_metrics, indent=2))
        else:
            _display_function_metrics(func_metrics)
    else:
        ***REMOVED*** Show overall metrics
        metrics = collector.get_metrics()
        if not metrics:
            console.print("[yellow]No metrics available yet[/yellow]")
            return

        if json_output:
            console.print(json.dumps(metrics, indent=2))
        else:
            _display_overall_metrics(metrics)


@metrics_app.command("summary")
def show_summary() -> None:
    """Show cache metrics summary."""
    collector = get_global_collector()
    summary = collector.get_summary()

    if not summary:
        console.print("[yellow]No metrics available yet[/yellow]")
        return

    _display_summary(summary)


@metrics_app.command("reset")
def reset_metrics(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
) -> None:
    """Reset all cache metrics."""
    if not confirm:
        confirm = typer.confirm("Are you sure you want to reset all metrics?")

    if confirm:
        from ..metrics.storage import reset_global_storage

        reset_global_storage()
        console.print("[green]✓ Cache metrics reset successfully[/green]")
    else:
        console.print("[yellow]Reset cancelled[/yellow]")


def _display_overall_metrics(metrics: Dict[str, Any]) -> None:
    """Display overall metrics in a formatted table."""
    overall = metrics.get("overall", {})
    functions = metrics.get("functions", {})

    ***REMOVED*** Overall summary panel
    summary_text = Text()
    summary_text.append(f"Total Calls: {overall.get('total_calls', 0)}\n", style="bold")
    summary_text.append(f"Cache Hits: {overall.get('total_hits', 0)} ", style="green")
    summary_text.append(f"({overall.get('hit_ratio', 0)}%)\n", style="green")
    summary_text.append(f"Cache Misses: {overall.get('total_misses', 0)} ", style="red")
    summary_text.append(f"({overall.get('miss_ratio', 0)}%)\n", style="red")
    summary_text.append(f"Started: {overall.get('started_at', 'Unknown')}", style="dim")

    console.print(Panel(summary_text, title="📊 Cache Performance Summary", border_style="blue"))

    if not functions:
        console.print("[yellow]No function-specific metrics available[/yellow]")
        return

    ***REMOVED*** Function metrics table
    table = Table(title="Function Performance Metrics")
    table.add_column("Function", style="cyan", no_wrap=True)
    table.add_column("Calls", justify="right")
    table.add_column("Hit Ratio", justify="right")
    table.add_column("Avg Cache Time", justify="right", style="green")
    table.add_column("Avg Uncached Time", justify="right", style="red")
    table.add_column("Performance Gain", justify="right", style="bold")

    for func_name, func_data in functions.items():
        hit_ratio = func_data.get("hit_ratio", 0)
        hit_ratio_style = "green" if hit_ratio > 50 else "yellow" if hit_ratio > 20 else "red"

        performance_gain = func_data.get("performance_improvement", 0)
        gain_style = (
            "green" if performance_gain > 2 else "yellow" if performance_gain > 1.5 else "dim"
        )

        table.add_row(
            func_name.split(".")[-1],  ***REMOVED*** Show only function name, not full module path
            str(func_data.get("total_calls", 0)),
            f"{hit_ratio}%",
            f"{func_data.get('avg_cache_time_ms', 0):.1f}ms",
            f"{func_data.get('avg_uncached_time_ms', 0):.1f}ms",
            f"{performance_gain:.1f}x",
        )

    console.print(table)


def _display_function_metrics(func_metrics: Dict[str, Any]) -> None:
    """Display metrics for a specific function."""
    func_name = func_metrics.get("function_name", "Unknown")

    ***REMOVED*** Function details panel
    details_text = Text()
    details_text.append(f"Function: {func_name}\n", style="bold cyan")
    details_text.append(f"Total Calls: {func_metrics.get('total_calls', 0)}\n")
    details_text.append(f"Cache Hits: {func_metrics.get('hits', 0)} ", style="green")
    details_text.append(f"({func_metrics.get('hit_ratio', 0)}%)\n", style="green")
    details_text.append(f"Cache Misses: {func_metrics.get('misses', 0)} ", style="red")
    details_text.append(f"({func_metrics.get('miss_ratio', 0)}%)\n", style="red")
    details_text.append(
        f"Avg Cache Time: {func_metrics.get('avg_cache_time_ms', 0):.1f}ms\n", style="green"
    )
    details_text.append(
        f"Avg Uncached Time: {func_metrics.get('avg_uncached_time_ms', 0):.1f}ms\n", style="red"
    )
    details_text.append(
        f"Performance Improvement: {func_metrics.get('performance_improvement', 0):.1f}x\n",
        style="bold",
    )

    if func_metrics.get("last_hit"):
        details_text.append(f"Last Hit: {func_metrics.get('last_hit')}\n", style="dim")
    if func_metrics.get("last_miss"):
        details_text.append(f"Last Miss: {func_metrics.get('last_miss')}\n", style="dim")

    details_text.append(f"Created: {func_metrics.get('created_at', 'Unknown')}", style="dim")

    console.print(
        Panel(details_text, title=f"📈 Metrics for {func_name.split('.')[-1]}", border_style="cyan")
    )


def _display_summary(summary: Dict[str, Any]) -> None:
    """Display metrics summary."""
    ***REMOVED*** Create a compact summary display
    table = Table(title="Cache Metrics Summary", show_header=False, box=None)
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Calls", str(summary.get("total_calls", 0)))
    table.add_row(
        "Cache Hits", f"{summary.get('total_hits', 0)} ({summary.get('overall_hit_ratio', 0)}%)"
    )
    table.add_row(
        "Cache Misses",
        f"{summary.get('total_misses', 0)} ({summary.get('overall_miss_ratio', 0)}%)",
    )
    table.add_row("Functions Tracked", str(summary.get("function_count", 0)))
    table.add_row("Started", summary.get("started_at", "Unknown"))

    console.print(Panel(table, title="📊 Cache Summary", border_style="blue"))
