"""BFF Cache Warming Service.

This module provides the main warming service that orchestrates all warming components
including configuration, functions, providers, and factories.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from cache import (
    CacheManager,
    WarmingEngine,
    WarmingStrategy,
    get_global_collector,
)
from cache.warming import set_global_warming_engine
from cache.warming.strategies import PopularContentStrategy
from config.logging import get_logger

from bff_api.services.cache_service.cache_service import get_cache
from bff_api.services.cache_service.warming.config import get_bff_warming_config
from bff_api.services.cache_service.warming.factories import BFFTargetFactories
from bff_api.services.cache_service.warming.functions import WarmingFunctions
from bff_api.config.app import settings
from bff_api.services.cache_service.warming.providers import BFFDataProviders

logger = get_logger(__name__)


class BFFWarmingService:
    """Main BFF warming service that orchestrates all warming components."""

    def __init__(self) -> None:
        """Initialize the BFF warming service."""
        self.config = get_bff_warming_config()
        self.cache_manager = get_cache()
        self.metrics_collector = get_global_collector()

        ***REMOVED*** Initialize component classes
        self.data_providers = BFFDataProviders()
        self.warming_functions = WarmingFunctions(settings)
        self.target_factories = BFFTargetFactories()

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

        logger.info("BFF warming service initialized successfully")

    def _register_warming_functions(self) -> None:
        """Register all BFF warming functions with the engine."""
        self.engine.register_warming_function(
            "movie_screen", self.warming_functions.warm_movie_screen
        )
        self.engine.register_warming_function(
            "movies_list", self.warming_functions.warm_movies_list
        )
        self.engine.register_warming_function(
            "actor_screen", self.warming_functions.warm_actor_screen
        )
        self.engine.register_warming_function(
            "genre_screen", self.warming_functions.warm_genre_screen
        )

        logger.info("Registered BFF warming functions for cache warming")

    def _setup_data_providers(self) -> None:
        """Set up data providers for warming strategies."""
        ***REMOVED*** Set up popular content provider
        self.engine.set_popularity_provider(self.data_providers.get_popularity_data)

        ***REMOVED*** Set up user data providers
        self.engine.set_user_data_provider(self.data_providers.get_user_data)
        self.engine.set_recommendation_provider(self.data_providers.get_user_recommendations)

        logger.info("Configured BFF data providers for warming strategies")

    def _setup_target_factories(self) -> None:
        """Set up target factories for popular content strategy."""
        popular_strategy = self.engine._strategies.get(WarmingStrategy.POPULAR_CONTENT)
        if popular_strategy and isinstance(popular_strategy, PopularContentStrategy):
            popular_strategy.register_target_factory(
                "movies", self.target_factories.create_movie_targets
            )
            popular_strategy.register_target_factory(
                "actors", self.target_factories.create_actor_targets
            )
            popular_strategy.register_target_factory(
                "genres", self.target_factories.create_genre_targets
            )

        logger.info("Configured BFF target factories for popular content strategy")

    async def health_check(self) -> bool:
        """Perform health check on BFF warming service.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            ***REMOVED*** Check if cache manager is healthy
            cache_healthy = await self.cache_manager.health_check()

            ***REMOVED*** Check if strategies are available
            strategies_available = len(self.engine.get_available_strategies()) > 0

            return cache_healthy and strategies_available

        except Exception as e:
            logger.error(f"BFF warming service health check failed: {e}")
            return False

    async def test_warming_function(
        self, function_name: str = "movie_screen", **kwargs: Any
    ) -> Dict[str, Any]:
        """Test a specific warming function to verify it works correctly.

        This is useful for development and testing to ensure warming functions
        are properly implemented and connected to cached endpoints.

        Args:
            function_name: Name of the warming function to test
            **kwargs: Parameters to pass to the warming function

        Returns:
            Dictionary containing test results and any warming data

        Example:
            ***REMOVED*** Test movie screen warming
            result = await warming_service.test_warming_function(
                "movie_screen",
                movie_id=1,
                user_id=None
            )

            ***REMOVED*** Test movies list warming
            result = await warming_service.test_warming_function(
                "movies_list",
                page=1,
                limit=20,
                genre_id=28  ***REMOVED*** Action genre
            )
        """
        try:
            logger.info(
                "Testing warming function",
                function_name=function_name,
                parameters=kwargs,
                service="bff",
                component="warming_service",
            )

            ***REMOVED*** Check if function is registered
            if function_name not in self.engine._warming_functions:
                available_functions = list(self.engine._warming_functions.keys())
                return {
                    "success": False,
                    "error": f"Warming function '{function_name}' not found",
                    "available_functions": available_functions,
                }

            ***REMOVED*** Call the warming function
            warming_func = self.engine._warming_functions[function_name]
            result = await warming_func(**kwargs)

            logger.info(
                "Successfully tested warming function",
                function_name=function_name,
                result_keys=list(result.keys()) if isinstance(result, dict) else "non-dict",
                service="bff",
                component="warming_service",
            )

            return {
                "success": True,
                "function_name": function_name,
                "parameters": kwargs,
                "warming_result": result,
                "test_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(
                "Warming function test failed",
                function_name=function_name,
                parameters=kwargs,
                error=str(e),
                service="bff",
                component="warming_service",
            )

            return {
                "success": False,
                "function_name": function_name,
                "parameters": kwargs,
                "error": str(e),
                "test_timestamp": datetime.now().isoformat(),
            }

    def get_warming_engine(self) -> WarmingEngine:
        """Get the configured warming engine.

        Returns:
            The warming engine instance
        """
        return self.engine


***REMOVED*** Global BFF warming service instance
_bff_warming_service: Optional[BFFWarmingService] = None


def get_bff_warming_service() -> BFFWarmingService:
    """Get the global BFF warming service instance.

    Returns:
        Global BFF warming service instance
    """
    global _bff_warming_service
    if _bff_warming_service is None:
        _bff_warming_service = BFFWarmingService()
    return _bff_warming_service


def configure_bff_warming() -> None:
    """Configure BFF-specific warming.

    This function initializes the BFF warming service which configures
    the cache warming system with BFF-specific data providers and functions.
    """
    try:
        ***REMOVED*** Initialize BFF warming service which configures the cache library
        service = get_bff_warming_service()
        logger.info("✅ BFF warming configuration applied")

    except Exception as e:
        logger.error(f"❌ Failed to configure BFF warming: {e}")
        ***REMOVED*** Don't raise - warming should be optional


***REMOVED*** Auto-configure BFF warming when this module is imported
***REMOVED*** This ensures the CLI commands use the BFF-configured engine
def _auto_configure() -> None:
    """Auto-configure BFF warming when module is imported."""
    try:
        configure_bff_warming()
        logger.debug("BFF warming auto-configured on import")
    except Exception as e:
        logger.warning(f"Auto-configuration of BFF warming failed: {e}")


***REMOVED*** Enable auto-configuration
_auto_configure()
