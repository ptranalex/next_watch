"""Routes package for BFF API application."""

from .bff import router as bff_router
from .health import router as health_router

__all__ = ["bff_router", "health_router"]
