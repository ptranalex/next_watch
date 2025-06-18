"""CLI output management module.

Provides unified output handling for CLI applications with separation between
user-facing output (Rich console) and operational logging (structured logging).
"""

from .handler import CLIOutput, get_cli_output

__all__ = ["CLIOutput", "get_cli_output"]
