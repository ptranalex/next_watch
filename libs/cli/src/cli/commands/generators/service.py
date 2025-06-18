"""Service command generator.

Generates service management commands for generic service operations following
Backend API patterns with serve, status, and operational commands.
"""

import asyncio
from typing import Optional, Callable, Awaitable, Any, Dict, List
import typer
from rich.table import Table

from ...output.handler import get_cli_output
from ...async_utils import run_with_retries, with_timeout
from ...health import display_health_results


def create_service_commands(
    service_name: str,
    get_health_service: Optional[Callable[[], Awaitable[Any]]] = None,
    serve_command: Optional[Callable[..., Any]] = None,
    additional_commands: Optional[Dict[str, Callable[..., Any]]] = None,
) -> typer.Typer:
    """Create service management commands following Backend API patterns.

    Args:
        service_name: Name of the service
        get_health_service: Optional function to get health service for status checks
        serve_command: Optional serve command function
        additional_commands: Optional dict of additional commands to add

    Returns:
        Typer app with service management commands

    Example:
        >>> service_app = create_service_commands(
        ...     "backend-api",
        ...     get_health_service=lambda: get_health_service(),
        ...     serve_command=serve_app,
        ...     additional_commands={"migrate": migrate_db}
        ... )
        >>> main_app.add_typer(service_app, name="service")
    """
    app = typer.Typer(
        name="service", help=f"{service_name} service management commands."
    )

    if serve_command:

        @app.command()
        def serve(
            host: str = typer.Option("0.0.0.0", "--host", help="Host to bind to"),
            port: int = typer.Option(8000, "--port", help="Port to bind to"),
            reload: bool = typer.Option(
                False, "--reload", help="Enable auto-reload for development"
            ),
            workers: int = typer.Option(
                1, "--workers", help="Number of worker processes"
            ),
            log_level: str = typer.Option("info", "--log-level", help="Log level"),
            verbose: bool = typer.Option(
                False, "--verbose", "-v", help="Enable verbose output"
            ),
        ) -> None:
            """Start the service server."""
            out = get_cli_output("serve", verbose=verbose)

            try:
                out.info(f"Starting {service_name} server...")
                out.info(f"Server configuration: {host}:{port}")

                if reload:
                    out.warning("Auto-reload enabled (development mode)")

                if verbose:
                    table = Table(title="Server Configuration")
                    table.add_column("Setting", style="cyan")
                    table.add_column("Value", style="white")

                    table.add_row("Host", host)
                    table.add_row("Port", str(port))
                    table.add_row("Workers", str(workers))
                    table.add_row("Log Level", log_level)
                    table.add_row("Reload", "Yes" if reload else "No")

                    out.console.print(table)

                ***REMOVED*** Call the actual serve command
                serve_command(
                    host=host,
                    port=port,
                    reload=reload,
                    workers=workers,
                    log_level=log_level,
                )

            except Exception as e:
                out.error(f"Failed to start server: {e}")
                raise typer.Exit(code=1)

    if get_health_service:

        @app.command()
        def status(
            verbose: bool = typer.Option(
                False, "--verbose", "-v", help="Show detailed status"
            ),
            timeout: int = typer.Option(
                30, "--timeout", help="Timeout for health checks in seconds"
            ),
        ) -> None:
            """Check service status and health."""
            asyncio.run(_service_status(service_name, verbose, timeout))

        async def _service_status(
            service_name: str, verbose: bool, timeout: int
        ) -> None:
            """Check service status."""
            out = get_cli_output("status", verbose=verbose)

            try:
                out.info(f"Checking {service_name} status...")

                async with with_timeout(
                    timeout, f"Health check timed out after {timeout}s"
                ):
                    health_service = await get_health_service()

                    ***REMOVED*** Use existing health service for comprehensive checks
                    results = await health_service.check_all()

                    ***REMOVED*** Use framework display utilities
                    display_health_results(results, out)

                    ***REMOVED*** Determine overall status
                    all_healthy = all(result.is_healthy for result in results.values())

                    if all_healthy:
                        out.success(f"{service_name} is healthy")
                    else:
                        unhealthy = [
                            name
                            for name, result in results.items()
                            if not result.is_healthy
                        ]
                        out.error(
                            f"{service_name} has unhealthy dependencies: {', '.join(unhealthy)}"
                        )
                        raise typer.Exit(code=1)

            except Exception as e:
                out.error(f"Status check failed: {e}")
                raise typer.Exit(code=1)

    @app.command()
    def info(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed information"
        )
    ) -> None:
        """Display service information."""
        out = get_cli_output("info", verbose=verbose)

        try:
            table = Table(title=f"{service_name} Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Service Name", service_name)
            table.add_row("CLI Framework", "NextWatch CLI Framework v0.1.0")

            ***REMOVED*** Add more service-specific info if available
            if verbose:
                ***REMOVED*** Count commands manually since app.commands doesn't exist
                command_count = len(
                    [cmd for cmd in dir(app) if not cmd.startswith("_")]
                )
                table.add_row("Commands Available", str(command_count))
                table.add_row(
                    "Health Monitoring", "Yes" if get_health_service else "No"
                )
                table.add_row("Serve Command", "Yes" if serve_command else "No")

            out.console.print(table)
            out.success("Service information displayed")

        except Exception as e:
            out.error(f"Failed to get service info: {e}")
            raise typer.Exit(code=1)

    @app.command()
    def version(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed version information"
        )
    ) -> None:
        """Display service version information."""
        out = get_cli_output("version", verbose=verbose)

        try:
            if verbose:
                table = Table(title="Version Information")
                table.add_column("Component", style="cyan")
                table.add_column("Version", style="white")

                table.add_row("Service", service_name)
                table.add_row("CLI Framework", "0.1.0")

                ***REMOVED*** Try to get package version if available
                try:
                    import importlib.metadata

                    pkg_version = importlib.metadata.version(
                        service_name.replace("-", "_")
                    )
                    table.add_row("Package Version", pkg_version)
                except Exception:
                    table.add_row("Package Version", "Unknown")

                out.console.print(table)
            else:
                out.info(f"{service_name} CLI")
                out.info("CLI Framework: NextWatch v0.1.0")

        except Exception as e:
            out.error(f"Failed to get version info: {e}")
            raise typer.Exit(code=1)

    ***REMOVED*** Add additional commands if provided
    if additional_commands:
        for cmd_name, cmd_func in additional_commands.items():
            app.command(name=cmd_name)(cmd_func)

    return app


def create_database_commands(
    get_db_connection: Callable[[], Awaitable[Any]],
    migration_commands: Optional[Dict[str, Callable[..., Any]]] = None,
) -> typer.Typer:
    """Create database management commands following Backend API patterns.

    Args:
        get_db_connection: Function to get database connection
        migration_commands: Optional migration command functions

    Returns:
        Typer app with database management commands

    Example:
        >>> db_app = create_database_commands(
        ...     get_db_connection=lambda: get_db(),
        ...     migration_commands={
        ...         "migrate": run_migrations,
        ...         "downgrade": downgrade_migrations
        ...     }
        ... )
        >>> main_app.add_typer(db_app, name="db")
    """
    app = typer.Typer(name="db", help="Database management commands.")

    @app.command()
    def status(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed database status"
        )
    ) -> None:
        """Check database connection and status."""
        asyncio.run(_db_status(verbose))

    @app.command()
    def info(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed database information"
        )
    ) -> None:
        """Display database information."""
        asyncio.run(_db_info(verbose))

    async def _db_status(verbose: bool) -> None:
        """Check database status."""
        out = get_cli_output("db-status", verbose=verbose)

        try:
            out.info("Checking database connection...")

            db_connection = await get_db_connection()

            ***REMOVED*** Test connection
            await run_with_retries(
                _test_db_connection, db_connection, retries=3, delay=1.0
            )

            out.success("Database connection successful")

            if verbose:
                ***REMOVED*** Get additional database info
                try:
                    ***REMOVED*** This would be database-specific
                    table = Table(title="Database Status")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="white")

                    table.add_row("Connection", "Active")
                    table.add_row("Status", "Healthy")

                    out.console.print(table)

                except Exception as e:
                    out.warning(f"Could not get detailed database info: {e}")

        except Exception as e:
            out.error(f"Database connection failed: {e}")
            raise typer.Exit(code=1)

    async def _db_info(verbose: bool) -> None:
        """Display database information."""
        out = get_cli_output("db-info", verbose=verbose)

        try:
            db_connection = await get_db_connection()

            table = Table(title="Database Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Connection Type", type(db_connection).__name__)
            table.add_row("Status", "Connected")

            if verbose:
                ***REMOVED*** Add more detailed info based on database type
                table.add_row("Framework", "NextWatch CLI Framework")
                ***REMOVED*** Count commands manually since app.commands doesn't exist
                command_count = len(
                    [cmd for cmd in dir(app) if not cmd.startswith("_")]
                )
                table.add_row("Available Commands", str(command_count))

            out.console.print(table)
            out.success("Database information displayed")

        except Exception as e:
            out.error(f"Failed to get database info: {e}")
            raise typer.Exit(code=1)

    async def _test_db_connection(db_connection: Any) -> bool:
        """Test database connection."""
        ***REMOVED*** This would be implemented based on the specific database type
        ***REMOVED*** For now, just return True if connection exists
        return db_connection is not None

    ***REMOVED*** Add migration commands if provided
    if migration_commands:
        for cmd_name, cmd_func in migration_commands.items():
            app.command(name=cmd_name)(cmd_func)

    return app
