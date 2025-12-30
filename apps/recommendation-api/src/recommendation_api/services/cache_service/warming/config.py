"""Recommendation API Cache Warming Configuration.

This module handles all configuration settings and setup for the recommendation API cache warming system.
"""

from typing import Any

from cache.warming import WarmingConfig

from recommendation_api.config import settings


def get_recommendation_warming_config() -> WarmingConfig:
    """Get recommendation-specific warming configuration.

    Returns:
        Configured WarmingConfig instance with recommendation-specific settings
    """
    return WarmingConfig(
        max_concurrent_operations=getattr(settings, "warming_max_concurrent", 5),
        max_items_per_strategy=getattr(settings, "warming_max_items_per_strategy", 100),
        min_miss_rate_threshold=getattr(settings, "warming_min_miss_rate", 0.3),
        min_avg_miss_time_ms=getattr(settings, "warming_min_avg_miss_time", 100.0),
        min_total_calls=getattr(settings, "warming_min_total_calls", 10),
        # Strategy configuration - Enable popular_content for recommendations
        enable_metrics_driven=True,
        enable_popular_content=True,
        enable_user_specific=False,  # Disable for recommendation API
        enable_scheduled=True,
        # Strategy weights
        metrics_driven_weight=1.0,
        popular_content_weight=1.0,  # Higher weight for popular content
        user_specific_weight=0.0,  # Disabled
        scheduled_weight=0.8,
    )


def get_recommendation_warming_settings() -> dict[str, Any]:
    """Get recommendation-specific warming settings as a dictionary.

    Returns:
        Dictionary containing warming configuration settings
    """
    return {
        "max_concurrent_operations": getattr(settings, "warming_max_concurrent", 5),
        "max_items_per_strategy": getattr(settings, "warming_max_items_per_strategy", 100),
        "enable_popular_content": True,
        "enable_user_specific": False,
        "enable_scheduled": True,
        "enable_metrics_driven": True,
    }
