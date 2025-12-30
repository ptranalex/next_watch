"""Data access layer for the Recommendation API.

This package contains repository implementations for accessing various data sources,
including databases, vector stores, and external services.
"""

# Import repository modules
from recommendation_api.repositories.vector import VectorRepository

# Export public API
__all__ = ["VectorRepository"]
