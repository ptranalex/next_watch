"""
Redis-backed search suggestion engine module.

This module provides a comprehensive suggestion engine that was moved from backend-api
to the dedicated search-api service. It supports advanced features like:
- Prefix matching with Redis sorted sets
- Entity-based suggestions with metadata
- Ranking and deduplication
- Fuzzy matching fallbacks

The module is organized into:
- core: Main SuggestionEngine class
- matching: Prefix and substring matching strategies
- hydration: Entity data fetching and enrichment
- ranking: Suggestion ranking and scoring
- utils: Helper functions and constants
"""

from .core import SuggestionEngine

__all__ = ["SuggestionEngine"]
