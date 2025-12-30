"""Health check commands for Auth API services."""

import asyncio
import logging
import time
from typing import Any

import typer
from rich.console import Console
from sqlalchemy.exc import SQLAlchemyError

from auth_api.cli.utils import check_service_health, display_service_status
from auth_api.config.app import settings

app = typer.Typer(name="health", help="Health check commands for Auth API and dependent services.")
console = Console()
logger = logging.getLogger(__name__)


@app.command(name="check")
def health_check(
    auth_api_url: str | None = typer.Option(
        None,
        "--auth-api-url",
        help="Auth API URL to check (overrides config)",
        envvar="AUTH_API_URL",
    ),
    backend_api_url: str | None = typer.Option(
        None,
        "--backend-api-url",
        help="Backend API URL to check",
        envvar="BACKEND_API_URL",
    ),
    timeout: int = typer.Option(
        5,
        "--timeout",
        "-t",
        help="Request timeout in seconds",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Check health of Auth API and dependent services.

    This command checks the health of:
    - Auth API service (self)
    - Backend API service (if URL provided)
    - Database connection

    Args:
        auth_api_url: Auth API URL to check
        backend_api_url: Backend API URL to check
        timeout: Request timeout in seconds
        verbose: Show detailed output including response times
    """
    if verbose:
        console.print("[blue]🔍 Starting comprehensive health check...[/blue]")
        console.print()

    # Use provided URLs or construct from config
    auth_url = auth_api_url or f"http://localhost:{settings.port}"

    # Run async health checks
    asyncio.run(
        _run_health_checks(
            auth_url=auth_url,
            backend_url=backend_api_url,
            timeout=timeout,
            verbose=verbose,
        )
    )


@app.command(name="self")
def check_self(
    url: str | None = typer.Option(
        None,
        "--url",
        help="Auth API URL (overrides config)",
        envvar="AUTH_API_URL",
    ),
    timeout: int = typer.Option(
        5,
        "--timeout",
        "-t",
        help="Request timeout in seconds",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Check health of Auth API service only.

    Args:
        url: Auth API URL to check
        timeout: Request timeout in seconds
        verbose: Show detailed output
    """
    auth_url = url or f"http://localhost:{settings.port}"

    if verbose:
        console.print(f"[blue]Checking Auth API at: {auth_url}[/blue]")

    asyncio.run(_check_single_service(auth_url, "Auth API", timeout))


@app.command(name="database")
def check_database(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Check database connection health.

    Args:
        verbose: Show detailed output
    """
    if verbose:
        console.print("[blue]Checking database connection...[/blue]")

    asyncio.run(_check_database_health(verbose))


async def _run_health_checks(
    auth_url: str,
    backend_url: str | None,
    timeout: int,
    verbose: bool,
) -> None:
    """Run comprehensive health checks for all services.

    Args:
        auth_url: Auth API URL
        backend_url: Backend API URL (optional)
        timeout: Request timeout in seconds
        verbose: Show detailed output
    """
    services: dict[str, dict[str, Any]] = {}

    # Check Auth API (self)
    start_time = time.time()
    auth_healthy = await check_service_health(auth_url, "Auth API", timeout, console)
    auth_time = round((time.time() - start_time) * 1000, 2)

    services["Auth API"] = {
        "status": "Healthy" if auth_healthy else "Unhealthy",
        "url": auth_url,
        "response_time": f"{auth_time}ms" if auth_healthy else "N/A",
    }

    # Check Backend API if URL provided
    if backend_url:
        start_time = time.time()
        backend_healthy = await check_service_health(backend_url, "Backend API", timeout, console)
        backend_time = round((time.time() - start_time) * 1000, 2)

        services["Backend API"] = {
            "status": "Healthy" if backend_healthy else "Unhealthy",
            "url": backend_url,
            "response_time": f"{backend_time}ms" if backend_healthy else "N/A",
        }

    # Check Database
    start_time = time.time()
    db_healthy = await _check_database_health(verbose=False)
    db_time = round((time.time() - start_time) * 1000, 2)

    services["Database"] = {
        "status": "Healthy" if db_healthy else "Unhealthy",
        "url": _mask_db_url(settings.database_url),
        "response_time": f"{db_time}ms" if db_healthy else "N/A",
    }

    console.print()
    display_service_status(services, console)

    # Overall status
    all_healthy = all(service["status"] == "Healthy" for service in services.values())

    if all_healthy:
        console.print("[bold green]🎉 All services are healthy![/bold green]")
        exit_code = 0
    else:
        console.print("[bold red]⚠️  Some services are unhealthy![/bold red]")
        exit_code = 1

    if verbose:
        console.print(f"\n[dim]Health check completed with exit code: {exit_code}[/dim]")

    raise typer.Exit(code=exit_code)


async def _check_single_service(url: str, service_name: str, timeout: int) -> None:
    """Check health of a single service.

    Args:
        url: Service URL
        service_name: Human-readable service name
        timeout: Request timeout in seconds
    """
    healthy = await check_service_health(url, service_name, timeout, console)

    if healthy:
        console.print(f"[bold green]✅ {service_name} is healthy![/bold green]")
        raise typer.Exit(code=0)
    else:
        console.print(f"[bold red]❌ {service_name} is unhealthy![/bold red]")
        raise typer.Exit(code=1)


async def _check_database_health(verbose: bool = False) -> bool:
    """Check database connection health.

    Args:
        verbose: Show detailed output

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        from sqlalchemy import create_engine, text

        # Create engine with connection timeout
        engine = create_engine(
            settings.database_url,
            pool_timeout=5,
            pool_recycle=300,
        )

        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

        if verbose:
            console.print("✅ Database is healthy: Connection successful")
        else:
            console.print("✅ Database is healthy: Connection successful")

        return True

    except SQLAlchemyError as e:
        console.print(f"❌ Database is unhealthy: {e}")
        logger.error(f"Database health check failed: {e}")
        return False
    except Exception as e:
        console.print(f"❌ Database connection error: {e}")
        logger.error(f"Unexpected database error: {e}")
        return False


def _mask_db_url(database_url: str) -> str:
    """Mask password in database URL for display.

    Args:
        database_url: Database connection URL

    Returns:
        Masked URL string
    """
    if not database_url:
        return "Not configured"

    # Handle PostgreSQL URLs like postgresql://user:pass@host:port/db
    if "://" in database_url and "@" in database_url:
        try:
            protocol_part, rest = database_url.split("://", 1)
            if "@" in rest:
                auth_part, host_part = rest.split("@", 1)
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                    return f"{protocol_part}://{username}:****@{host_part}"
        except (IndexError, ValueError):
            pass

    return database_url
