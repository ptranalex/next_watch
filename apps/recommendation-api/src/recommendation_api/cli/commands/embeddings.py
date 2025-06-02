"""Embedding generation and management commands."""

import typer
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from typing import Optional

from recommendation_api.config import settings
from recommendation_api.db.connection import get_db_context, test_connection
from recommendation_api.db.operations import get_movies_for_embeddings, get_movie_features
from recommendation_api.repositories.vector import (
    create_collection,
    store_movie_embedding,
    get_embeddings_stats,
    get_collection_info,
)
from recommendation_api.services.embedding import generate_movie_embedding
from recommendation_api.services.vector_service import get_vector_service

app = typer.Typer()
console = Console()


@app.command()
def generate(
    batch_size: Optional[int] = typer.Option(None, "--batch-size", help="Batch size for processing"),
    force: bool = typer.Option(False, "--force", help="Force regeneration of existing embeddings"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Limit number of movies to process"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
) -> None:
    """Generate embeddings for movies.
    
    This command generates vector embeddings for movies and stores them in the vector database.
    It fetches movie data from PostgreSQL, generates embeddings using the configured model,
    and stores them in Qdrant vector database for similarity search.
    """
    ***REMOVED*** Use config defaults if not provided
    actual_batch_size = batch_size or settings.batch_size
    
    console.print("[cyan]Starting movie embedding generation...[/cyan]")
    
    ***REMOVED*** Test database connection
    if not test_connection():
        console.print("[red]Database connection failed. Please check your configuration.[/red]")
        raise typer.Exit(1)
    
    ***REMOVED*** Get vector service
    vector_service = get_vector_service()
    
    ***REMOVED*** Create Qdrant collection if it doesn't exist
    console.print("[yellow]Setting up vector database collection...[/yellow]")
    if not vector_service.ensure_collection_exists():
        console.print("[red]Failed to create vector database collection.[/red]")
        raise typer.Exit(1)
    
    try:
        with get_db_context() as session:
            ***REMOVED*** Get movies that need embeddings
            console.print(f"[yellow]Fetching movies for embedding generation...[/yellow]")
            movies = get_movies_for_embeddings(
                session=session,
                limit=limit,
                min_rating=settings.min_imdb_rating if not force else None,
            )
            
            if not movies:
                console.print("[yellow]No movies found for embedding generation.[/yellow]")
                return
            
            console.print(f"[green]Found {len(movies)} movies to process[/green]")
            
            ***REMOVED*** Process movies in batches
            with Progress() as progress:
                task = progress.add_task(
                    "[cyan]Generating embeddings...", 
                    total=len(movies)
                )
                
                processed = 0
                errors = 0
                
                for i in range(0, len(movies), actual_batch_size):
                    batch = movies[i:i + actual_batch_size]
                    
                    ***REMOVED*** Process movies and collect IDs for batch processing
                    movie_ids = []
                    for movie in batch:
                        if movie.id is not None:
                            movie_ids.append(movie.id)
                    
                    ***REMOVED*** Use batch processing through vector service
                    if movie_ids:
                        results = vector_service.batch_process_movies(session, movie_ids)
                        processed += results.get("processed", 0)
                        errors += results.get("failed", 0)
                        skipped = results.get("skipped", 0)
                        
                        if verbose:
                            console.print(f"[green]Batch processed: {results.get('processed', 0)} movies[/green]")
                            if results.get("failed", 0) > 0:
                                console.print(f"[yellow]Batch errors: {results.get('failed', 0)} movies[/yellow]")
                            if results.get("skipped", 0) > 0:
                                console.print(f"[blue]Batch skipped: {results.get('skipped', 0)} movies[/blue]")
                        
                    ***REMOVED*** Update progress
                    progress.update(task, advance=len(batch))
                
                console.print(f"[green]Embedding generation completed![/green]")
                console.print(f"[green]Processed: {processed}[/green]")
                if errors > 0:
                    console.print(f"[yellow]Errors: {errors}[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error during embedding generation: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed status"),
) -> None:
    """Show embedding generation status.
    
    This command shows the current status of embedding generation, including:
    - Total movies in the database
    - Number of movies with embeddings
    - Indexed embeddings count
    - Collection status
    - Completion percentage
    """
    console.print("[cyan]Checking embedding status...[/cyan]")
    
    ***REMOVED*** Test database connection
    if not test_connection():
        console.print("[red]Database connection failed.[/red]")
        raise typer.Exit(1)
    
    try:
        ***REMOVED*** Get database stats
        with get_db_context() as session:
            movies = get_movies_for_embeddings(session, limit=None)
            total_movies = len(movies)
        
        ***REMOVED*** Get vector service stats
        vector_service = get_vector_service()
        stats = vector_service.get_vector_stats()
        collection_info = get_collection_info()
        
        ***REMOVED*** Create status table
        table = Table(title="Embedding Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Movies in Database", str(total_movies))
        table.add_row("Movies with Embeddings", str(stats.get("total_embeddings", 0)))
        table.add_row("Indexed Embeddings", str(stats.get("indexed_embeddings", 0)))
        table.add_row("Collection Status", stats.get("collection_status", "unknown"))
        table.add_row("Service Status", stats.get("service_status", "unknown"))
        
        if verbose and collection_info:
            table.add_row("Vector Dimension", str(stats.get("vector_size", 0)))
            table.add_row("Distance Metric", stats.get("distance_metric", "unknown"))
            table.add_row("Segments Count", str(collection_info.get("segments_count", 0)))
        
        console.print(table)
        
        ***REMOVED*** Calculate completion percentage
        if total_movies > 0:
            completion = (stats.get("total_embeddings", 0) / total_movies) * 100
            console.print(f"\n[cyan]Completion: {completion:.1f}%[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def cleanup(
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Show what would be cleaned up"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed cleanup info"),
) -> None:
    """Clean up orphaned embeddings.
    
    This command identifies and removes embeddings for movies that no longer exist
    in the database. It helps maintain a clean vector database by removing stale entries.
    """
    console.print("[cyan]Starting embedding cleanup...[/cyan]")
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")
    
    try:
        ***REMOVED*** Test database connection
        if not test_connection():
            console.print("[red]Database connection failed.[/red]")
            raise typer.Exit(1)
        
        ***REMOVED*** Get collection info
        collection_info = get_collection_info()
        if not collection_info:
            console.print("[yellow]No vector collection found - nothing to clean up.[/yellow]")
            return
        
        console.print(f"[green]Found collection with {collection_info.get('points_count', 0)} embeddings[/green]")
        
        ***REMOVED*** TODO: Implement actual cleanup logic
        ***REMOVED*** This would involve:
        ***REMOVED*** 1. Getting all movie IDs from vector database
        ***REMOVED*** 2. Checking which ones don't exist in PostgreSQL
        ***REMOVED*** 3. Removing orphaned embeddings
        
        if dry_run:
            console.print("[yellow]Cleanup functionality will be implemented in future versions[/yellow]")
        else:
            console.print("[yellow]Cleanup executed (placeholder)[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error during cleanup: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
) -> None:
    """Show embedding configuration and model information.
    
    This command displays the current configuration for embedding generation,
    including the model being used, vector dimensions, and database settings.
    """
    table = Table(title="Embedding Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Embedding Model", settings.embedding_model)
    table.add_row("Vector Dimension", str(settings.embedding_dimension))
    table.add_row("Batch Size", str(settings.batch_size))
    table.add_row("Max Sequence Length", str(settings.max_sequence_length))
    table.add_row("Qdrant URL", settings.qdrant_url)
    table.add_row("Collection Name", settings.qdrant_collection_name)
    
    if verbose:
        table.add_row("Min IMDb Rating", str(settings.min_imdb_rating))
        table.add_row("Similarity Threshold", str(settings.similarity_threshold))
        table.add_row("Generation Timeout", f"{settings.embedding_generation_timeout}s")
    
    console.print(table)


@app.callback(invoke_without_command=True)
def embeddings_main(ctx: typer.Context) -> None:
    """Embedding generation and management commands.
    
    Commands for generating, managing, and monitoring text embeddings used for
    movie similarity search and recommendation.
    """
    if ctx.invoked_subcommand is None:
        status() 