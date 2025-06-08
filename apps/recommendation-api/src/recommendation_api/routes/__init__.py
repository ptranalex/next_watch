"""Route modules for the Recommendation API."""

from .api_v1 import api_v1_router
from .health import router as health_router
from .meta import router as meta_router

__all__ = ["api_v1_router", "health_router", "meta_router"]
