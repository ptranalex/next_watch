"""Database command generator.

Generates database management commands following Backend API patterns with
status, info, migration, and connection management functionality.
"""

import asyncio
from typing import Optional, Callable, Awaitable, Any, Dict, Union
import typer
from rich.table import Table

from ...output.handler import get_cli_output
from ...async_utils import run_with_retries


def create_database_commands(
    get_db_connection: Callable[[], Awaitable[Any]],
    migration_commands: Optional[Dict[str, Callable[..., Any]]] = None,
    command_name: str = "db",
) -> typer.Typer:
    """Create database management commands following Backend API patterns.

    Args:
        get_db_connection: Function to get database connection
        migration_commands: Optional migration command functions
        command_name: Name for the command group

    Returns:
        Typer app with database management commands

    Example:
        >>> db_app = create_database_commands(
        ...     get_db_connection=lambda: get_db(),
        ...     migration_commands={
        ...         "migrate": run_migrations,
        ...         "downgrade": downgrade_migrations,
        ...         "init": init_database
        ...     }
        ... )
        >>> main_app.add_typer(db_app, name="db")
    """
    app = typer.Typer(name=command_name, help="Database management commands.")

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

    @app.command()
    def test_connection(
        retries: int = typer.Option(
            3, "--retries", help="Number of connection retry attempts"
        ),
        delay: float = typer.Option(
            1.0, "--delay", help="Delay between retries in seconds"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed output"
        ),
    ) -> None:
        """Test database connection with retry logic."""
        asyncio.run(_test_connection(retries, delay, verbose))

    async def _db_status(verbose: bool) -> None:
        """Check database status."""
        out = get_cli_output("db-status", verbose=verbose)

        try:
            out.info("Checking database connection...")

            db_connection = await get_db_connection()

            ***REMOVED*** Test connection with retries
            await run_with_retries(
                _test_db_connection, db_connection, retries=3, delay=1.0
            )

            out.success("Database connection successful")

            if verbose:
                ***REMOVED*** Get additional database info
                try:
                    table = Table(title="Database Status")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="white")

                    table.add_row("Connection", "Active")
                    table.add_row("Status", "Healthy")
                    table.add_row("Connection Type", type(db_connection).__name__)

                    ***REMOVED*** Try to get database-specific info
                    if hasattr(db_connection, "info"):
                        ***REMOVED*** PostgreSQL-style info
                        try:
                            info = await db_connection.info()
                            if "version" in info:
                                table.add_row("Database Version", info["version"])
                        except Exception:
                            pass

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
                ***REMOVED*** Count available commands
                command_count = len(
                    [cmd for cmd in dir(app) if cmd.startswith("command")]
                )
                table.add_row("Available Commands", str(command_count))

                ***REMOVED*** Try to get connection details
                if hasattr(db_connection, "get_dsn_parameters"):
                    ***REMOVED*** PostgreSQL asyncpg connection
                    try:
                        params = db_connection.get_dsn_parameters()
                        table.add_row("Host", params.get("host", "Unknown"))
                        table.add_row("Port", params.get("port", "Unknown"))
                        table.add_row("Database", params.get("dbname", "Unknown"))
                        table.add_row("User", params.get("user", "Unknown"))
                    except Exception:
                        pass
                elif hasattr(db_connection, "connection"):
                    ***REMOVED*** SQLAlchemy-style connection
                    try:
                        url = str(db_connection.connection.engine.url)
                        ***REMOVED*** Mask password in URL
                        if "@" in url:
                            masked_url = (
                                url.split("://")[0] + "://***:***@" + url.split("@")[1]
                            )
                            table.add_row("Connection URL", masked_url)
                    except Exception:
                        pass

            out.console.print(table)
            out.success("Database information displayed")

        except Exception as e:
            out.error(f"Failed to get database info: {e}")
            raise typer.Exit(code=1)

    async def _test_connection(retries: int, delay: float, verbose: bool) -> None:
        """Test database connection with custom retry settings."""
        out = get_cli_output("db-test", verbose=verbose)

        try:
            out.info(
                f"Testing database connection (retries: {retries}, delay: {delay}s)..."
            )

            db_connection = await run_with_retries(
                get_db_connection, retries=retries, delay=delay
            )

            ***REMOVED*** Additional connection test
            is_healthy = await run_with_retries(
                _test_db_connection, db_connection, retries=retries, delay=delay
            )

            if is_healthy:
                out.success("Database connection test passed")

                if verbose:
                    table = Table(title="Connection Test Results")
                    table.add_column("Test", style="cyan")
                    table.add_column("Result", style="green")

                    table.add_row("Connection Established", "✓ Pass")
                    table.add_row("Response Test", "✓ Pass")
                    table.add_row(
                        "Retry Configuration", f"{retries} attempts, {delay}s delay"
                    )

                    out.console.print(table)
            else:
                out.error("Database connection test failed")
                raise typer.Exit(code=1)

        except Exception as e:
            out.error(f"Connection test failed: {e}")
            raise typer.Exit(code=1)

    async def _test_db_connection(db_connection: Any) -> bool:
        """Test database connection health."""
        try:
            ***REMOVED*** Generic connection test - this would be customized based on database type
            if hasattr(db_connection, "execute"):
                ***REMOVED*** SQLAlchemy-style or asyncpg connection
                await db_connection.execute("SELECT 1")
                return True
            elif hasattr(db_connection, "ping"):
                ***REMOVED*** Some databases have ping methods
                ping_result = await db_connection.ping()
                return bool(ping_result)
            elif hasattr(db_connection, "is_connected"):
                ***REMOVED*** Check connection status
                connection_status = db_connection.is_connected()
                return bool(connection_status)
            else:
                ***REMOVED*** Basic existence check
                return db_connection is not None
        except Exception:
            return False

    ***REMOVED*** Add migration commands if provided
    if migration_commands:
        for cmd_name, cmd_func in migration_commands.items():
            ***REMOVED*** Wrap functions to provide consistent output handling
            def wrap_migration_command(func: Callable[..., Any]) -> Callable[..., Any]:
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    ***REMOVED*** Add verbose option if not present
                    if "verbose" not in kwargs:
                        kwargs["verbose"] = False

                    ***REMOVED*** Setup output handler
                    out = get_cli_output(
                        f"db-{cmd_name}", verbose=kwargs.get("verbose", False)
                    )

                    try:
                        out.info(f"Running database {cmd_name}...")
                        result = func(*args, **kwargs)
                        out.success(f"Database {cmd_name} completed successfully")
                        return result
                    except Exception as e:
                        out.error(f"Database {cmd_name} failed: {e}")
                        raise typer.Exit(code=1)

                ***REMOVED*** Preserve function metadata
                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__ or f"Run database {cmd_name} operation"

                return wrapper

            app.command(name=cmd_name)(wrap_migration_command(cmd_func))

    return app
