"""Dummy logging module (no longer used).

This module is kept for compatibility purposes but all logging configuration
functionality has been removed.
"""

import logging
from pathlib import Path
from typing import Optional, Callable, Any, Dict


def configure_logging(*args, **kwargs) -> Dict[str, Any]:
    """Dummy function that doesn't do anything.

    Returns:
        Empty dictionary.
    """
    return {}


def with_logging(*args, **kwargs) -> Callable[[Callable], Callable]:
    """Dummy decorator that just returns the original function.

    Returns:
        Identity decorator.
    """

    def decorator(func: Callable) -> Callable:
        return func

    return decorator
