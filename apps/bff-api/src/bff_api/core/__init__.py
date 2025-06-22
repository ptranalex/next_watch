"""Core module for the BFF service.

This module contains the foundational components for the Next Watch BFF service,
implementing fast-core integration for standardized application patterns.
"""

from .app_fast_core import create_bff_app as create_app

__all__ = ["create_app"]
