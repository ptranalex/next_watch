"""Health check commands for BFF API services."""

import asyncio
import logging
import time
from typing import Dict, Any, Optional

import typer
from rich.console import Console

from bff_api.config.app import settings
from bff_api.cli.utils import check_service_health, display_service_status

app = typer.Typer(
    name="health", help="Health check commands for BFF and dependent services."
)
console = Console()
logger = logging.getLogger(__name__)


@app.command(name="check")
def health_check(
    backend_api_url: Optional[str] = typer.Option(
        None,
        "--backend-api-url",
        help="Backend API URL to check (overrides config)",
        envvar="BACKEND_API_URL",
    ),
    auth_api_url: Optional[str] = typer.Option(
        None,
        "--auth-api-url",
        help="Auth API URL to check (overrides config)",
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
    """Check health of BFF and all dependent services.

    This command checks the health of:
    - Backend API service
    - Auth API service
    - Redis cache (if configured)

    Args:
        backend_api_url: Backend API URL to check
        auth_api_url: Auth API URL to check
        timeout: Request timeout in seconds
        verbose: Show detailed output including response times
    """
    if verbose:
        console.print("[blue]🔍 Starting comprehensive health check...[/blue]")
        console.print()

    ***REMOVED*** Use provided URLs or fall back to configuration
    backend_url = backend_api_url or settings.backend_api_url
    auth_url = auth_api_url or settings.auth_api_url

    ***REMOVED*** Run async health checks
    asyncio.run(
        _run_health_checks(
            backend_url=backend_url,
            auth_url=auth_url,
            timeout=timeout,
            verbose=verbose,
        )
    )


@app.command(name="backend")
def check_backend(
    url: Optional[str] = typer.Option(
        None,
        "--url",
        help="Backend API URL (overrides config)",
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
    """Check health of Backend API service only.

    Args:
        url: Backend API URL to check
        timeout: Request timeout in seconds
        verbose: Show detailed output
    """
    backend_url = url or settings.backend_api_url

    if verbose:
        console.print(f"[blue]Checking Backend API at: {backend_url}[/blue]")

    asyncio.run(_check_single_service(backend_url, "Backend API", timeout))


@app.command(name="auth")
def check_auth(
    url: Optional[str] = typer.Option(
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
    auth_url = url or settings.auth_api_url

    if verbose:
        console.print(f"[blue]Checking Auth API at: {auth_url}[/blue]")

    asyncio.run(_check_single_service(auth_url, "Auth API", timeout))


async def _run_health_checks(
    backend_url: str,
    auth_url: str,
    timeout: int,
    verbose: bool,
) -> None:
    """Run comprehensive health checks for all services.

    Args:
        backend_url: Backend API URL
        auth_url: Auth API URL
        timeout: Request timeout in seconds
        verbose: Show detailed output
    """
    services: Dict[str, Dict[str, Any]] = {}

    ***REMOVED*** Check Backend API
    start_time = time.time()
    backend_healthy = await check_service_health(
        backend_url, "Backend API", timeout, console
    )
    backend_time = round((time.time() - start_time) * 1000, 2)

    services["Backend API"] = {
        "status": "Healthy" if backend_healthy else "Unhealthy",
        "url": backend_url,
        "response_time": f"{backend_time}ms" if backend_healthy else "N/A",
    }

    ***REMOVED*** Check Auth API
    start_time = time.time()
    auth_healthy = await check_service_health(auth_url, "Auth API", timeout, console)
    auth_time = round((time.time() - start_time) * 1000, 2)

    services["Auth API"] = {
        "status": "Healthy" if auth_healthy else "Unhealthy",
        "url": auth_url,
        "response_time": f"{auth_time}ms" if auth_healthy else "N/A",
    }

    ***REMOVED*** Check Redis (basic connection test)
    start_time = time.time()
    redis_healthy = await _check_redis_health()
    redis_time = round((time.time() - start_time) * 1000, 2)

    services["Redis Cache"] = {
        "status": "Healthy" if redis_healthy else "Unhealthy",
        "url": settings.redis_url,
        "response_time": f"{redis_time}ms" if redis_healthy else "N/A",
    }

    console.print()
    display_service_status(services, console)

    ***REMOVED*** Overall status
    all_healthy = all(service["status"] == "Healthy" for service in services.values())

    if all_healthy:
        console.print("[bold green]🎉 All services are healthy![/bold green]")
        exit_code = 0
    else:
        console.print("[bold red]⚠️  Some services are unhealthy![/bold red]")
        exit_code = 1

    if verbose:
        console.print(
            f"\n[dim]Health check completed with exit code: {exit_code}[/dim]"
        )

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


async def _check_redis_health() -> bool:
    """Check Redis connection health.

    Returns:
        True if Redis is accessible, False otherwise
    """
    try:
        import redis.asyncio as redis

        client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

        ***REMOVED*** Simple ping test
        await client.ping()
        await client.close()

        console.print("✅ Redis Cache is healthy: Connection successful")
        return True

    except Exception as e:
        console.print(f"❌ Redis Cache is unhealthy: {e}")
        logger.error(f"Redis health check failed: {e}")
        return False
