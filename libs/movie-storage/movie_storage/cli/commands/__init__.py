"""Command implementations for the CLI."""

# Import and register commands
from movie_storage.cli import app

# Import all command modules (this triggers registration with the app)
from movie_storage.cli.commands import downgrade, init, migrate, teardown

__all__ = ["migrate", "downgrade", "init", "teardown"]
