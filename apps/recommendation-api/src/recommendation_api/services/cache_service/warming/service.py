"""Recommendation API Cache Warming Service.

This module provides the main warming service that orchestrates all warming components
including configuration, functions, providers, and factories.
"""

from datetime import datetime
from typing import Any

from cache import (
    WarmingEngine,
    WarmingStrategy,
    get_global_collector,
)
from cache.warming import set_global_warming_engine
from config.logging import get_logger

from recommendation_api.services.cache_service.cache_service import get_cache
from recommendation_api.services.cache_service.warming.config import (
    get_recommendation_warming_config,
)
from recommendation_api.services.cache_service.warming.factories import (
    RecommendationTargetFactories,
)
from recommendation_api.services.cache_service.warming.functions import (
    RecommendationWarmingFunctions,
)
from recommendation_api.services.cache_service.warming.providers import RecommendationDataProviders

logger = get_logger(__name__)


class RecommendationWarmingService:
    """Main recommendation warming service that orchestrates all warming components."""

    def __init__(self) -> None:
        """Initialize the recommendation warming service."""
        self.config = get_recommendation_warming_config()
        self.cache_manager = get_cache()
        self.metrics_collector = get_global_collector()

        ***REMOVED*** Initialize component classes
        self.data_providers = RecommendationDataProviders()
        self.warming_functions = RecommendationWarmingFunctions()
        self.target_factories = RecommendationTargetFactories()

        ***REMOVED*** Create warming engine
        self.engine = WarmingEngine(
            cache_manager=self.cache_manager,
            metrics_collector=self.metrics_collector,
            config=self.config,
        )

        self._setup_warming_system()

    def _setup_warming_system(self) -> None:
        """Set up the complete warming system with all components."""
        self._register_warming_functions()
        self._setup_data_providers()
        self._setup_target_factories()

        ***REMOVED*** Register engine globally for CLI usage
        set_global_warming_engine(self.engine)

        logger.info(
            "Recommendation warming service initialized successfully",
            service="recommendation-api",
            component="warming_service",
        )

    def _register_warming_functions(self) -> None:
        """Register all recommendation warming functions with the engine."""
        self.engine.register_warming_function(
            "similar_movies", self.warming_functions.warm_similar_movies
        )
        self.engine.register_warming_function(
            "popular_movies", self.warming_functions.warm_popular_movies
        )
        self.engine.register_warming_function(
            "trending_movies", self.warming_functions.warm_trending_movies
        )

        logger.info(
            "Registered recommendation warming functions for cache warming",
            service="recommendation-api",
            component="warming_service",
        )

    def _setup_data_providers(self) -> None:
        """Set up data providers for warming strategies."""
        ***REMOVED*** Set up popular content provider
        self.engine.set_popularity_provider(self.data_providers.get_popularity_data)

        ***REMOVED*** No user-specific providers for recommendation API
        logger.info(
            "Configured recommendation data providers for warming strategies",
            service="recommendation-api",
            component="warming_service",
        )

    def _setup_target_factories(self) -> None:
        """Set up target factories for warming strategies."""
        ***REMOVED*** The WarmingEngine doesn't have set_popular_content_factory method
        ***REMOVED*** Instead, we'll register our factory functions when needed in the warming functions

        ***REMOVED*** No need to set factories directly on the engine
        logger.info(
            "Configured recommendation target factories for warming strategies",
            service="recommendation-api",
            component="warming_service",
        )

    async def warm_by_strategy(
        self, strategy: WarmingStrategy, limit: int | None = None
    ) -> dict[str, Any]:
        """Warm cache using a specific strategy.

        Args:
            strategy: Warming strategy to use
            limit: Maximum number of targets to warm

        Returns:
            Dictionary with warming statistics
        """
        try:
            logger.info(
                f"Running {strategy.name} warming strategy",
                service="recommendation-api",
                component="warming_service",
                strategy=strategy.name,
            )

            stats = await self.engine.warm_by_strategy(strategy, limit=limit)

            ***REMOVED*** Convert stats to dictionary with safe attribute access
            targets_warmed = getattr(stats, "targets_warmed", 0)
            success_count = getattr(stats, "success_count", 0)
            error_count = getattr(stats, "error_count", 0)
            total_time_ms = getattr(stats, "total_time_ms", 0)

            logger.info(
                f"Completed {strategy.name} warming: {targets_warmed} targets, {success_count} successes, {error_count} errors",
                service="recommendation-api",
                component="warming_service",
                strategy=strategy.name,
                targets_warmed=targets_warmed,
                success_count=success_count,
                error_count=error_count,
                total_time_ms=total_time_ms,
            )

            return {
                "strategy": strategy,
                "success": True,
                "targets_warmed": targets_warmed,
                "success_count": success_count,
                "error_count": error_count,
                "total_time_ms": total_time_ms,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(
                f"Error warming cache with strategy {strategy}: {e}",
                service="recommendation-api",
                component="warming_service",
                strategy=strategy.name,
                error=str(e),
                exc_info=True,
            )
            return {
                "strategy": strategy,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def test_warming_function(self, function_name: str, **kwargs) -> dict[str, Any]:
        """Test a specific warming function.

        Args:
            function_name: Name of the warming function to test
            **kwargs: Parameters for the warming function

        Returns:
            Dictionary with test results
        """
        try:
            logger.info(
                f"Testing warming function: {function_name}",
                service="recommendation-api",
                component="warming_service",
                function=function_name,
                parameters=str(kwargs),
            )

            if function_name == "similar_movies":
                result = await self.warming_functions.warm_similar_movies(**kwargs)
            elif function_name == "popular_movies":
                result = await self.warming_functions.warm_popular_movies(**kwargs)
            elif function_name == "trending_movies":
                result = await self.warming_functions.warm_trending_movies(**kwargs)
            else:
                logger.warning(
                    f"Unknown warming function: {function_name}",
                    service="recommendation-api",
                    component="warming_service",
                    function=function_name,
                )
                return {
                    "success": False,
                    "error": f"Unknown warming function: {function_name}",
                    "timestamp": datetime.now().isoformat(),
                }

            logger.info(
                f"Successfully tested warming function: {function_name}",
                service="recommendation-api",
                component="warming_service",
                function=function_name,
            )

            return {
                "function": function_name,
                "success": True,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(
                f"Error testing warming function {function_name}: {e}",
                service="recommendation-api",
                component="warming_service",
                function=function_name,
                error=str(e),
                exc_info=True,
            )
            return {
                "function": function_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_warming_engine(self) -> WarmingEngine:
        """Get the configured warming engine.

        Returns:
            The warming engine instance
        """
        return self.engine


***REMOVED*** Global recommendation warming service instance
_recommendation_warming_service: RecommendationWarmingService | None = None


def get_recommendation_warming_service() -> RecommendationWarmingService:
    """Get the global recommendation warming service instance.

    Returns:
        Global recommendation warming service instance
    """
    global _recommendation_warming_service
    if _recommendation_warming_service is None:
        _recommendation_warming_service = RecommendationWarmingService()
    return _recommendation_warming_service


def configure_recommendation_warming() -> None:
    """Configure recommendation-specific warming.

    This function initializes the recommendation warming service which configures
    the cache warming system with recommendation-specific data providers and functions.
    """
    try:
        ***REMOVED*** Initialize recommendation warming service which configures the cache library
        get_recommendation_warming_service()
        logger.info(
            "✅ Recommendation warming configuration applied",
            service="recommendation-api",
            component="warming_service",
        )

    except Exception as e:
        logger.error(
            f"❌ Failed to configure recommendation warming: {e}",
            service="recommendation-api",
            component="warming_service",
            error=str(e),
            exc_info=True,
        )
        ***REMOVED*** Don't raise - warming should be optional
