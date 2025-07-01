"""Health check service for the Auth API.

This service provides comprehensive health checks for all dependencies:
- PostgreSQL database (via movie_storage)
"""

import asyncio
from config.logging import get_logger
import time
from typing import Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

from config.logging import get_logger

from sqlmodel import Session, text

from auth_api.config.app import settings
from auth_api.db.database import get_db

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
        ***REMOVED*** Run all health checks concurrently (only postgres for auth-api)
        postgres_task = asyncio.create_task(self.check_postgres())

        ***REMOVED*** Wait for all checks to complete
        gather_results = await asyncio.gather(postgres_task, return_exceptions=True)

        ***REMOVED*** Handle any exceptions and build results
        results: Dict[str, HealthCheckResult] = {}

        postgres_result = gather_results[0]  ***REMOVED*** Extract from list
        if isinstance(postgres_result, Exception):
            results["postgres"] = HealthCheckResult(
                is_healthy=False, status="error", error=str(postgres_result)
            )
        elif isinstance(postgres_result, HealthCheckResult):
            results["postgres"] = postgres_result
        else:
            ***REMOVED*** This shouldn't happen, but handle it
            results["postgres"] = HealthCheckResult(
                is_healthy=False, status="error", error="Unexpected result type"
            )

        return results

    async def check_postgres(self) -> HealthCheckResult:
        """Check PostgreSQL database health.

        Returns:
            Health check result for PostgreSQL
        """
        ***REMOVED*** Use the sync version since we don't have asyncpg dependency
        return self.check_postgres_sync()

    def check_postgres_sync(self) -> HealthCheckResult:
        """Synchronous PostgreSQL health check using existing database session.

        Returns:
            Health check result for PostgreSQL
        """
        start_time = time.time()

        try:
            ***REMOVED*** Use the existing database session
            with next(get_db()) as db:
                ***REMOVED*** Try a simple query
                result = db.execute(text("SELECT 1")).scalar()

                ***REMOVED*** Get version
                version_result = db.execute(text("SELECT version()")).scalar()
                version = version_result if version_result else "Unknown"

                ***REMOVED*** Get database size
                db_size_result = db.execute(
                    text("SELECT pg_size_pretty(pg_database_size(current_database())) as size")
                ).scalar()
                db_size = db_size_result if db_size_result else "Unknown"

                response_time = (time.time() - start_time) * 1000

                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={
                        "version": version,
                        "database_size": db_size,
                        "connection_successful": True,
                        "query_result": result,
                    },
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"PostgreSQL sync health check failed: {e}")

            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    def close(self) -> None:
        """Close all client connections (no-op for auth-api since only postgres)."""
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


def setup_auth_health_checks(registry: "HealthCheckRegistry") -> None:
    """Setup Auth API-specific health checks with the new registry system.

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
    from sqlmodel import text

    ***REMOVED*** PostgreSQL Database - CRITICAL dependency (auth service requires database for user data)
    async def check_postgres() -> HealthCheckResult:
        """Check PostgreSQL database health."""
        start_time = time.time()
        try:
            with next(get_db()) as db:
                ***REMOVED*** Simple connectivity test
                result = db.execute(text("SELECT 1")).scalar()

                ***REMOVED*** Get version for details
                version_result = db.execute(text("SELECT version()")).scalar()
                version = version_result if version_result else "Unknown"

                response_time = (time.time() - start_time) * 1000

                return HealthCheckResult(
                    is_healthy=True,
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    details={
                        "version": (
                            version.split()[1]
                            if version and len(version.split()) > 1
                            else "Unknown"
                        ),
                        "connection": "successful",
                    },
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                is_healthy=False,
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                error=str(e),
            )

    ***REMOVED*** JWT Token validation check - INFORMATIONAL (for monitoring)
    async def check_jwt_config() -> HealthCheckResult:
        """Check JWT configuration is valid."""
        start_time = time.time()
        try:
            ***REMOVED*** Basic check that JWT secret is configured (correct field name)
            if (
                hasattr(settings, "jwt_secret")
                and settings.jwt_secret
                and settings.jwt_secret != "change_me_in_production"
            ):
                jwt_configured = True
                details = {
                    "jwt_secret": "configured",
                    "algorithm": getattr(settings, "jwt_algorithm", "unknown"),
                }
            else:
                jwt_configured = False
                if not hasattr(settings, "jwt_secret"):
                    details = {"jwt_secret": "field_missing"}
                elif not settings.jwt_secret:
                    details = {"jwt_secret": "empty"}
                elif settings.jwt_secret == "change_me_in_production":
                    details = {"jwt_secret": "using_default"}
                else:
                    details = {"jwt_secret": "misconfigured"}

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                is_healthy=jwt_configured,
                status="healthy" if jwt_configured else "misconfigured",
                response_time_ms=round(response_time, 2),
                details=details,
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
            name="postgres",
            check_func=check_postgres,
            types={HealthCheckType.READINESS, HealthCheckType.DEEP},
            category=HealthCheckCategory.CRITICAL,
            timeout_seconds=5.0,
        )
    )

    registry.add_check(
        HealthCheckDefinition(
            name="jwt_config",
            check_func=check_jwt_config,
            types={HealthCheckType.DEEP},  ***REMOVED*** Only in deep checks
            category=HealthCheckCategory.INFORMATIONAL,
            timeout_seconds=1.0,
        )
    )

    logger.info(
        "Auth API health checks registered - CRITICAL: postgres | INFORMATIONAL: jwt_config"
    )
