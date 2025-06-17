"""Command implementations for the CLI."""

***REMOVED*** Import command groups
from backend_api.cli import cache_app, db_app, health_app

***REMOVED*** Import all command modules (this triggers registration with the appropriate apps)
from backend_api.cli.commands import (  ***REMOVED*** Database commands (consolidated); Health commands; Cache commands; System commands (registered directly with main app)
    cache,
    config,
    database,
    health,
    redis,
    serve,
    version,
)

__all__ = [
    ***REMOVED*** Database commands
    "database",
    ***REMOVED*** Health commands
    "health",
    ***REMOVED*** Cache commands
    "cache",
    "redis",
    ***REMOVED*** System commands
    "config",
    "serve",
    "version",
]
