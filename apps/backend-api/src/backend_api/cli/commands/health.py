"""Health check commands for the Backend API CLI."""

import logging
from typing import Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table
from typer import Typer

from backend_api.config.app import settings
from backend_api.config.logging import configure_logging, get_logger

app = typer.Typer(
    name="health",
    help="Health check commands for Backend API and dependent services.",
    add_completion=False,
)

console = Console()
logger = logging.getLogger("backend_api.cli.commands.health")


@app.command(name="check")
def check_health(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    timeout: float = typer.Option(5.0, "--timeout", "-t", help="Request timeout in seconds"),
) -> None:
    """Check the health of the backend API service.

    Args:
        verbose: Show detailed output including response data
        timeout: Timeout for health check requests in seconds
    """
    ***REMOVED*** Configure minimal logging for health check
    configure_logging(log_level="ERROR", quiet=not verbose)
    logger = get_logger(__name__)

    port = getattr(settings, "api_port", 8000)
    url = f"http://localhost:{port}/health"

    try:
        if verbose:
            console.print(f"🔍 Checking backend API health at {url}")

        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()

        data = response.json()

        if verbose:
            ***REMOVED*** Create a table for the detailed health information
            table = Table(title="Backend API Health Status")
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details", style="yellow")

            for service, info in data.items():
                if isinstance(info, dict):
                    status = "✅ Healthy" if info.get("status") == "ok" else "❌ Unhealthy"
                    details = str(info.get("details", ""))
                    table.add_row(service, status, details)
                else:
                    status = "✅ Healthy" if info == "ok" else "❌ Unhealthy"
                    table.add_row(service, status, "")

            console.print(table)
        else:
            console.print("✅ Backend API is healthy")

        if verbose:
            logger.info(f"Health check successful: {data}")

    except httpx.RequestError as e:
        error_msg = f"❌ Failed to connect to backend API: {e}"
        console.print(error_msg, style="bold red")
        logger.error(error_msg)
        raise typer.Exit(1)
    except httpx.HTTPStatusError as e:
        error_msg = f"❌ Backend API returned error: {e}"
        console.print(error_msg, style="bold red")
        logger.error(error_msg)
        raise typer.Exit(1)


@app.command(name="redis")
def check_redis_health(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    timeout: float = typer.Option(5.0, "--timeout", "-t", help="Request timeout in seconds"),
) -> None:
    """Check the health of the Redis service.

    Args:
        verbose: Show detailed output
        timeout: Timeout for health check requests in seconds
    """
    import redis
    from redis.exceptions import RedisError

    ***REMOVED*** Configure minimal logging
    configure_logging(log_level="ERROR", quiet=not verbose)
    logger = get_logger(__name__)

    redis_url = getattr(settings, "redis_url", "redis://localhost:6379/0")

    try:
        if verbose:
            console.print(f"🔍 Checking Redis health at {redis_url}")

        ***REMOVED*** Create a Redis client with the specified timeout
        redis_client = redis.from_url(redis_url, socket_timeout=timeout)

        ***REMOVED*** Simple ping to check connectivity
        response = redis_client.ping()

        if response:
            if verbose:
                ***REMOVED*** Get more info
                info = redis_client.info()

                table = Table(title="Redis Health Status")
                table.add_column("Attribute", style="cyan")
                table.add_column("Value", style="green")

                ***REMOVED*** Add key redis info
                table.add_row("Status", "✅ Healthy")
                table.add_row("Version", info.get("redis_version", "Unknown"))
                table.add_row("Mode", info.get("redis_mode", "Unknown"))
                table.add_row("OS", info.get("os", "Unknown"))
                table.add_row("Uptime", f"{info.get('uptime_in_days', 0)} days")
                table.add_row("Connected clients", str(info.get("connected_clients", 0)))
                table.add_row("Memory used", f"{info.get('used_memory_human', 'Unknown')}")

                console.print(table)
            else:
                console.print("✅ Redis is healthy")
        else:
            console.print("❌ Redis ping failed", style="bold red")
            raise typer.Exit(1)

    except RedisError as e:
        error_msg = f"❌ Redis error: {str(e)}"
        console.print(error_msg, style="bold red")
        logger.error(error_msg)
        raise typer.Exit(1)
    except Exception as e:
        error_msg = f"❌ Error checking Redis health: {str(e)}"
        console.print(error_msg, style="bold red")
        logger.error(error_msg)
        raise typer.Exit(1)


@app.command(name="db")
def check_db_health(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    timeout: float = typer.Option(5.0, "--timeout", "-t", help="Request timeout in seconds"),
) -> None:
    """Check the health of the database service.

    Args:
        verbose: Show detailed output
        timeout: Timeout for health check in seconds
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError

    ***REMOVED*** Configure minimal logging
    configure_logging(log_level="ERROR", quiet=not verbose)
    logger = get_logger(__name__)

    ***REMOVED*** Get database URL from settings
    db_url = getattr(settings, "database_url", "")

    if not db_url:
        console.print("❌ Database URL not configured", style="bold red")
        raise typer.Exit(1)

    try:
        if verbose:
            ***REMOVED*** Mask password in URL for display
            display_url = db_url
            if "@" in db_url:
                parts = db_url.split("@")
                auth_part = parts[0]
                host_part = parts[1]

                if ":" in auth_part:
                    protocol_user, _ = auth_part.rsplit(":", 1)
                    display_url = f"{protocol_user}:****@{host_part}"

            console.print(f"🔍 Checking database health at {display_url}")

        ***REMOVED*** Create engine with timeout
        engine = create_engine(db_url, connect_args={"connect_timeout": timeout})

        ***REMOVED*** Try simple query to test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

        if verbose:
            ***REMOVED*** Get database info
            with engine.connect() as conn:
                db_info = conn.execute(text("SELECT version()")).scalar()

            table = Table(title="Database Health Status")
            table.add_column("Attribute", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Status", "✅ Healthy")
            table.add_row("Version", str(db_info))

            console.print(table)
        else:
            console.print("✅ Database is healthy")

    except SQLAlchemyError as e:
        error_msg = f"❌ Database error: {str(e)}"
        console.print(error_msg, style="bold red")
        logger.error(error_msg)
        raise typer.Exit(1)
    except Exception as e:
        error_msg = f"❌ Error checking database health: {str(e)}"
        console.print(error_msg, style="bold red")
        logger.error(error_msg)
        raise typer.Exit(1)


***REMOVED*** Default command - alias to check
@app.callback(invoke_without_command=True)
def health(ctx: typer.Context) -> None:
    """Check the health of all services."""
    if ctx.invoked_subcommand is None:
        check_health()
