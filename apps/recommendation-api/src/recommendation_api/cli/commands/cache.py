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
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of similar movies per movie"),
    min_score: float = typer.Option(0.01, "--min-score", "-s", help="Minimum similarity score threshold"),
    ttl: Optional[int] = typer.Option(None, "--ttl", "-t", help="Cache TTL in seconds (default: from config)"),
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="Number of movies to process in each batch"),
    movie_ids: Optional[List[int]] = typer.Option(None, "--movie-id", "-m", help="Specific movie IDs to process (comma-separated)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Precompute similar movies and store them in the Redis cache.
    
    This command processes movies in batches, finds similar movies for each one,
    and stores the results in Redis for fast retrieval.
    """
    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)
    
    ***REMOVED*** Validate Redis connection
    redis_repo = get_redis_repository()
    if not redis_repo.ping():
        console.print("[bold red]Error:[/bold red] Could not connect to Redis")
        raise typer.Exit(code=1)
    
    with get_db_context() as session:
        ***REMOVED*** Initialize cache service
        cache_service = get_cache_service(session)
        
        ***REMOVED*** Convert movie_ids to list if provided
        movie_id_list = None
        if movie_ids:
            movie_id_list = [int(movie_id) for movie_id in movie_ids]
            console.print(f"Processing [bold]{len(movie_id_list)}[/bold] specific movies")
        else:
            console.print("Processing [bold]all[/bold] movies from database")
        
        with console.status("[bold green]Precomputing similar movies...[/bold green]", spinner="dots"):
            results = cache_service.precompute_similar_movies(
                movie_ids=movie_id_list,
                limit=limit,
                min_score=min_score,
                ttl=ttl,
                batch_size=batch_size,
            )
        
        ***REMOVED*** Print results
        console.print("\n[bold green]Precomputation completed![/bold green]")
        
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


@app.command("info")
def get_cache_info(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """Get information about the recommendation cache."""
    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)
    
    ***REMOVED*** Validate Redis connection
    redis_repo = get_redis_repository()
    if not redis_repo.ping():
        console.print("[bold red]Error:[/bold red] Could not connect to Redis")
        raise typer.Exit(code=1)
    
    with get_db_context() as session:
        ***REMOVED*** Initialize cache service
        cache_service = get_cache_service(session)
        
        ***REMOVED*** Get cache stats
        with console.status("[bold green]Getting cache information...[/bold green]", spinner="dots"):
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
):
    """Clear the Redis recommendation cache."""
    if not settings.redis_url:
        console.print("[bold red]Error:[/bold red] Redis URL not configured")
        raise typer.Exit(code=1)
    
    ***REMOVED*** Validate Redis connection
    redis_repo = get_redis_repository()
    if not redis_repo.ping():
        console.print("[bold red]Error:[/bold red] Could not connect to Redis")
        raise typer.Exit(code=1)
    
    ***REMOVED*** Confirm clearing unless force flag is set
    if not force:
        confirm = typer.confirm("Are you sure you want to clear the recommendation cache?")
        if not confirm:
            console.print("Operation cancelled.")
            raise typer.Exit(code=0)
    
    with get_db_context() as session:
        ***REMOVED*** Initialize cache service
        cache_service = get_cache_service(session)
        
        ***REMOVED*** Clear cache
        with console.status("[bold yellow]Clearing cache...[/bold yellow]", spinner="dots"):
            result = cache_service.clear_similar_movies_cache()
        
        if "error" in result:
            console.print(f"[bold red]Error:[/bold red] {result['error']}")
            raise typer.Exit(code=1)
        
        console.print(f"[bold green]Cache cleared![/bold green] Deleted {result['deleted_keys']} keys in {result['elapsed_time']:.2f} seconds") 