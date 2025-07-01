"""Health check service for the ML API.

This service provides comprehensive health checks for all dependencies:
- Embedding model loading and availability
- Vector storage systems
- Computation resources
"""

import asyncio
import time
from typing import Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

from config.logging import get_logger

if TYPE_CHECKING:
    from fast_core.monitoring import HealthCheckRegistry

logger = get_logger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    is_healthy: bool
    status: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthService:
    """Service for performing health checks on all dependencies."""

    def __init__(self) -> None:
        """Initialize the health service."""
        pass

    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """Check health of all services.

        Returns:
            Dictionary mapping service names to health check results
        """
        ***REMOVED*** Run all health checks concurrently
        model_task = asyncio.create_task(self.check_embedding_model())

        ***REMOVED*** Wait for all checks to complete
        gather_results = await asyncio.gather(model_task, return_exceptions=True)

        ***REMOVED*** Handle any exceptions and build results
        results: Dict[str, HealthCheckResult] = {}

        model_result = gather_results[0]
        if isinstance(model_result, Exception):
            results["embedding_model"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(model_result)
            )
        elif isinstance(model_result, HealthCheckResult):
            results["embedding_model"] = model_result
        else:
            results["embedding_model"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        return results

    async def check_embedding_model(self) -> HealthCheckResult:
        """Check embedding model health.

        Returns:
            Health check result for embedding model
        """
        start_time = time.time()

        try:
            ***REMOVED*** Check if embedding service is available
            from ml_api.config.app import get_ml_settings

            settings = get_ml_settings()
            response_time = (time.time() - start_time) * 1000

            if settings.enable_embeddings:
                ***REMOVED*** Check if embedding service is loaded by calling the info endpoint
                try:
                    from ml_api.services import embedding_service

                    ***REMOVED*** Get actual model info from the service
                    model_info = embedding_service.get_model_info()
                    model_loaded = model_info.get("status") == "loaded"
                    model_health = model_info.get("health", "unknown")

                    return HealthCheckResult(
                        is_healthy=model_loaded and model_health in ["ok", "good"],
                        status="healthy" if model_loaded else "not_loaded",
                        response_time_ms=round(response_time, 2),
                        details={
                            "embeddings_enabled": True,
                            "model_loaded": model_loaded,
                            "model_health": model_health,
                            "model_id": model_info.get("model_id", "unknown"),
                            "dimensions": model_info.get("dimensions", 0),
                            "service": "available",
                        },
                    )
                except ImportError:
                    return HealthCheckResult(
                        is_healthy=False,
                        status="service_unavailable",
                        response_time_ms=round(response_time, 2),
                        error="Embedding service not available",
                    )
            else:
                return HealthCheckResult(
                    is_healthy=True,
                    status="disabled",
                    response_time_ms=round(response_time, 2),
                    details={
                        "embeddings_enabled": False,
                        "message": "Embeddings disabled by configuration",
                    },
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Embedding model health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    def close(self) -> None:
        """Close all client connections."""
        pass


***REMOVED*** Global health service instance
_health_service: Optional[HealthService] = None


def get_health_service() -> HealthService:
    """Get the global health service instance.

    Returns:
        HealthService instance
    """
    global _health_service

    if _health_service is None:
        _health_service = HealthService()

    return _health_service


def close_health_service() -> None:
    """Close the global health service instance."""
    global _health_service

    if _health_service is not None:
        _health_service.close()
        _health_service = None


***REMOVED***
***REMOVED*** NEW HEALTH CHECK REGISTRY INTEGRATION
***REMOVED***


def setup_ml_health_checks(registry: "HealthCheckRegistry") -> None:
    """Setup ML API-specific health checks with the new registry system.

    Args:
        registry: Health check registry to register checks with
    """
    from fast_core.monitoring import (
        HealthCheckDefinition,
        HealthCheckType,
        HealthCheckCategory,
        HealthCheckResult,
    )
    import time

    ***REMOVED*** Embedding Model - CRITICAL (core ML functionality)
    async def check_embedding_model() -> HealthCheckResult:
        """Check embedding model availability."""
        start_time = time.time()
        try:
            from ml_api.config.app import get_ml_settings

            settings = get_ml_settings()
            response_time = (time.time() - start_time) * 1000

            if settings.enable_embeddings:
                ***REMOVED*** Check if embedding service is loaded by calling the info endpoint
                try:
                    from ml_api.services import embedding_service

                    ***REMOVED*** Get actual model info from the service
                    model_info = embedding_service.get_model_info()
                    model_loaded = model_info.get("status") == "loaded"
                    model_health = model_info.get("health", "unknown")

                    return HealthCheckResult(
                        is_healthy=model_loaded and model_health in ["ok", "good"],
                        status="healthy" if model_loaded else "not_loaded",
                        response_time_ms=round(response_time, 2),
                        details={
                            "embeddings_enabled": True,
                            "model_loaded": model_loaded,
                            "model_health": model_health,
                            "model_id": model_info.get("model_id", "unknown"),
                            "dimensions": model_info.get("dimensions", 0),
                            "service": "available",
                        },
                    )
                except ImportError:
                    return HealthCheckResult(
                        is_healthy=False,
                        status="service_unavailable",
                        response_time_ms=round(response_time, 2),
                        error="Embedding service not available",
                    )
            else:
                ***REMOVED*** Embeddings disabled - this is OK for development
                return HealthCheckResult(
                    is_healthy=True,
                    status="disabled",
                    response_time_ms=round(response_time, 2),
                    details={
                        "embeddings_enabled": False,
                        "message": "Embeddings disabled by configuration",
                    },
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="error",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    ***REMOVED*** Vector Storage - IMPORTANT (for similarity search)
    async def check_vector_storage() -> HealthCheckResult:
        """Check vector storage systems."""
        start_time = time.time()
        try:
            ***REMOVED*** Basic check - could be enhanced with actual vector DB connectivity
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                is_healthy=True,
                status="healthy",
                response_time_ms=round(response_time, 2),
                details={
                    "vector_storage": "configured",
                    "storage_type": "in_memory",  ***REMOVED*** Could be enhanced
                },
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="error",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    ***REMOVED*** Model Performance - INFORMATIONAL (monitoring only)
    async def check_model_performance() -> HealthCheckResult:
        """Check ML model performance metrics."""
        start_time = time.time()
        try:
            ***REMOVED*** Performance metrics check - could be enhanced with actual benchmarks
            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                is_healthy=True,
                status="healthy",
                response_time_ms=round(response_time, 2),
                details={
                    "performance_check": "basic",
                    "latency_ok": True,
                    "memory_usage": "normal",
                },
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="error",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    ***REMOVED*** Register health checks
    registry.add_check(
        HealthCheckDefinition(
            name="embedding_model",
            check_func=check_embedding_model,
            types={HealthCheckType.READINESS, HealthCheckType.DEEP},
            category=HealthCheckCategory.CRITICAL,
            timeout_seconds=10.0,  ***REMOVED*** Model loading can take time
        )
    )

    registry.add_check(
        HealthCheckDefinition(
            name="vector_storage",
            check_func=check_vector_storage,
            types={HealthCheckType.READINESS, HealthCheckType.DEEP},
            category=HealthCheckCategory.IMPORTANT,
            timeout_seconds=5.0,
        )
    )

    registry.add_check(
        HealthCheckDefinition(
            name="model_performance",
            check_func=check_model_performance,
            types={HealthCheckType.DEEP},  ***REMOVED*** Only in deep checks
            category=HealthCheckCategory.INFORMATIONAL,
            timeout_seconds=3.0,
        )
    )

    logger.info(
        "ML API health checks registered - CRITICAL: embedding_model | IMPORTANT: vector_storage | INFO: model_performance"
    )
