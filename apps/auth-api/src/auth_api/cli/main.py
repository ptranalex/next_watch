"""Main CLI application for Authentication service."""

import logging
import os
import sys
from importlib import metadata

import typer
import uvicorn
from rich.console import Console
from rich.traceback import install

# Import command modules
from auth_api.cli.commands import health, users
from auth_api.cli.utils import print_config

# Import configuration and utilities
from auth_api.config.app import settings

# Install rich traceback handler
install()

console = Console()
logger = logging.getLogger(__name__)

# Create main Typer app
app = typer.Typer(
    name="auth-api",
    help="Authentication service for Next Watch movie platform",
    add_completion=False,
)

# Add command groups
app.add_typer(health.app, name="health")
app.add_typer(users.app, name="users")


@app.command()
def serve(
    host: str = typer.Option(
        None,
        "--host",
        "-h",
        help="Host to bind server to",
        envvar="HOST",
    ),
    port: int = typer.Option(
        None,
        "--port",
        "-p",
        help="Port to bind server to",
        envvar="AUTH_API_PORT",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload for development",
    ),
    log_level: str = typer.Option(
        None,
        "--log-level",
        help="Set log level (DEBUG, INFO, WARNING, ERROR)",
        envvar="LOG_LEVEL",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging and output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress console output except errors",
    ),
) -> None:
    """Start the Authentication API server.

    Args:
        host: Host address to bind the server to
        port: Port number to bind the server to
        reload: Whether to enable auto-reload for development
        log_level: Logging level for the application
        verbose: Enable verbose console output
        quiet: Suppress console output except errors
    """
    try:
        # Use the existing settings instance and apply CLI overrides if needed
        config = settings

        # Override individual values for CLI usage
        actual_host = host or "0.0.0.0"
        actual_port = port or config.port
        actual_log_level = log_level or config.log_level

        # Get environment from environment variable
        environment = os.getenv("ENVIRONMENT", "development")

        # Display configuration unless quiet mode
        if not quiet:
            if verbose:
                print_config(config, "Auth Server Configuration", console)
            else:
                console.print(
                    f"[blue]Starting Auth API server on {actual_host}:{actual_port}[/blue]"
                )
                console.print(f"[dim]Environment: {environment} | Debug: {config.debug}[/dim]")

        # Configure logging level
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        elif quiet:
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=getattr(logging, actual_log_level))

        logger.info(f"Starting Authentication API server on {actual_host}:{actual_port}")

        if verbose:
            logger.debug(f"Configuration: host={actual_host}, port={actual_port}, reload={reload}")

        # Start server
        # Use factory pattern to create app - works for both dev and production
        from auth_api.main import create_app

        app_instance = create_app()

        uvicorn.run(
            app_instance,
            host=actual_host,
            port=actual_port,
            reload=reload,
            log_level=actual_log_level.lower(),
            access_log=not config.is_production,
        )

    except Exception as e:
        console.print(f"[bold red]Error starting server: {e}[/bold red]")
        logger.error(f"Failed to start server: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def config(
    show_secrets: bool = typer.Option(
        False,
        "--show-secrets",
        help="Show sensitive configuration values (use with caution)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed configuration information",
    ),
) -> None:
    """Display current configuration.

    Args:
        show_secrets: Whether to show sensitive values unmasked
        verbose: Show additional configuration details
    """
    try:
        title = "Auth API Configuration"
        if verbose:
            title += " (Detailed)"

        print_config(settings, title, console, show_secrets=show_secrets)

        if verbose:
            environment = os.getenv("ENVIRONMENT", "development")
            console.print(f"[dim]Configuration loaded from: {environment} environment[/dim]")
            console.print(f"[dim]Debug mode: {'Enabled' if settings.debug else 'Disabled'}[/dim]")
            console.print(
                f"[dim]Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'Local'}[/dim]"
            )

    except Exception as e:
        console.print(f"[bold red]Error displaying configuration: {e}[/bold red]")
        logger.error(f"Failed to display configuration: {e}")
        raise typer.Exit(code=1) from e


@app.command(name="version")
def show_version() -> None:
    """Show Auth API version information."""
    try:
        # Try to get version from package metadata
        try:
            version = metadata.version("auth-api")
        except (metadata.PackageNotFoundError, AttributeError):
            version = "development"

        environment = os.getenv("ENVIRONMENT", "development")

        console.print(f"[bold blue]Auth API[/bold blue] version [green]{version}[/green]")
        console.print(f"Environment: [yellow]{environment}[/yellow]")
        console.print(f"Python: [dim]{sys.version.split()[0]}[/dim]")
        console.print(
            f"Database: [cyan]{settings.database_url.split('@')[-1] if '@' in settings.database_url else 'Local'}[/cyan]"
        )

    except Exception as e:
        console.print(f"[bold red]Error getting version: {e}[/bold red]")
        raise typer.Exit(code=1) from e


@app.command(name="init-db")
def init_database(
    confirm: bool = typer.Option(
        True,
        "--confirm/--no-confirm",
        help="Confirm before initializing database",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Initialize the authentication database with required tables.

    Args:
        confirm: Whether to confirm before initializing
        verbose: Show detailed output
    """
    try:
        if confirm:
            from rich.prompt import Confirm

            confirmed = Confirm.ask("This will create/update database tables. Continue?")
            if not confirmed:
                console.print("[yellow]Database initialization cancelled.[/yellow]")
                return

        if verbose:
            console.print("[blue]🔧 Initializing authentication database...[/blue]")

        # Import and run database initialization
        from sqlalchemy import create_engine

        # Try to import SQLModel Base from movie_storage, but provide fallback
        try:
            from sqlmodel import SQLModel
        except ImportError:
            console.print(
                "[yellow]⚠️  movie_storage.models not available, creating basic user table...[/yellow]"
            )
            # Create a basic user table if movie_storage is not available
            from sqlalchemy import (
                Boolean,
                Column,
                DateTime,
                Integer,
                MetaData,
                String,
                Table,
            )
            from sqlalchemy.sql import func

            metadata = MetaData()
            _ = Table(
                "users",
                metadata,
                Column("id", Integer, primary_key=True),
                Column("email", String(255), unique=True, nullable=False),
                Column("username", String(100), unique=True, nullable=True),
                Column("hashed_password", String(255), nullable=False),
                Column("is_active", Boolean, default=True),
                Column("is_admin", Boolean, default=False),
                Column("created_at", DateTime, server_default=func.now()),
                Column("last_login_at", DateTime, nullable=True),
            )

            engine = create_engine(settings.database_url)
            metadata.create_all(bind=engine)

            console.print("[green]✅ Basic user table created successfully![/green]")
            return

        engine = create_engine(settings.database_url)

        if verbose:
            console.print("[blue]Creating database tables...[/blue]")

        SQLModel.metadata.create_all(bind=engine)

        console.print("[green]✅ Database initialized successfully![/green]")

        if verbose:
            console.print(
                f"[dim]Database URL: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}[/dim]"
            )

    except Exception as e:
        console.print(f"[bold red]Error initializing database: {e}[/bold red]")
        logger.error(f"Failed to initialize database: {e}")
        raise typer.Exit(code=1) from e


def main() -> None:
    """Main entry point for CLI."""
    try:
        app()
    except Exception as e:
        # Use basic logging since configure_logging might not be set up yet
        logger = logging.getLogger("auth_api.cli")
        logger.error(f"Error running command: {str(e)}")
        console.print(f"[bold red]CLI Error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
