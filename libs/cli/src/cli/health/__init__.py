"""Health check utilities for CLI commands.

This module provides lightweight utilities for health command generation and result display,
following the proven patterns from the BFF API CLI where the complexity lives in each
service's health_service, not in CLI orchestration.
"""

from .display import (
    display_health_results,
    display_single_health_result,
    get_health_summary,
)
from .generators import create_health_commands

__all__ = [
    "display_health_results",
    "display_single_health_result",
    "get_health_summary",
    "create_health_commands",
]
