"""Command implementations for the CLI."""

# Import command groups
# Import all command modules (this triggers registration with the appropriate apps)
from backend_api.cli.commands import (  # Database commands (consolidated); Health commands; Cache commands; System commands (registered directly with main app)
    cache,
    config,
    database,
    health,
    redis,
    serve,
    version,
)

__all__ = [
    # Database commands
    "database",
    # Health commands
    "health",
    # Cache commands
    "cache",
    "redis",
    # System commands
    "config",
    "serve",
    "version",
]
