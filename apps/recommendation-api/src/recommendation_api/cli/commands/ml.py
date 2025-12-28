"""ML API commands for the Recommendation API.

This module provides CLI commands for working with the ML API, including
testing connectivity and generating embeddings for movies.
"""

import asyncio
import json
import logging
import sys
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typer import Typer

from recommendation_api.config import configure_logging, settings
from recommendation_api.services.ml_api_client import get_ml_api_client

***REMOVED*** Create CLI app
app: Typer = typer.Typer(name="ml", help="ML API commands and utilities")
console = Console()


@app.command("test-connection")
def test_connection(
    url: str | None = typer.Option(None, "--url", "-u", help="ML API URL"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most console output"),
) -> None:
    """Test connection to the ML API.

    This command attempts to connect to the ML API and retrieve model information.
    It displays the connection status and model details if successful.

    Args:
        url: Optional URL to override the configured ML_API_URL
        verbose: Show additional debug information
        quiet: Suppress console output except errors
    """
    ***REMOVED*** Configure logging
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "WARNING"

    configure_logging(log_level=log_level, verbose=verbose)
    logger = logging.getLogger(__name__)

    ***REMOVED*** Initialize client
    client = get_ml_api_client()
    if url:
        client.base_url = url
        logger.info(f"Using ML API URL: {url}")
    else:
        logger.info(f"Using configured ML API URL: {client.base_url}")

    if not quiet:
        console.print(f"[cyan]Testing connection to ML API at {client.base_url}...[/cyan]")

    ***REMOVED*** Run the async test
    try:
        asyncio.run(_test_connection(client, verbose=verbose, quiet=quiet))
    except Exception as e:
        logger.error(f"Error during connection test: {str(e)}")
        console.print(f"[bold red]✗ Connection test failed: {str(e)}[/bold red]")

        if verbose:
            console.print("\n[yellow]Troubleshooting tips:[/yellow]")
            console.print("1. Check if the ML service is running")
            console.print("2. Verify network connectivity")
            console.print(
                f"3. Check ML_API_URL environment variable (current: {settings.ml_api_url})"
            )
            console.print("4. Check server logs for more details")

        sys.exit(1)


async def _test_connection(client: Any, verbose: bool = False, quiet: bool = False) -> None:
    """Async implementation of test_connection."""
    try:
        ***REMOVED*** Skip status display in quiet mode
        if quiet:
            model_info = await client.get_model_info()
        else:
            with console.status("[bold green]Testing connection to ML API..."):
                model_info = await client.get_model_info()

                ***REMOVED*** Display success
                console.print("[bold green]✓ Connection successful![/]")

                ***REMOVED*** Display model info
                table = Table(title="ML API Model Information")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                for key, value in model_info.items():
                    table.add_row(key, str(value))

                console.print(table)

                if verbose:
                    console.print(
                        Panel(
                            "The connection to the ML API is working correctly.\n"
                            "You can now use other ML API commands such as 'generate-embedding'.",
                            title="Connection Details",
                            border_style="green",
                        )
                    )

    except Exception as e:
        if not quiet:
            console.print(f"[bold red]✗ Connection failed: {str(e)}[/]")
        raise


@app.command("generate-embedding")
def generate_embedding(
    title: str = typer.Argument(..., help="Movie title"),
    overview: str = typer.Argument(..., help="Movie overview/description"),
    genres: str = typer.Option("", "--genres", "-g", help="Comma-separated genres"),
    movie_id: str = typer.Option("test-movie", "--id", help="Movie ID"),
    url: str | None = typer.Option(None, "--url", "-u", help="ML API URL"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most console output"),
) -> None:
    """Generate an embedding for a movie.

    This command sends movie information to the ML API and generates a vector embedding.
    The embedding can be used for similarity search and recommendations.

    Args:
        title: Movie title
        overview: Movie overview/description
        genres: Comma-separated list of genres
        movie_id: Movie ID
        url: Optional URL to override the configured ML_API_URL
        verbose: Show detailed information
        quiet: Suppress console output except errors
    """
    ***REMOVED*** Configure logging
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "WARNING"

    configure_logging(log_level=log_level, verbose=verbose)
    logger = logging.getLogger(__name__)

    ***REMOVED*** Initialize client
    client = get_ml_api_client()
    if url:
        client.base_url = url
        logger.info(f"Using ML API URL: {url}")
    else:
        logger.info(f"Using configured ML API URL: {client.base_url}")

    ***REMOVED*** Process genres
    genre_list = [g.strip() for g in genres.split(",")] if genres else []

    ***REMOVED*** Create movie features
    movie_features = {
        "movie_id": movie_id,
        "title": title,
        "overview": overview,
        "genres": genre_list,
        "additional_metadata": {"source": "cli-test"},
    }

    if not quiet:
        console.print(f"[cyan]Generating embedding for movie: {title}[/cyan]")
        if verbose:
            console.print(f"Movie details: {json.dumps(movie_features, indent=2)}")

    ***REMOVED*** Run the async test
    try:
        asyncio.run(_generate_embedding(client, movie_features, verbose=verbose, quiet=quiet))
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        console.print(f"[bold red]✗ Failed to generate embedding: {str(e)}[/bold red]")

        if verbose:
            console.print("\n[yellow]Troubleshooting tips:[/yellow]")
            console.print("1. Check if the ML service is running")
            console.print("2. Ensure the movie data is valid")
            console.print("3. Try with a shorter overview text")
            console.print("4. Check server logs for more details")

        sys.exit(1)


async def _generate_embedding(
    client: Any,
    movie_features: dict[str, Any],
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    """Async implementation of generate_embedding."""
    try:
        if quiet:
            embedding = await client.generate_movie_embedding(movie_features)
        else:
            with console.status("[bold green]Generating embedding..."):
                embedding = await client.generate_movie_embedding(movie_features)

                ***REMOVED*** Display success
                console.print("[bold green]✓ Embedding generated successfully![/]")

                ***REMOVED*** Display embedding info
                dimension = len(embedding)
                console.print(f"[cyan]Embedding dimension:[/] [green]{dimension}[/]")

                ***REMOVED*** Display a preview of the embedding vector
                if verbose:
                    preview = (
                        embedding[:5] + ["..."] + embedding[-5:] if dimension > 10 else embedding
                    )
                    console.print(f"[cyan]Embedding preview:[/] {preview}")

                    console.print(
                        Panel(
                            f"The embedding vector has {dimension} dimensions and can be used for similarity search.",
                            title="Embedding Details",
                            border_style="green",
                        )
                    )

    except Exception as e:
        if not quiet:
            console.print(f"[bold red]✗ Failed to generate embedding: {str(e)}[/]")
        raise


@app.callback(invoke_without_command=True)
def ml_callback(ctx: typer.Context) -> None:
    """ML API commands for the Recommendation API.

    These commands allow you to interact with the ML API service,
    test connectivity, and generate embeddings for movies.
    """
    ***REMOVED*** When no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        console.print(
            "[yellow]No ML command specified. Use --help to see available commands.[/yellow]"
        )
        ctx.invoke(app, ["--help"])
