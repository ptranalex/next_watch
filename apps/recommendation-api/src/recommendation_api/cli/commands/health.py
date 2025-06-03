"""Health check commands for the Recommendation API CLI."""

import asyncio
import logging
from typing import Dict, Any
import typer
from rich.console import Console
from rich.table import Table
import asyncpg ***REMOVED*** type: ignore
from qdrant_client import QdrantClient
from qdrant_client.http import models

from recommendation_api.config.app import settings
from recommendation_api.cli.utils import check_service_health, display_service_status, print_error
from recommendation_api.config.logging import configure_logging

app = typer.Typer(
    name="health",
    help="Health check commands",
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False, quiet: bool = False):
    """Configure logging for health commands.
    
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


async def check_database_health() -> bool:
    """Check database health by attempting to connect and execute a simple query.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        conn = await asyncpg.connect(settings.database_url)
        await conn.execute('SELECT 1')
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_qdrant_health() -> bool:
    """Check Qdrant health by attempting to connect and get collections.
    
    Returns:
        bool: True if Qdrant is healthy, False otherwise
    """
    try:
        client = QdrantClient(url=settings.qdrant_url)
        collections = client.get_collections()
        return True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return False


@app.command()
def check(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed health information",
    ),
    quiet: bool = typer.Option(
        False, 
        "--quiet", 
        "-q", 
        help="Suppress most log output"
    ),
) -> None:
    """Check the health of the Recommendation API and its dependencies.
    
    Args:
        verbose: Show detailed health information
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)
    
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

        console.print("[cyan]Checking health of services...[/cyan]")
        
        ***REMOVED*** Check each service
        async def check_services():
            ***REMOVED*** Check Recommendation API
            is_healthy = await check_service_health(
                services["Recommendation API"]["url"],
                "Recommendation API",
                timeout=5,
                console=console,
            )
            services["Recommendation API"]["status"] = "Healthy" if is_healthy else "Unhealthy"

            ***REMOVED*** Check Database
            is_healthy = await check_database_health()
            services["Database"]["status"] = "Healthy" if is_healthy else "Unhealthy"
            if is_healthy:
                console.print("✅ Database is healthy")
            else:
                console.print("❌ Database is unhealthy")

            ***REMOVED*** Check Qdrant
            is_healthy = await check_qdrant_health()
            services["Qdrant"]["status"] = "Healthy" if is_healthy else "Unhealthy"
            if is_healthy:
                console.print("✅ Qdrant is healthy")
            else:
                console.print("❌ Qdrant is unhealthy")

        ***REMOVED*** Run health checks
        asyncio.run(check_services())

        ***REMOVED*** Display results
        display_service_status(services, console)
        
        ***REMOVED*** Check overall health
        all_healthy = all(service["status"] == "Healthy" for service in services.values())
        
        if all_healthy:
            console.print("\n[green]✅ All services are healthy[/green]")
        else:
            unhealthy_services = [name for name, info in services.items() if info["status"] != "Healthy"]
            console.print(f"\n[red]❌ Unhealthy services: {', '.join(unhealthy_services)}[/red]")
            
            if verbose:
                console.print("\n[yellow]Troubleshooting tips:[/yellow]")
                if "Database" in unhealthy_services:
                    console.print("- Check if PostgreSQL is running and accessible")
                    console.print("- Verify database credentials and connection string")
                if "Qdrant" in unhealthy_services:
                    console.print("- Check if Qdrant server is running and accessible")
                    console.print("- Verify Qdrant URL configuration")
                if "Recommendation API" in unhealthy_services:
                    console.print("- Check if the API server is running")
                    console.print("- Try starting the server with 'rec-api serve start'")

    except Exception as e:
        print_error(f"Failed to check service health: {str(e)}", console)
        if verbose:
            logger.exception("Health check error")
        raise typer.Exit(code=1)


@app.command()
def ping(
    service: str = typer.Argument(
        ...,
        help="Service to ping (api, db, qdrant)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed ping information",
    ),
    quiet: bool = typer.Option(
        False, 
        "--quiet", 
        "-q", 
        help="Suppress most log output"
    ),
) -> None:
    """Ping a specific service.

    Args:
        service: Service to ping (api, db, qdrant)
        verbose: Show detailed ping information
        quiet: Suppress most log output
    """
    ***REMOVED*** Configure logging
    setup_logging(verbose=verbose, quiet=quiet)
    
    try:
        console.print(f"[cyan]Pinging {service} service...[/cyan]")
        
        if service == "api":
            is_healthy = asyncio.run(
                check_service_health(
                    f"http://{settings.host}:{settings.port}",
                    "API",
                    timeout=5,
                    console=console,
                )
            )
        elif service == "db":
            is_healthy = asyncio.run(check_database_health())
            if is_healthy:
                console.print("✅ Database is healthy")
            else:
                console.print("❌ Database is unhealthy")
        elif service == "qdrant":
            is_healthy = asyncio.run(check_qdrant_health())
            if is_healthy:
                console.print("✅ Qdrant is healthy")
            else:
                console.print("❌ Qdrant is unhealthy")
        else:
            console.print(f"[red]❌ Unknown service: {service}[/red]")
            console.print("[yellow]Available services: api, db, qdrant[/yellow]")
            raise typer.Exit(code=1)

        ***REMOVED*** Show summary
        if is_healthy:
            console.print(f"[green]✅ {service.upper()} service is healthy[/green]")
        else:
            console.print(f"[red]❌ {service.upper()} service is unhealthy[/red]")
            
            if verbose:
                console.print("\n[yellow]Troubleshooting tips:[/yellow]")
                if service == "db":
                    console.print("- Check if PostgreSQL is running and accessible")
                    console.print("- Verify database credentials and connection string")
                elif service == "qdrant":
                    console.print("- Check if Qdrant server is running and accessible")
                    console.print("- Verify Qdrant URL configuration")
                elif service == "api":
                    console.print("- Check if the API server is running")
                    console.print("- Try starting the server with 'rec-api serve start'")
            
            raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Failed to ping {service} service: {str(e)}", console)
        if verbose:
            logger.exception(f"Ping {service} error")
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def health_main(ctx: typer.Context) -> None:
    """Health check commands.
    
    This command group provides tools for checking the health of the Recommendation API
    and its dependencies.
    """
    if ctx.invoked_subcommand is None:
        check() 