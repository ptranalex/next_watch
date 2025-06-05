"""ML API CLI commands.

This module provides CLI commands for testing the ML API integration.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
import json

import typer
from rich.console import Console
from rich.table import Table

from recommendation_api.services.ml_api_client import get_ml_api_client
from recommendation_api.config import settings, configure_logging

***REMOVED*** Create CLI app
app = typer.Typer(name="ml-api", help="ML API commands")
console = Console()


@app.command("test-connection")
def test_connection(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="ML API URL")
):
    """Test connection to the ML API.

    Args:
        url: Optional URL to override the configured ML_API_URL
    """
    ***REMOVED*** Configure logging
    configure_logging(log_level="INFO", verbose=True)
    logger = logging.getLogger(__name__)

    ***REMOVED*** Initialize client
    client = get_ml_api_client()
    if url:
        client.base_url = url
        logger.info(f"Using ML API URL: {url}")
    else:
        logger.info(f"Using configured ML API URL: {client.base_url}")

    ***REMOVED*** Run the async test
    asyncio.run(_test_connection(client))


async def _test_connection(client: Any):
    """Async implementation of test_connection."""
    console = Console()

    with console.status("[bold green]Testing connection to ML API..."):
        try:
            ***REMOVED*** Get model info
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

        except Exception as e:
            console.print(f"[bold red]✗ Connection failed: {str(e)}[/]")


@app.command("generate-embedding")
def generate_embedding(
    title: str = typer.Argument(..., help="Movie title"),
    overview: str = typer.Argument(..., help="Movie overview/description"),
    genres: str = typer.Option("", "--genres", "-g", help="Comma-separated genres"),
    movie_id: str = typer.Option("test-movie", "--id", help="Movie ID"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="ML API URL"),
):
    """Generate an embedding for a movie.

    Args:
        title: Movie title
        overview: Movie overview/description
        genres: Comma-separated list of genres
        movie_id: Movie ID
        url: Optional URL to override the configured ML_API_URL
    """
    ***REMOVED*** Configure logging
    configure_logging(log_level="INFO", verbose=True)
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

    ***REMOVED*** Run the async test
    asyncio.run(_generate_embedding(client, movie_features))


async def _generate_embedding(client: Any, movie_features: Dict[str, Any]):
    """Async implementation of generate_embedding."""
    console = Console()

    with console.status("[bold green]Generating embedding..."):
        try:
            ***REMOVED*** Generate embedding
            embedding = await client.generate_movie_embedding(movie_features)

            ***REMOVED*** Display success
            console.print("[bold green]✓ Embedding generated successfully![/]")

            ***REMOVED*** Display embedding info
            dimension = len(embedding)
            console.print(f"[cyan]Embedding dimension:[/] [green]{dimension}[/]")

            ***REMOVED*** Display a preview of the embedding vector
            preview = (
                embedding[:5] + ["..."] + embedding[-5:]
                if dimension > 10
                else embedding
            )
            console.print(f"[cyan]Embedding preview:[/] {preview}")

        except Exception as e:
            console.print(f"[bold red]✗ Failed to generate embedding: {str(e)}[/]")


if __name__ == "__main__":
    app()
