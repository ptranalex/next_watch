"""Base warming strategy interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from cache.warming.types import WarmingTarget, WarmingConfig, WarmingStrategy


class BaseWarmingStrategy(ABC):
    """Abstract base class for cache warming strategies."""

    def __init__(self, config: WarmingConfig):
        """Initialize strategy with configuration.

        Args:
            config: Warming configuration
        """
        self.config = config
        self.strategy_type = WarmingStrategy.MANUAL  ***REMOVED*** Override in subclasses

    @abstractmethod
    async def identify_targets(
        self, limit: Optional[int] = None, context: Optional[Dict[str, Any]] = None
    ) -> List[WarmingTarget]:
        """Identify warming targets based on strategy logic.

        Args:
            limit: Maximum number of targets to return
            context: Additional context for target identification

        Returns:
            List of warming targets
        """
        pass

    @abstractmethod
    def calculate_priority(self, target_data: Dict[str, Any]) -> float:
        """Calculate priority score for a potential target.

        Args:
            target_data: Data about the potential target

        Returns:
            Priority score (higher = more important)
        """
        pass

    def should_warm_target(self, target_data: Dict[str, Any]) -> bool:
        """Check if a target should be warmed based on strategy criteria.

        Args:
            target_data: Data about the potential target

        Returns:
            True if target should be warmed
        """
        ***REMOVED*** Default implementation - can be overridden
        return True

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.

        Returns:
            Strategy information dictionary
        """
        return {
            "name": self.strategy_type.value,
            "description": self.__doc__ or "No description available",
            "config": {
                "max_items": self.config.max_items_per_strategy,
                "weight": getattr(self.config, f"{self.strategy_type.value}_weight", 1.0),
            },
        }

    def create_warming_target(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        priority: float,
        estimated_benefit: float = 0.0,
        ttl: Optional[int] = None,
    ) -> WarmingTarget:
        """Create a warming target with this strategy.

        Args:
            function_name: Name of function to warm
            parameters: Function parameters
            priority: Priority score
            estimated_benefit: Estimated performance benefit
            ttl: Optional TTL override

        Returns:
            Warming target
        """
        return WarmingTarget(
            function_name=function_name,
            parameters=parameters,
            priority=priority,
            estimated_benefit=estimated_benefit,
            ttl=ttl,
            strategy=self.strategy_type,
        )
