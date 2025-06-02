"""Health check commands for the Recommendation API CLI."""

import asyncio
import logging
from typing import Dict, Any
import typer
from rich.console import Console

from recommendation_api.config.app import settings
from recommendation_api.cli.utils import check_service_health, display_service_status, print_error

app = typer.Typer(
    name="health",
    help="Health check commands",
)

console = Console()
logger = logging.getLogger(__name__)


@app.command()
def check() -> None:
    """Check the health of the Recommendation API and its dependencies."""
    try:
        ***REMOVED*** Define services to check
        services = {
            "Recommendation API": {
                "url": f"http://{settings.host}:{settings.port}",
                "status": "Unknown",
                "response_time": "N/A",
            },
            "Database": {
                "url": settings.database_url,
                "status": "Unknown",
                "response_time": "N/A",
            },
            "Qdrant": {
                "url": settings.qdrant_url,
                "status": "Unknown",
                "response_time": "N/A",
            },
        }

        ***REMOVED*** Check each service
        async def check_services():
            for service_name, info in services.items():
                is_healthy = await check_service_health(
                    info["url"],
                    service_name,
                    timeout=5,
                    console=console,
                )
                info["status"] = "Healthy" if is_healthy else "Unhealthy"

        ***REMOVED*** Run health checks
        asyncio.run(check_services())

        ***REMOVED*** Display results
        display_service_status(services, console)

    except Exception as e:
        print_error(f"Failed to check service health: {str(e)}", console)
        raise typer.Exit(code=1)


@app.command()
def ping(
    service: str = typer.Argument(
        ...,
        help="Service to ping (api, db, qdrant)",
    ),
) -> None:
    """Ping a specific service.

    Args:
        service: Service to ping
    """
    try:
        ***REMOVED*** Map service names to URLs
        service_urls = {
            "api": f"http://{settings.host}:{settings.port}",
            "db": settings.database_url,
            "qdrant": settings.qdrant_url,
        }

        if service not in service_urls:
            console.print(f"[red]❌ Unknown service: {service}[/red]")
            console.print("Available services: api, db, qdrant")
            raise typer.Exit(code=1)
    
        ***REMOVED*** Check service health
        is_healthy = asyncio.run(
            check_service_health(
                service_urls[service],
                service.upper(),
                timeout=5,
                console=console,
            )
        )

        if not is_healthy:
            raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Failed to ping service: {str(e)}", console)
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def health_main(ctx: typer.Context) -> None:
    """Health check commands."""
    if ctx.invoked_subcommand is None:
        check() 