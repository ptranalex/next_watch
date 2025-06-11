"""Command implementations for the CLI."""

***REMOVED*** Import command groups
from backend_api.cli import db_app, health_app, cache_app

***REMOVED*** Import all command modules (this triggers registration with the appropriate apps)
from backend_api.cli.commands import (
    ***REMOVED*** Database commands (consolidated)
    database,
    ***REMOVED*** Health commands
    health,
    ***REMOVED*** Cache commands
    cache,
    redis,
    ***REMOVED*** System commands (registered directly with main app)
    config,
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
