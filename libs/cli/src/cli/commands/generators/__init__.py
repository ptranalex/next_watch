"""Command generator utilities.

Provides functions to automatically generate CLI commands following proven
patterns from Backend API and other NextWatch services.
"""

from .cache import create_cache_commands
from .service import create_service_commands
from .database import create_database_commands
from .version import create_version_command, create_simple_version_command
from .serve import create_serve_command, create_serve_app

__all__ = [
    "create_cache_commands",
    "create_service_commands",
    "create_database_commands",
    "create_version_command",
    "create_simple_version_command",
    "create_serve_command",
    "create_serve_app",
]
