"""Embedding generation and management commands."""

import asyncio
import typer
from typer import Typer
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from typing import Optional, List, Dict, Any, Tuple
import rich
import logging

from recommendation_api.config import settings
from recommendation_api.db.connection import (
    get_db_context,
    test_connection,
    get_simple_session,
)
from recommendation_api.db.operations import (
    get_movies_for_embeddings,
    get_movie_features,
)
from recommendation_api.repositories.vector import (
    create_collection,
    store_movie_embedding,
    get_embeddings_stats,
    get_collection_info,
)
from recommendation_api.services.vector_service import get_vector_service
from recommendation_api.config.logging import configure_logging

app: Typer = typer.Typer()
console = Console()


@app.command()
def generate(
    batch_size: Optional[int] = typer.Option(
        None, "--batch-size", help="Batch size for processing"
    ),
    force: bool = typer.Option(False, "--force", help="Force regeneration of existing embeddings"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Limit number of movies to process"),
    movie_id: Optional[int] = typer.Option(None, "--movie-id", help="Process specific movie by ID"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Generate embeddings for movies.

    This command generates vector embeddings for movies and stores them in the vector database.
    It fetches movie data from PostgreSQL, generates embeddings using the configured model,
    and stores them in Qdrant vector database for similarity search.
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

    ***REMOVED*** Always suppress noisy logs unless in debug mode
    noisy_loggers = [
        "httpx",
        "qdrant_client",
        "sentence_transformers",
        "recommendation_api.repositories.vector.repository",
        "recommendation_api.repositories.vector.client",
        "recommendation_api.services.vector_service",
        "recommendation_api.services.embedding_service",
    ]

    if verbose:
        ***REMOVED*** In verbose mode, show more details but still suppress the noisiest ones
        for logger_name in ["httpx", "qdrant_client", "sentence_transformers"]:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    else:
        ***REMOVED*** In normal mode, suppress all noisy loggers
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    ***REMOVED*** Use config defaults if not provided
    actual_batch_size = batch_size or settings.batch_size

    console.print("[cyan]Starting movie embedding generation...[/cyan]")

    ***REMOVED*** Indicate when force mode is active
    if force:
        console.print("[yellow]Force mode enabled - all embeddings will be regenerated.[/yellow]")

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

    ***REMOVED*** Define async function to process movies
    async def process_movies(
        session: Any, movie_ids: List[int], force: bool = False
    ) -> Dict[str, int]:
        return await vector_service.batch_process_movies(session, movie_ids, force=force)

    try:
        with get_db_context() as session:
            ***REMOVED*** Handle specific movie ID if provided
            if movie_id is not None:
                console.print(f"[yellow]Processing specific movie ID: {movie_id}[/yellow]")

                ***REMOVED*** Use asyncio.run to handle async method
                results = asyncio.run(process_movies(session, [movie_id], force=force))

                processed = results.get("processed", 0)
                errors = results.get("failed", 0)
                skipped = results.get("skipped", 0)

                console.print(f"[green]Processed: {processed}[/green]")
                if errors > 0:
                    console.print(f"[yellow]Errors: {errors}[/yellow]")
                if skipped > 0:
                    console.print(f"[blue]Skipped: {skipped}[/blue]")
                return

            ***REMOVED*** Get movies that need embeddings
            console.print(f"[yellow]Fetching movies for embedding generation...[/yellow]")
            movies = get_movies_for_embeddings(
                session=session,
                limit=limit,
            )

            if not movies:
                console.print("[yellow]No movies found for embedding generation.[/yellow]")
                return

            console.print(f"[green]Found {len(movies)} movies to process[/green]")

            ***REMOVED*** Track overall statistics
            overall_stats = {
                "total": len(movies),
                "processed": 0,
                "skipped": 0,
                "failed": 0,
            }

            ***REMOVED*** Track last reported batch for cleaner output
            last_batch_report = 0
            report_interval = max(1, len(movies) // 20)  ***REMOVED*** Report every 5% or at least every batch

            ***REMOVED*** Process movies in batches
            with Progress(
                "[progress.description]{task.description}",
                rich.progress.BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                rich.progress.TimeRemainingColumn(),
                "[cyan]{task.fields[processed]}[/cyan] processed, "
                "[blue]{task.fields[skipped]}[/blue] skipped, "
                "[red]{task.fields[failed]}[/red] failed",
                console=console,
                transient=False,  ***REMOVED*** Keep progress bar visible
                refresh_per_second=2,  ***REMOVED*** Reduce refresh rate to minimize flicker
            ) as progress:
                task = progress.add_task(
                    "[cyan]Processing movies...",
                    total=len(movies),
                    processed=0,
                    skipped=0,
                    failed=0,
                )

                for i in range(0, len(movies), actual_batch_size):
                    batch = movies[i : i + actual_batch_size]
                    batch_num = i // actual_batch_size + 1
                    total_batches = (len(movies) + actual_batch_size - 1) // actual_batch_size

                    ***REMOVED*** Process movies and collect IDs for batch processing
                    movie_ids = []
                    for movie in batch:
                        if movie.id is not None:
                            movie_ids.append(movie.id)

                    ***REMOVED*** Use batch processing through vector service with asyncio.run
                    if movie_ids:
                        ***REMOVED*** Temporarily suppress logs during batch processing unless verbose
                        if not verbose:
                            ***REMOVED*** Temporarily increase log level for batch processing
                            temp_loggers = {}
                            for logger_name in noisy_loggers:
                                logger = logging.getLogger(logger_name)
                                temp_loggers[logger_name] = logger.level
                                logger.setLevel(logging.CRITICAL)

                        try:
                            results = asyncio.run(process_movies(session, movie_ids, force=force))
                        finally:
                            ***REMOVED*** Restore log levels
                            if not verbose:
                                for logger_name, level in temp_loggers.items():
                                    logging.getLogger(logger_name).setLevel(level)

                        ***REMOVED*** Update statistics
                        batch_processed = results.get("processed", 0)
                        batch_failed = results.get("failed", 0)
                        batch_skipped = results.get("skipped", 0)

                        overall_stats["processed"] += batch_processed
                        overall_stats["failed"] += batch_failed
                        overall_stats["skipped"] += batch_skipped

                        ***REMOVED*** Update progress bar with detailed stats
                        progress.update(
                            task,
                            advance=len(batch),
                            processed=overall_stats["processed"],
                            skipped=overall_stats["skipped"],
                            failed=overall_stats["failed"],
                        )

                        ***REMOVED*** Report batch progress periodically or if verbose
                        should_report = (
                            verbose
                            or batch_num - last_batch_report >= report_interval
                            or batch_num == total_batches
                            or batch_failed > 0
                        )

                        if should_report:
                            last_batch_report = batch_num

                            if verbose:
                                console.print(
                                    f"[dim]Batch {batch_num}/{total_batches}: "
                                    f"{batch_processed} processed, "
                                    f"{batch_skipped} skipped, "
                                    f"{batch_failed} failed[/dim]"
                                )
                            elif batch_failed > 0:
                                console.print(
                                    f"[yellow]Batch {batch_num}: {batch_failed} failures detected[/yellow]"
                                )

                ***REMOVED*** Final summary
                console.print("\n[bold cyan]Embedding Generation Summary:[/bold cyan]")

                ***REMOVED*** Create a table for summary statistics
                table = Table()
                table.add_column("Metric", style="cyan")
                table.add_column("Count", style="white")
                table.add_column("Percentage", style="green")

                table.add_row("Total Movies", str(overall_stats["total"]), "100.0%")

                if overall_stats["processed"] > 0:
                    table.add_row(
                        "Processed",
                        str(overall_stats["processed"]),
                        f"{overall_stats['processed'] / overall_stats['total'] * 100:.1f}%",
                    )

                if overall_stats["skipped"] > 0:
                    table.add_row(
                        "Skipped (Already Exists)",
                        str(overall_stats["skipped"]),
                        f"{overall_stats['skipped'] / overall_stats['total'] * 100:.1f}%",
                    )

                if overall_stats["failed"] > 0:
                    table.add_row(
                        "Failed",
                        str(overall_stats["failed"]),
                        f"{overall_stats['failed'] / overall_stats['total'] * 100:.1f}%",
                    )

                console.print(table)

                ***REMOVED*** Add explanatory message if all skipped
                if overall_stats["processed"] == 0 and overall_stats["skipped"] > 0:
                    console.print(
                        "\n[yellow]All movies already have embeddings. Use --force to regenerate.[/yellow]"
                    )

                ***REMOVED*** Add a completion message
                if overall_stats["processed"] > 0:
                    console.print("\n[green]✓ Embedding generation completed successfully![/green]")
                elif overall_stats["failed"] > 0:
                    console.print(
                        "\n[yellow]⚠ Embedding generation completed with some failures.[/yellow]"
                    )
                    if not verbose:
                        console.print("[dim]Use --verbose to see detailed error information.[/dim]")
                else:
                    console.print("\n[blue]ℹ No new embeddings were generated.[/blue]")

    except Exception as e:
        console.print(f"[red]Error during embedding generation: {e}[/red]")
        if verbose:
            import traceback

            console.print(f"[red]{traceback.format_exc()}[/red]")
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
        session = get_simple_session()
        try:
            movies = get_movies_for_embeddings(session, limit=None)
            total_movies = len(movies)
        finally:
            session.close()

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

        console.print(
            f"[green]Found collection with {collection_info.get('points_count', 0)} embeddings[/green]"
        )

        ***REMOVED*** TODO: Implement actual cleanup logic
        ***REMOVED*** This would involve:
        ***REMOVED*** 1. Getting all movie IDs from vector database
        ***REMOVED*** 2. Checking which ones don't exist in PostgreSQL
        ***REMOVED*** 3. Removing orphaned embeddings

        if dry_run:
            console.print(
                "[yellow]Cleanup functionality will be implemented in future versions[/yellow]"
            )
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
        table.add_row("Similarity Threshold", str(settings.similarity_threshold))
        table.add_row("Generation Timeout", f"{settings.embedding_generation_timeout}s")

    console.print(table)


@app.command()
def repair_embeddings(
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="Batch size for processing"),
    specific_movie_id: Optional[int] = typer.Option(
        None, "--movie-id", "-m", help="Specific movie ID to repair"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show which embeddings would be repaired without making changes"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
) -> None:
    """Repair movie embeddings that have metadata but missing vectors.

    This command identifies movies that have records in the vector database with metadata
    but where the vector attribute is None, and regenerates their embeddings.

    Args:
        batch_size: Number of movies to process in each batch
        specific_movie_id: Only repair a specific movie by ID
        dry_run: Only show what would be repaired without making changes
        quiet: Suppress most log output
        verbose: Show detailed progress
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

    ***REMOVED*** Always suppress noisy logs unless in debug mode
    noisy_loggers = [
        "httpx",
        "qdrant_client",
        "sentence_transformers",
        "recommendation_api.repositories.vector.repository",
        "recommendation_api.repositories.vector.client",
        "recommendation_api.services.vector_service",
        "recommendation_api.services.embedding_service",
    ]

    if verbose:
        ***REMOVED*** In verbose mode, show more details but still suppress the noisiest ones
        for logger_name in ["httpx", "qdrant_client", "sentence_transformers"]:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    else:
        ***REMOVED*** In normal mode, suppress all noisy loggers
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    console.print("[cyan]Repairing movie embeddings with missing vectors[/cyan]")

    from recommendation_api.repositories.vector.client import get_qdrant_client
    from recommendation_api.services.vector_service import get_vector_service
    from recommendation_api.db.connection import get_db_context
    from qdrant_client.http import models
    from recommendation_api.config import settings

    ***REMOVED*** Create vector service
    vector_service = get_vector_service()

    ***REMOVED*** Get direct client access for checking points
    client = get_qdrant_client()

    ***REMOVED*** Use a dummy vector for search (to find all points)
    vector_size = settings.embedding_dimension
    dummy_vector = [0.1] * vector_size

    ***REMOVED*** Track progress
    stats = {
        "checked": 0,
        "needing_repair": 0,
        "repaired": 0,
        "failed": 0,
    }

    ***REMOVED*** Function to check if a movie needs repair
    def needs_repair(movie_id: int) -> bool:
        try:
            ***REMOVED*** Get point directly with vectors explicitly requested
            point = client.get_point(movie_id, with_vectors=True)
            if point:
                ***REMOVED*** Has metadata but missing vector
                if point.vector is None:
                    return True
            return False
        except Exception as e:
            if verbose:
                console.print(f"[red]Error checking movie {movie_id}: {e}[/red]")
            return False

    try:
        ***REMOVED*** Handle case for specific movie ID
        if specific_movie_id is not None:
            console.print(f"[cyan]Checking specific movie ID: {specific_movie_id}[/cyan]")

            if needs_repair(specific_movie_id):
                stats["needing_repair"] += 1
                console.print(
                    f"[yellow]Movie ID {specific_movie_id} needs repair (has metadata but vector is None)[/yellow]"
                )

                if not dry_run:
                    ***REMOVED*** Repair the embedding
                    with get_db_context() as session:
                        ***REMOVED*** Temporarily suppress logs during repair unless verbose
                        if not verbose:
                            temp_loggers = {}
                            for logger_name in noisy_loggers:
                                logger = logging.getLogger(logger_name)
                                temp_loggers[logger_name] = logger.level
                                logger.setLevel(logging.CRITICAL)

                        try:
                            embedding = vector_service.generate_and_store_movie_embedding(
                                session, specific_movie_id
                            )
                        finally:
                            if not verbose:
                                for logger_name, level in temp_loggers.items():
                                    logging.getLogger(logger_name).setLevel(level)

                        if embedding:
                            stats["repaired"] += 1
                            console.print(
                                f"[green]Successfully repaired embedding for movie {specific_movie_id}[/green]"
                            )
                        else:
                            stats["failed"] += 1
                            console.print(
                                f"[red]Failed to repair embedding for movie {specific_movie_id}[/red]"
                            )
            else:
                console.print(f"[green]Movie ID {specific_movie_id} does not need repair[/green]")

            stats["checked"] += 1
        ***REMOVED*** Handle case for scanning all movies
        else:
            console.print("[cyan]Scanning all movies for those needing repair...[/cyan]")

            ***REMOVED*** Get all movies with metadata in the vector database
            all_points = client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=dummy_vector,
                limit=10000,  ***REMOVED*** Set a large limit to get as many as possible
                score_threshold=None,  ***REMOVED*** No score threshold
            )

            movies_to_check = [int(point.id) for point in all_points]
            total_movies = len(movies_to_check)
            console.print(f"[cyan]Found {total_movies} movies in vector database to check[/cyan]")

            ***REMOVED*** Find which movies need repair
            movies_needing_repair = []

            if not quiet:
                with typer.progressbar(movies_to_check, label="Checking movies") as progress:
                    for movie_id in progress:
                        stats["checked"] += 1
                        if needs_repair(movie_id):
                            movies_needing_repair.append(movie_id)
                            stats["needing_repair"] += 1
            else:
                ***REMOVED*** Silent checking in quiet mode
                for movie_id in movies_to_check:
                    stats["checked"] += 1
                    if needs_repair(movie_id):
                        movies_needing_repair.append(movie_id)
                        stats["needing_repair"] += 1

            console.print(
                f"[yellow]Found {len(movies_needing_repair)} movies needing repair[/yellow]"
            )

            ***REMOVED*** Process in batches
            if not dry_run and movies_needing_repair:
                console.print("[cyan]Repairing embeddings...[/cyan]")

                ***REMOVED*** Process in batches
                batches = [
                    movies_needing_repair[i : i + batch_size]
                    for i in range(0, len(movies_needing_repair), batch_size)
                ]

                for batch_num, batch in enumerate(batches, 1):
                    if not quiet:
                        console.print(
                            f"[cyan]Processing batch {batch_num}/{len(batches)} ({len(batch)} movies)[/cyan]"
                        )

                    with get_db_context() as session:
                        ***REMOVED*** Temporarily suppress logs during batch repair unless verbose
                        if not verbose:
                            temp_loggers = {}
                            for logger_name in noisy_loggers:
                                logger = logging.getLogger(logger_name)
                                temp_loggers[logger_name] = logger.level
                                logger.setLevel(logging.CRITICAL)

                        try:
                            if not quiet:
                                for movie_id in typer.progressbar(batch, label="Repairing"):
                                    embedding = vector_service.generate_and_store_movie_embedding(
                                        session, movie_id
                                    )
                                    if embedding:
                                        stats["repaired"] += 1
                                    else:
                                        stats["failed"] += 1
                            else:
                                ***REMOVED*** Silent processing in quiet mode
                                for movie_id in batch:
                                    embedding = vector_service.generate_and_store_movie_embedding(
                                        session, movie_id
                                    )
                                    if embedding:
                                        stats["repaired"] += 1
                                    else:
                                        stats["failed"] += 1
                        finally:
                            if not verbose:
                                for logger_name, level in temp_loggers.items():
                                    logging.getLogger(logger_name).setLevel(level)

    except Exception as e:
        console.print(f"[red]Error repairing embeddings: {e}[/red]")
        if verbose:
            import traceback

            console.print(f"[red]{traceback.format_exc()}[/red]")

    ***REMOVED*** Print summary
    console.print("\n[cyan]Repair Summary:[/cyan]")
    table = rich.table.Table()
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")

    table.add_row("Movies Checked", str(stats["checked"]))
    table.add_row("Movies Needing Repair", str(stats["needing_repair"]))

    if not dry_run:
        table.add_row("Movies Repaired", str(stats["repaired"]))
        table.add_row("Repair Failures", str(stats["failed"]))
    else:
        table.add_row("Dry Run", "No changes made")

    console.print(table)

    if dry_run and stats["needing_repair"] > 0:
        console.print("[yellow]Run again without --dry-run to repair these embeddings[/yellow]")
    elif not dry_run and stats["failed"] > 0 and not verbose:
        console.print("[dim]Use --verbose to see detailed error information.[/dim]")


@app.callback(invoke_without_command=True)
def embeddings_main(ctx: typer.Context) -> None:
    """Embedding generation and management commands.

    Commands for generating, managing, and monitoring text embeddings used for
    movie similarity search and recommendation.
    """
    if ctx.invoked_subcommand is None:
        status()
