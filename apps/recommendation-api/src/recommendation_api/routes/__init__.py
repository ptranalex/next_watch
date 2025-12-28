"""Route modules for the Recommendation API."""

from .api_v1 import api_v1_router
from .health import router as health_router

__all__ = ["api_v1_router", "health_router"]
