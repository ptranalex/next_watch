"""Core modules for the Recommendation API.

Now integrated with fast-core for standardized patterns.
"""

from .app_fast_core import create_recommendation_app as create_app

__all__ = ["create_app"]
