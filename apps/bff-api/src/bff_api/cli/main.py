"""Main CLI application for BFF service."""

import sys
from typing import Any

import typer

# CLI framework utilities and command generators
from cli import (
    create_cache_commands,
    create_config_command,
    create_health_commands,
    create_serve_app,
    create_version_command,
)
from rich.traceback import install

# BFF-specific cache commands (consolidated)
from bff_api.cli.commands.cache_warming import cache_app as cache_cli

# Local BFF imports
from bff_api.config.app import settings

# Import BFF warming service to ensure auto-configuration
from bff_api.services.health_service import get_health_service

# Constants
DEFAULT_VERSION = "0.1.0"  # Should match pyproject.toml
SERVICE_NAME = "BFF API"
PACKAGE_NAME = "bff-api"
APP_IMPORT_STRING = "bff_api.main:app"

# Service configuration
SERVICE_CHECKS = {
    "backend": ("check_backend_api", "Backend API"),
    "auth": ("check_auth_api", "Auth API"),
    "reco": ("check_recommendation_api", "Recommendation API"),
    "cache": ("check_cache", "Cache Service"),
}

SECRET_FIELDS = ["jwt_secret", "backend_api_key", "reco_api_key", "auth_api_key"]
CORE_DEPENDENCIES = ["fastapi", "uvicorn", "redis", "httpx", "typer", "rich"]

# Install rich traceback handler
install()


# Helper function to get settings
def get_settings() -> Any:
    """Get settings instance."""
    return settings


# Helper functions
async def _get_redis_client() -> Any:
    """Get Redis client for cache commands."""
    from cache.providers.redis import RedisProvider

    from bff_api.services.cache_service import get_cache_service

    cache_manager = get_cache_service()  # This returns CacheManager directly
    provider = cache_manager.provider
    if isinstance(provider, RedisProvider):
        return await provider._get_client()
    else:
        raise RuntimeError("Redis provider required for cache commands")


def _get_app_instance() -> Any:
    """Get the FastAPI app instance for production mode."""
    from bff_api.main import create_app

    return create_app()


def _print_config(config: Any, title: str, console: Any) -> None:
    """Print configuration using BFF API's print_config utility."""
    from bff_api.cli.utils import print_config

    print_config(config, title, console)


def _parse_cli_flags() -> tuple[bool, bool]:
    """Parse CLI flags for logging configuration."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    http_verbose = "--http-verbose" in sys.argv
    return verbose, http_verbose


def _configure_logging(verbose: bool, http_verbose: bool) -> None:
    """Configure logging based on CLI flags."""
    from config.logging import configure_logging

    # Component-specific log levels based on context
    component_levels: dict[str, str] = {}
    if verbose:
        # In verbose mode, show more health service details but keep cache quiet
        component_levels = {
            "services.health_service": "DEBUG",
            "services.cache": "INFO",
            "config": "DEBUG",
        }

    configure_logging(
        log_level="DEBUG" if verbose else "INFO",
        verbose=verbose,
        quiet=not verbose,
        http_verbose=http_verbose,
        component_levels=component_levels,
    )


def _log_environment_info(verbose: bool) -> None:
    """Log environment and configuration information in verbose mode."""
    if not verbose:
        return

    # Show config details
    config = get_settings()
    # Log basic configuration info
    from config.logging import get_logger

    logger = get_logger(__name__)
    logger.info(
        f"BFF API configuration loaded - Environment: {config.environment}, Port: {config.port}"
    )


def _create_command_apps() -> tuple[typer.Typer, ...]:
    """Create all command applications using CLI framework."""
    # Health commands
    health_app = create_health_commands(
        health_service_getter=get_health_service,
        service_checks=SERVICE_CHECKS,
    )

    # Cache commands (generic Redis commands)
    redis_cache_app = create_cache_commands(
        get_redis_client=_get_redis_client, command_name="redis-cache"
    )

    # Serve app
    serve_app = create_serve_app(
        service_name=SERVICE_NAME,
        app_import_string=APP_IMPORT_STRING,
        get_app_instance=_get_app_instance,
        config_getter=get_settings,
        print_config_func=_print_config,
    )

    return health_app, redis_cache_app, serve_app


def _create_individual_commands() -> tuple[Any, Any]:
    """Create individual commands using CLI framework."""
    # Config command
    config_command = create_config_command(
        config_getter=get_settings,
        secret_fields=SECRET_FIELDS,
    )

    # Version command
    version_command = create_version_command(
        service_name=SERVICE_NAME,
        package_name=PACKAGE_NAME,
        default_version=DEFAULT_VERSION,
        config_getter=get_settings,
        dependencies=CORE_DEPENDENCIES,
    )

    return config_command, version_command


def _setup_cli_app() -> typer.Typer:
    """Set up and configure the main CLI application."""
    # Create main Typer app
    app = typer.Typer(
        name="bff-api",
        help="Backend for Frontend API service for Next Watch movie platform",
        add_completion=True,
    )

    # Create command applications
    health_app, redis_cache_app, serve_app = _create_command_apps()
    config_command, version_command = _create_individual_commands()

    # Add command groups
    app.add_typer(health_app, name="health")

    # Consolidated cache commands (metrics + warming + redis)
    app.add_typer(
        cache_cli,
        name="cache",
        help="🚀 Cache management, metrics, and warming operations",
    )
    app.add_typer(serve_app, name="serve")

    # Add individual commands
    app.command("config")(config_command)
    app.command("version")(version_command)

    return app


def main() -> None:
    """Main BFF CLI entry point."""
    # Parse CLI flags
    verbose, http_verbose = _parse_cli_flags()

    # Configure logging
    _configure_logging(verbose, http_verbose)

    # Log environment information in verbose mode
    _log_environment_info(verbose)

    # Set up and run CLI app
    app = _setup_cli_app()
    app()


# Create global app instance for external imports (e.g., testing)
app = _setup_cli_app()


if __name__ == "__main__":
    main()
