"""Debug and diagnostic commands for the recommendation system."""

import typer
import numpy as np
from rich.console import Console
from rich.table import Table
from typing import Optional, List, Dict, Any
import logging

from recommendation_api.db.connection import get_db_context
from recommendation_api.db.operations import get_movies_by_ids, get_movie_by_id
from recommendation_api.repositories.vector import VectorRepository
from recommendation_api.repositories.vector.client import get_qdrant_client
from recommendation_api.services.vector_service import VectorService, get_vector_service
from recommendation_api.config.logging import configure_logging
from recommendation_api.config import settings
from qdrant_client.http import models

app = typer.Typer()
console = Console()


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging for debug commands.

    Args:
        verbose: Enable verbose logging
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging based on verbosity
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "WARNING"
    configure_logging(log_level=log_level, verbose=verbose)

    ***REMOVED*** Suppress noisy logs unless in verbose mode
    if not verbose:
        ***REMOVED*** Set higher log levels for noisy libraries
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("qdrant_client").setLevel(logging.WARNING)
        logging.getLogger("recommendation_api.repositories.vector.repository").setLevel(
            logging.WARNING
        )
        logging.getLogger("recommendation_api.repositories.vector.client").setLevel(logging.WARNING)

    ***REMOVED*** Set to ERROR level in quiet mode
    if quiet:
        for logger_name in [
            "httpx",
            "qdrant_client",
            "recommendation_api.repositories.vector.repository",
            "recommendation_api.repositories.vector.client",
        ]:
            logging.getLogger(logger_name).setLevel(logging.ERROR)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    ***REMOVED*** Convert to numpy arrays for efficient calculation
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    ***REMOVED*** Calculate cosine similarity
    dot_product = np.dot(v1, v2)
    norm_a = np.linalg.norm(v1)
    norm_b = np.linalg.norm(v2)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


@app.command()
def check_embedding(
    movie_id: int = typer.Argument(..., help="Movie ID to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show vector data"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Check if a movie has an embedding in the vector database.

    This command checks if a specific movie ID has an embedding in the vector database
    and displays metadata about it.

    Args:
        movie_id: Movie ID to check
        verbose: Show detailed vector data
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    console.print(f"[cyan]Checking embedding for movie ID: {movie_id}[/cyan]")

    ***REMOVED*** Get Qdrant client
    client = get_qdrant_client()

    ***REMOVED*** Check if the embedding exists
    try:
        ***REMOVED*** Try direct point retrieval
        response = client.get_point(
            collection_name=settings.qdrant_collection_name, point_id=movie_id, with_vectors=verbose
        )

        if response:
            console.print(
                f"[green]✓ Movie ID {movie_id} has an embedding in the vector database[/green]"
            )

            ***REMOVED*** Create a table for metadata
            table = Table(title=f"Embedding Metadata for Movie ID {movie_id}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            ***REMOVED*** Add metadata from payload
            if hasattr(response, "payload") and response.payload:
                for key, value in response.payload.items():
                    ***REMOVED*** Format value for display
                    if isinstance(value, list) and len(value) > 10:
                        display_value = f"{str(value[:3])[:-1]}, ... {len(value)} items]"
                    else:
                        display_value = str(value)
                    table.add_row(key, display_value)

            console.print(table)

            ***REMOVED*** Show vector status
            vector_status = (
                "Present" if hasattr(response, "vector") and response.vector else "Missing"
            )
            console.print(f"[yellow]Vector status: {vector_status}[/yellow]")

            ***REMOVED*** Show vector data if verbose and vector exists
            if verbose and hasattr(response, "vector") and response.vector:
                console.print("[yellow]Vector Data (first 10 dimensions):[/yellow]")
                ***REMOVED*** Use a safer approach to get the first elements of the vector
                if isinstance(response.vector, list):
                    console.print(response.vector[:10])
                    console.print(f"[yellow]Vector Dimensions: {len(response.vector)}[/yellow]")
                else:
                    console.print(
                        "[yellow]Vector data not available in the expected format[/yellow]"
                    )
            elif verbose and (not hasattr(response, "vector") or response.vector is None):
                console.print("[red]⚠ Vector data is missing for this embedding[/red]")
        else:
            console.print(
                f"[red]✗ Movie ID {movie_id} does not have an embedding in the vector database[/red]"
            )

            ***REMOVED*** Try searching by metadata as fallback
            console.print("[yellow]Trying to find via metadata search...[/yellow]")
            dummy_vector = [0.1] * settings.embedding_dimension
            similar_response = client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=dummy_vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="movie_id", match=models.MatchValue(value=movie_id)
                        )
                    ]
                ),
                limit=1,
            )

            if similar_response and len(similar_response) > 0:
                console.print(
                    f"[green]Found movie via metadata search (ID: {similar_response[0].id})[/green]"
                )
                console.print(
                    "[yellow]Note: This movie exists in the vector database but may not have a vector[/yellow]"
                )
            else:
                console.print("[red]No embedding found via any method[/red]")

                ***REMOVED*** Check if movie exists in database
                with get_db_context() as session:
                    movie = get_movie_by_id(session, movie_id)
                    if movie:
                        console.print(f"[yellow]Movie exists in database: {movie.title}[/yellow]")
                        console.print(
                            "[yellow]Run 'rec-api debug recreate_embedding {movie_id}' to create the embedding[/yellow]"
                        )
                    else:
                        console.print("[red]Movie does not exist in the database[/red]")

    except Exception as e:
        console.print(f"[red]Error checking embedding: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@app.command()
def similar_movies(
    movie_id: int = typer.Argument(..., help="Movie ID to find similar movies for"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of similar movies"),
    min_score: float = typer.Option(
        0.01, "--min-score", "-s", help="Minimum similarity score (0-1)"
    ),
    direct_search: bool = typer.Option(
        False, "--direct", "-d", help="Use direct repository search"
    ),
    show_ids_only: bool = typer.Option(
        False, "--ids-only", "-i", help="Show only movie IDs without details"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Find movies similar to a specific movie ID.

    This command searches for movies similar to the specified movie ID
    using vector similarity search. It can use different search methods
    and display results with or without movie details.

    Args:
        movie_id: Movie ID to find similar movies for
        limit: Maximum number of similar movies to return
        min_score: Minimum similarity score threshold (0-1)
        direct_search: Use direct repository search instead of service
        show_ids_only: Show only movie IDs without fetching details
        verbose: Show detailed progress
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    console.print(f"[cyan]Finding similar movies for movie ID: {movie_id}[/cyan]")
    console.print(f"[cyan]Using minimum similarity score: {min_score}[/cyan]")

    similar_movies = []

    try:
        if direct_search:
            ***REMOVED*** Use direct repository search
            console.print("[yellow]Using direct repository search method[/yellow]")
            repo = VectorRepository()
            similar_movies = repo.search_by_movie_id(
                movie_id=movie_id, limit=limit, score_threshold=min_score
            )
        else:
            ***REMOVED*** Use service layer (standard approach)
            console.print("[yellow]Using service layer search method[/yellow]")
            service = VectorService()
            similar_movies = service.find_similar_movies_by_id(
                movie_id=movie_id, limit=limit, min_score=min_score
            )

        ***REMOVED*** If no results with standard approach, try fallback
        if not similar_movies:
            console.print(
                "[yellow]No results from standard search, trying fallback approach[/yellow]"
            )

            ***REMOVED*** Use direct search with dummy vector
            client = get_qdrant_client()
            dummy_vector = [0.1] * settings.embedding_dimension
            similar_response = client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=dummy_vector,
                query_filter=models.Filter(
                    must_not=[
                        models.FieldCondition(
                            key="movie_id", match=models.MatchValue(value=movie_id)
                        )
                    ]
                ),
                limit=limit,
                score_threshold=min_score,
            )

            if similar_response:
                similar_movies = [(int(point.id), float(point.score)) for point in similar_response]

        ***REMOVED*** Display results
        if similar_movies and len(similar_movies) > 0:
            console.print(f"[green]Found {len(similar_movies)} similar movies[/green]")

            if show_ids_only:
                ***REMOVED*** Show just IDs and scores
                for i, (m_id, score) in enumerate(similar_movies, 1):
                    console.print(f"{i}. Movie ID: {m_id}, Score: {score:.4f}")
            else:
                ***REMOVED*** Get movie details from database
                with get_db_context() as session:
                    movie_ids = [m_id for m_id, _ in similar_movies]
                    movies = get_movies_by_ids(session, movie_ids)

                    ***REMOVED*** Create a table
                    table = Table(title=f"Similar Movies to ID {movie_id}")
                    table.add_column("Movie ID", style="cyan")
                    table.add_column("Title", style="green")
                    table.add_column("Similarity Score", style="yellow")
                    table.add_column("IMDb Rating", style="magenta")
                    table.add_column("Release Year", style="blue")

                    ***REMOVED*** Map IDs to movies
                    id_to_movie = {m.id: m for m in movies if m.id is not None}

                    ***REMOVED*** Add rows
                    for m_id, score in similar_movies:
                        movie = id_to_movie.get(m_id)
                        if movie:
                            title = movie.title
                            imdb = movie.imdb_rating if movie.imdb_rating is not None else "N/A"
                            year = movie.release_date if movie.release_date is not None else "N/A"
                        else:
                            title = f"Unknown (ID: {m_id})"
                            imdb = "N/A"
                            year = "N/A"

                        table.add_row(str(m_id), title, f"{score:.4f}", str(imdb), str(year))

                    console.print(table)
        else:
            console.print(
                f"[yellow]No similar movies found with minimum score {min_score}[/yellow]"
            )
            console.print(
                "[yellow]Try lowering the minimum score with --min-score parameter[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]Error finding similar movies: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@app.command()
def compare_movies(
    movie_id1: int = typer.Argument(..., help="First movie ID"),
    movie_id2: int = typer.Argument(..., help="Second movie ID"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show embedding details"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Compare two movies by calculating similarity between their embeddings.

    This command retrieves embeddings for two movies and calculates their
    similarity score, displaying details about both movies and their vectors.

    Args:
        movie_id1: First movie ID
        movie_id2: Second movie ID
        verbose: Show detailed embedding data
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    console.print(f"[cyan]Comparing movies: {movie_id1} and {movie_id2}[/cyan]")

    ***REMOVED*** Create vector service
    service = VectorService()

    ***REMOVED*** Get embeddings
    embedding1 = service.get_movie_embedding(movie_id1)
    embedding2 = service.get_movie_embedding(movie_id2)

    if not embedding1:
        console.print(f"[red]No embedding found for movie ID {movie_id1}[/red]")
        return

    if not embedding2:
        console.print(f"[red]No embedding found for movie ID {movie_id2}[/red]")
        return

    console.print(f"[green]Found embeddings for both movies[/green]")

    ***REMOVED*** Get movie details
    try:
        with get_db_context() as session:
            movies = get_movies_by_ids(session, [movie_id1, movie_id2])

            ***REMOVED*** Create a table for movie details
            table = Table(title="Movie Comparison")
            table.add_column("Property", style="cyan")
            table.add_column(f"Movie {movie_id1}", style="green")
            table.add_column(f"Movie {movie_id2}", style="yellow")

            ***REMOVED*** Get movie objects
            movie1 = next((m for m in movies if m.id == movie_id1), None)
            movie2 = next((m for m in movies if m.id == movie_id2), None)

            if movie1 and movie2:
                table.add_row("Title", movie1.title, movie2.title)
                table.add_row(
                    "Release Year",
                    str(movie1.release_date) if movie1.release_date else "N/A",
                    str(movie2.release_date) if movie2.release_date else "N/A",
                )
                table.add_row(
                    "IMDb Rating",
                    str(movie1.imdb_rating) if movie1.imdb_rating else "N/A",
                    str(movie2.imdb_rating) if movie2.imdb_rating else "N/A",
                )

                ***REMOVED*** Handle genres correctly (either as list of strings or list of Genre objects)
                genres1 = movie1.genres if movie1.genres else []
                genres2 = movie2.genres if movie2.genres else []

                ***REMOVED*** Convert genre objects to strings if needed
                if genres1 and hasattr(genres1[0], "name"):
                    genres1_str = ", ".join(g.name for g in genres1)
                else:
                    genres1_str = ", ".join(str(g) for g in genres1) if genres1 else "N/A"

                if genres2 and hasattr(genres2[0], "name"):
                    genres2_str = ", ".join(g.name for g in genres2)
                else:
                    genres2_str = ", ".join(str(g) for g in genres2) if genres2 else "N/A"

                table.add_row("Genres", genres1_str, genres2_str)

                console.print(table)

            ***REMOVED*** Calculate similarity using our local implementation
            similarity = cosine_similarity(embedding1, embedding2)

            console.print(f"[cyan]Similarity Score: {similarity:.4f}[/cyan]")

            if verbose:
                ***REMOVED*** Display vector information
                console.print(f"[yellow]Embedding dimensions: {len(embedding1)}[/yellow]")

                ***REMOVED*** Show first few dimensions of each vector
                console.print(f"[yellow]First 5 dimensions of Movie {movie_id1}:[/yellow]")
                console.print(embedding1[:5])
                console.print(f"[yellow]First 5 dimensions of Movie {movie_id2}:[/yellow]")
                console.print(embedding2[:5])

    except Exception as e:
        console.print(f"[red]Error comparing movies: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@app.command()
def vector_status(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Show status of the vector database.

    This command displays information about the vector database,
    including collection stats, index status, and configuration.

    Args:
        verbose: Show detailed information
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    console.print("[cyan]Checking vector database status...[/cyan]")

    try:
        ***REMOVED*** Get client
        client = get_qdrant_client()

        ***REMOVED*** Test connection
        if client.test_connection():
            console.print("[green]✓ Vector database connection successful[/green]")
        else:
            console.print("[red]✗ Vector database connection failed[/red]")
            return

        ***REMOVED*** Get collection info
        collection_name = settings.qdrant_collection_name

        collection_info = None
        try:
            collection_info = client.get_collection_info(collection_name)
        except Exception as e:
            console.print(f"[red]Error getting collection info: {e}[/red]")

        if collection_info:
            ***REMOVED*** Display collection info in a table
            table = Table(title=f"Vector Collection: {collection_name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            ***REMOVED*** Add basic info
            if hasattr(collection_info, "points_count"):
                table.add_row("Points Count", str(collection_info.points_count))
            if hasattr(collection_info, "vectors_count"):
                table.add_row("Vectors Count", str(collection_info.vectors_count))
            if hasattr(collection_info, "segments_count"):
                table.add_row("Segments Count", str(collection_info.segments_count))
            if hasattr(collection_info, "config"):
                if hasattr(collection_info.config, "params"):
                    if hasattr(collection_info.config.params, "vectors"):
                        vector_params = collection_info.config.params.vectors
                        if hasattr(vector_params, "size"):
                            table.add_row("Vector Size", str(vector_params.size))
                        if hasattr(vector_params, "distance"):
                            table.add_row("Distance Metric", str(vector_params.distance))

            console.print(table)

            ***REMOVED*** Provide some helpful context about the data
            if hasattr(collection_info, "points_count") and hasattr(
                collection_info, "vectors_count"
            ):
                if collection_info.points_count > collection_info.vectors_count:
                    diff = collection_info.points_count - collection_info.vectors_count
                    console.print(
                        f"[yellow]⚠ Warning: {diff} points have metadata but no vector data[/yellow]"
                    )
                    console.print(
                        "[yellow]Use 'rec-api debug recreate_embedding' or 'rec-api embeddings repair_embeddings' to fix[/yellow]"
                    )
        else:
            console.print(f"[yellow]Collection '{collection_name}' not found[/yellow]")

    except Exception as e:
        console.print(f"[red]Error checking vector status: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@app.command()
def recreate_embedding(
    movie_id: int = typer.Argument(..., help="Movie ID to recreate embedding for"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force recreation even if embedding exists"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Completely delete and recreate an embedding for a specific movie.

    This command addresses cases where a movie has a record in the vector database
    but its vector attribute is None, by completely deleting and recreating the embedding.

    Args:
        movie_id: Movie ID to recreate embedding for
        force: Force recreation even if the embedding already exists
        verbose: Show detailed progress
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    console.print(f"[cyan]Recreating embedding for movie ID: {movie_id}[/cyan]")

    ***REMOVED*** Get repositories and services
    repo = VectorRepository()
    vector_service = get_vector_service()
    client = get_qdrant_client()

    ***REMOVED*** First check if point exists
    point = client.get_point(movie_id, with_vectors=True)
    if point:
        console.print(f"[yellow]Found existing point for movie ID {movie_id}[/yellow]")
        has_vector = point.vector is not None

        if has_vector and not force:
            console.print(
                f"[green]Movie ID {movie_id} already has a valid vector. Use --force to recreate anyway.[/green]"
            )
            return

        ***REMOVED*** Delete the existing point
        console.print("[yellow]Deleting existing point...[/yellow]")
        success = repo.delete_movie_embedding(movie_id)

        if success:
            console.print(
                f"[green]Successfully deleted existing point for movie ID {movie_id}[/green]"
            )
        else:
            console.print(f"[red]Failed to delete existing point for movie ID {movie_id}[/red]")
            return

    ***REMOVED*** Generate and store new embedding
    console.print("[cyan]Generating and storing new embedding...[/cyan]")

    with get_db_context() as session:
        ***REMOVED*** Get movie details to confirm it exists
        movie = get_movie_by_id(session, movie_id)
        if not movie:
            console.print(f"[red]Movie ID {movie_id} not found in database[/red]")
            return

        console.print(f"[green]Found movie in database: {movie.title}[/green]")

        ***REMOVED*** Generate and store embedding
        embedding = vector_service.generate_and_store_movie_embedding(session, movie_id)

        if embedding:
            console.print(
                f"[green]✓ Successfully generated and stored embedding for movie ID {movie_id}[/green]"
            )

            ***REMOVED*** Verify the embedding was stored correctly
            console.print("[cyan]Verifying embedding...[/cyan]")
            point = client.get_point(movie_id, with_vectors=True)

            if point and point.vector is not None:
                console.print(
                    f"[green]✓ Verification successful. Embedding stored correctly with {len(point.vector)} dimensions.[/green]"
                )
            else:
                console.print(
                    f"[red]✗ Verification failed. Embedding was generated but not stored correctly.[/red]"
                )
        else:
            console.print(f"[red]✗ Failed to generate embedding for movie ID {movie_id}[/red]")


@app.callback(invoke_without_command=True)
def debug_main(ctx: typer.Context) -> None:
    """Debug tools for the recommendation system.

    This command group provides diagnostic and debugging tools for the recommendation system,
    allowing you to inspect embeddings, test similarity searches, and verify system functionality.
    """
    if ctx.invoked_subcommand is None:
        console.print("[cyan]Recommendation System Debug Tools[/cyan]")
        console.print("[yellow]Available commands:[/yellow]")
        console.print("  check_embedding    - Check if a movie has an embedding")
        console.print("  similar_movies     - Find movies similar to a specific movie")
        console.print("  compare_movies     - Compare two movies by calculating similarity")
        console.print("  vector_status      - Show status of the vector database")
        console.print("  recreate_embedding - Completely delete and recreate an embedding")
        console.print(
            "\n[yellow]Run 'rec-api debug COMMAND --help' for more information on a command[/yellow]"
        )
