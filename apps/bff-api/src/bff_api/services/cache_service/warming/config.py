"""BFF Cache Warming Configuration.

This module handles all configuration settings and setup for the BFF cache warming system.
"""

from typing import Dict, Any
from cache.warming import WarmingConfig
from bff_api.config.app import settings


def get_bff_warming_config() -> WarmingConfig:
    """Get BFF-specific warming configuration.

    Returns:
        Configured WarmingConfig instance with BFF-specific settings
    """

    return WarmingConfig(
        max_concurrent_operations=getattr(settings, "warming_max_concurrent", 5),
        max_items_per_strategy=getattr(settings, "warming_max_items_per_strategy", 100),
        min_miss_rate_threshold=getattr(settings, "warming_min_miss_rate", 0.3),
        min_avg_miss_time_ms=getattr(settings, "warming_min_avg_miss_time", 100.0),
        min_total_calls=getattr(settings, "warming_min_total_calls", 10),
        ***REMOVED*** Strategy configuration - Enable user_specific for BFF
        enable_metrics_driven=True,
        enable_popular_content=True,
        enable_user_specific=True,  ***REMOVED*** Enable for BFF
        enable_scheduled=True,
        ***REMOVED*** Strategy weights
        metrics_driven_weight=1.0,
        popular_content_weight=0.8,
        user_specific_weight=0.6,
        scheduled_weight=0.7,
    )


def get_bff_warming_settings() -> Dict[str, Any]:
    """Get BFF-specific warming settings as a dictionary.

    Returns:
        Dictionary containing warming configuration settings
    """

    return {
        "max_concurrent_operations": getattr(settings, "warming_max_concurrent", 5),
        "max_items_per_strategy": getattr(settings, "warming_max_items_per_strategy", 100),
        "enable_popular_content": True,
        "enable_user_specific": True,
        "enable_scheduled": True,
        "enable_metrics_driven": True,
    }
