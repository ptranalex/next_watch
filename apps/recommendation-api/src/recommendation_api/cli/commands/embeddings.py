"""Embedding generation and management commands."""

import asyncio
import logging

import typer
from config.logging import configure_logging, get_logger
from rich.console import Console
from rich.table import Table
from typer import Typer

from recommendation_api.services.embedding_service import get_embedding_service

app: Typer = typer.Typer()
console = Console()
logger = get_logger(__name__)


@app.command()
def generate(
    batch_size: int | None = typer.Option(None, "--batch-size", help="Batch size for processing"),
    force: bool = typer.Option(False, "--force", help="Force regeneration of existing embeddings"),
    limit: int | None = typer.Option(None, "--limit", help="Limit number of movies to process"),
    movie_id: int | None = typer.Option(None, "--movie-id", help="Process specific movie by ID"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Generate embeddings for movies.

    This command generates vector embeddings for movies and stores them in the vector database.
    It fetches movie data from the backend API, generates embeddings using the configured model,
    and stores them in Qdrant vector database for similarity search.
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
        "recommendation_api.services.embedding_service",
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

    # Use asyncio to run the async function
    asyncio.run(
        _run_generate(
            batch_size=batch_size,
            force=force,
            limit=limit,
            movie_id=movie_id,
            verbose=verbose,
            quiet=quiet,
            noisy_loggers=noisy_loggers,
        )
    )


async def _run_generate(
    batch_size: int | None,
    force: bool,
    limit: int | None,
    movie_id: int | None,
    verbose: bool,
    quiet: bool,
    noisy_loggers: list[str],
) -> None:
    """Async implementation of generate command."""
    # Temporarily suppress logs during generation unless verbose
    temp_loggers = {}
    if not verbose:
        for logger_name in noisy_loggers:
            logger = logging.getLogger(logger_name)
            temp_loggers[logger_name] = logger.level
            logger.setLevel(logging.CRITICAL)

    embedding_service = None
    try:
        # Initialize embedding service
        console.print("[cyan]Initializing embedding service...[/cyan]")
        embedding_service = await get_embedding_service()

        # Indicate when force mode is active
        if force:
            console.print(
                "[yellow]Force mode enabled - all embeddings will be regenerated.[/yellow]"
            )

        # Process specific movie or all movies
        movie_ids = [movie_id] if movie_id is not None else None

        if movie_id is not None:
            console.print(f"[yellow]Processing specific movie ID: {movie_id}[/yellow]")

        # Run embedding generation with progress tracking if not quiet
        if not quiet:
            with console.status(
                "[bold green]Generating embeddings...[/bold green]", spinner="dots"
            ):
                results = await embedding_service.generate_embeddings(
                    movie_ids=movie_ids,
                    force=force,
                    limit=limit,
                    batch_size=batch_size,
                )
        else:
            # Silent mode
            results = await embedding_service.generate_embeddings(
                movie_ids=movie_ids,
                force=force,
                limit=limit,
                batch_size=batch_size,
            )

        # Print results
        if not quiet:
            console.print("\n[bold cyan]Embedding Generation Summary:[/bold cyan]")

            # Create a table for summary statistics
            table = Table()
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="white")
            table.add_column("Percentage", style="green")

            total = results["total"]
            processed = results["processed"]
            skipped = results["skipped"]
            failed = results["failed"]

            table.add_row("Total Movies", str(total), "100.0%")

            if processed > 0:
                table.add_row(
                    "Processed",
                    str(processed),
                    f"{processed / total * 100:.1f}%" if total > 0 else "0.0%",
                )

            if skipped > 0:
                table.add_row(
                    "Skipped (Already Exists)",
                    str(skipped),
                    f"{skipped / total * 100:.1f}%" if total > 0 else "0.0%",
                )

            if failed > 0:
                table.add_row(
                    "Failed",
                    str(failed),
                    f"{failed / total * 100:.1f}%" if total > 0 else "0.0%",
                )

            console.print(table)

            # Add explanatory message if all skipped
            if processed == 0 and skipped > 0:
                console.print(
                    "\n[yellow]All movies already have embeddings. Use --force to regenerate.[/yellow]"
                )

            # Add a completion message
            if processed > 0:
                console.print("\n[green]✓ Embedding generation completed successfully![/green]")
            elif failed > 0:
                console.print(
                    "\n[yellow]⚠ Embedding generation completed with some failures.[/yellow]"
                )
                if not verbose:
                    console.print("[dim]Use --verbose to see detailed error information.[/dim]")
            else:
                console.print("\n[blue]ℹ No new embeddings were generated.[/blue]")

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

        # Clean up embedding service
        if embedding_service:
            await embedding_service.close()


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

    # Use asyncio to run the async function
    asyncio.run(_run_status(verbose=verbose))


async def _run_status(verbose: bool) -> None:
    """Async implementation of status command."""
    embedding_service = None
    try:
        # Initialize embedding service
        embedding_service = await get_embedding_service()

        # Get status information
        with console.status(
            "[bold green]Retrieving status information...[/bold green]", spinner="dots"
        ):
            status_info = embedding_service.get_embedding_status()

            # Get total movies from API
            all_movies = await embedding_service.get_movies_for_embeddings()
            total_movies = len(all_movies)

        if "error" in status_info:
            console.print(f"[bold red]Error:[/bold red] {status_info['error']}")
            raise typer.Exit(code=1)

        # Create status table
        table = Table(title="Embedding Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Movies in Database", str(total_movies))
        table.add_row("Movies with Embeddings", str(status_info.get("total_embeddings", 0)))
        table.add_row("Indexed Embeddings", str(status_info.get("indexed_embeddings", 0)))
        table.add_row("Collection Status", status_info.get("collection_status", "unknown"))
        table.add_row("Service Status", status_info.get("service_status", "unknown"))

        if verbose:
            collection_info = status_info.get("collection_info", {})
            table.add_row("Vector Dimension", str(status_info.get("vector_dimension", 0)))
            table.add_row("Distance Metric", status_info.get("distance_metric", "unknown"))
            table.add_row("Segments Count", str(collection_info.get("segments_count", 0)))

        console.print(table)

        # Calculate completion percentage
        if total_movies > 0:
            completion = (status_info.get("total_embeddings", 0) / total_movies) * 100
            console.print(f"\n[cyan]Completion: {completion:.1f}%[/cyan]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1) from e

    finally:
        # Clean up embedding service
        if embedding_service:
            await embedding_service.close()


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

    # TODO: Implement cleanup using EmbeddingService
    console.print("[yellow]Cleanup functionality will be implemented in future versions[/yellow]")
    console.print("[dim]This would check for orphaned embeddings and remove them.[/dim]")


@app.command()
def info(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
) -> None:
    """Show embedding configuration and model information.

    This command displays the current configuration for embedding generation,
    including the model being used, vector dimensions, and database settings.
    """
    # Use asyncio to run the async function
    asyncio.run(_run_info(verbose=verbose))


async def _run_info(verbose: bool) -> None:
    """Async implementation of info command."""
    embedding_service = None
    try:
        # Initialize embedding service
        embedding_service = await get_embedding_service()

        # Get configuration information
        config_info = embedding_service.get_configuration_info()

        table = Table(title="Embedding Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Embedding Model", config_info.get("embedding_model", "unknown"))
        table.add_row("Vector Dimension", str(config_info.get("vector_dimension", 0)))
        table.add_row("Batch Size", str(config_info.get("batch_size", 0)))
        table.add_row("Max Sequence Length", str(config_info.get("max_sequence_length", 0)))
        table.add_row("Qdrant URL", config_info.get("qdrant_url", "unknown"))
        table.add_row("Collection Name", config_info.get("collection_name", "unknown"))

        if verbose:
            table.add_row("Similarity Threshold", str(config_info.get("similarity_threshold", 0)))
            table.add_row("Generation Timeout", f"{config_info.get('generation_timeout', 0)}s")

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1) from e

    finally:
        # Clean up embedding service
        if embedding_service:
            await embedding_service.close()


@app.command()
def repair_embeddings(
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="Batch size for processing"),
    specific_movie_id: int | None = typer.Option(
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
        "recommendation_api.services.embedding_service",
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

    console.print("[cyan]Repairing movie embeddings with missing vectors[/cyan]")

    # Use asyncio to run the async function
    asyncio.run(
        _run_repair(
            batch_size=batch_size,
            specific_movie_id=specific_movie_id,
            dry_run=dry_run,
            quiet=quiet,
            verbose=verbose,
            noisy_loggers=noisy_loggers,
        )
    )


async def _run_repair(
    batch_size: int,
    specific_movie_id: int | None,
    dry_run: bool,
    quiet: bool,
    verbose: bool,
    noisy_loggers: list[str],
) -> None:
    """Async implementation of repair command."""
    # Temporarily suppress logs during repair unless verbose
    temp_loggers = {}
    if not verbose:
        for logger_name in noisy_loggers:
            logger = logging.getLogger(logger_name)
            temp_loggers[logger_name] = logger.level
            logger.setLevel(logging.CRITICAL)

    embedding_service = None
    try:
        # Initialize embedding service
        if not quiet:
            console.print("[cyan]Initializing embedding service...[/cyan]")

        embedding_service = await get_embedding_service()

        # Handle case for specific movie ID
        movie_ids = [specific_movie_id] if specific_movie_id is not None else None

        if specific_movie_id is not None:
            console.print(f"[cyan]Checking specific movie ID: {specific_movie_id}[/cyan]")

        # Run repair process
        if not quiet and not dry_run:
            with console.status("[bold green]Repairing embeddings...[/bold green]", spinner="dots"):
                results = await embedding_service.repair_embeddings(
                    movie_ids=movie_ids,
                    batch_size=batch_size,
                    dry_run=dry_run,
                )
        else:
            # Silent mode or dry run
            results = await embedding_service.repair_embeddings(
                movie_ids=movie_ids,
                batch_size=batch_size,
                dry_run=dry_run,
            )

        # Print summary
        if not quiet:
            console.print("\n[cyan]Repair Summary:[/cyan]")
            table = Table()
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="green")

            table.add_row("Movies Checked", str(results.get("checked", 0)))
            table.add_row("Movies Needing Repair", str(results.get("needing_repair", 0)))

            if not dry_run:
                table.add_row("Movies Repaired", str(results.get("repaired", 0)))
                table.add_row("Repair Failures", str(results.get("failed", 0)))
            else:
                table.add_row("Dry Run", "No changes made")

            console.print(table)

            if dry_run and results.get("needing_repair", 0) > 0:
                console.print(
                    "[yellow]Run again without --dry-run to repair these embeddings[/yellow]"
                )
            elif not dry_run and results.get("failed", 0) > 0 and not verbose:
                console.print("[dim]Use --verbose to see detailed error information.[/dim]")

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

        # Clean up embedding service
        if embedding_service:
            await embedding_service.close()


@app.callback(invoke_without_command=True)
def embeddings_main(ctx: typer.Context) -> None:
    """Embedding generation and management commands.

    Commands for generating, managing, and monitoring text embeddings used for
    movie similarity search and recommendation.
    """
    if ctx.invoked_subcommand is None:
        status()
