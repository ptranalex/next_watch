"""Command implementations for the CLI."""

***REMOVED*** Import and register commands
from movie_storage.cli import app

***REMOVED*** Import all command modules (this triggers registration with the app)
from movie_storage.cli.commands import (
    migrate,
    downgrade,
    init,
    teardown,
)

__all__ = ["migrate", "downgrade", "init", "teardown"]
