"""Cache warming system for NextWatch cache library."""

from .engine import WarmingEngine
from .strategies import (
    BaseWarmingStrategy,
    MetricsDrivenStrategy,
    PopularContentStrategy,
    ScheduledStrategy,
    UserSpecificStrategy,
)
from .types import (
    WarmingBatch,
    WarmingConfig,
    WarmingResult,
    WarmingStats,
    WarmingStatus,
    WarmingStrategy,
    WarmingTarget,
)

***REMOVED*** Global warming engine registry for dependency injection
_global_warming_engine: WarmingEngine | None = None


def set_global_warming_engine(engine: WarmingEngine) -> None:
    """Set the global warming engine for CLI and other components to use.

    This supports the dependency injection pattern where applications
    can provide their configured warming engine.

    Args:
        engine: Configured warming engine
    """
    global _global_warming_engine
    _global_warming_engine = engine


def get_global_warming_engine() -> WarmingEngine | None:
    """Get the global warming engine if one has been set.

    Returns:
        Global warming engine or None if not set
    """
    return _global_warming_engine


def clear_global_warming_engine() -> None:
    """Clear the global warming engine."""
    global _global_warming_engine
    _global_warming_engine = None


__all__ = [
    ***REMOVED*** Types
    "WarmingTarget",
    "WarmingResult",
    "WarmingBatch",
    "WarmingStats",
    "WarmingConfig",
    "WarmingStatus",
    "WarmingStrategy",
    ***REMOVED*** Core engine
    "WarmingEngine",
    ***REMOVED*** Strategies
    "BaseWarmingStrategy",
    "MetricsDrivenStrategy",
    "PopularContentStrategy",
    "UserSpecificStrategy",
    "ScheduledStrategy",
    ***REMOVED*** Global engine registry
    "set_global_warming_engine",
    "get_global_warming_engine",
    "clear_global_warming_engine",
]
