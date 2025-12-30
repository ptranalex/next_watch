"""Example demonstrating health status metrics integration in fast-core.

This example shows how to use the new health status metrics that integrate
with the health check system to provide Prometheus metrics for monitoring.
"""

import asyncio
import time

from fast_core.monitoring import (
    HealthCheckCategory,
    HealthCheckDefinition,
    HealthCheckRegistry,
    HealthCheckResult,
    HealthCheckType,
    initialize_metrics,
)


# Example health check functions
async def check_database() -> HealthCheckResult:
    """Example database health check."""
    start_time = time.time()

    # Simulate database check
    await asyncio.sleep(0.1)

    # Simulate random failure (20% chance)
    import random

    is_healthy = random.random() > 0.2

    response_time = (time.time() - start_time) * 1000

    return HealthCheckResult(
        is_healthy=is_healthy,
        status="healthy" if is_healthy else "unhealthy",
        response_time_ms=round(response_time, 2),
        details={"connection_pool": "active", "queries": 42},
        error=None if is_healthy else "Connection timeout",
    )


async def check_redis() -> HealthCheckResult:
    """Example Redis health check."""
    start_time = time.time()

    # Simulate Redis check
    await asyncio.sleep(0.05)

    # Simulate random degradation (30% chance)
    import random

    rand = random.random()
    if rand > 0.7:
        is_healthy = False
        status = "unhealthy"
        error = "Redis connection failed"
    elif rand > 0.4:
        is_healthy = True
        status = "degraded"
        error = None
    else:
        is_healthy = True
        status = "healthy"
        error = None

    response_time = (time.time() - start_time) * 1000

    return HealthCheckResult(
        is_healthy=is_healthy,
        status=status,
        response_time_ms=round(response_time, 2),
        details={"memory_usage": "45%", "connected_clients": 12},
        error=error,
    )


async def check_external_api() -> HealthCheckResult:
    """Example external API health check."""
    start_time = time.time()

    # Simulate API check
    await asyncio.sleep(0.2)

    # Always healthy for this example
    response_time = (time.time() - start_time) * 1000

    return HealthCheckResult(
        is_healthy=True,
        status="healthy",
        response_time_ms=round(response_time, 2),
        details={"api_version": "v1.2.3", "rate_limit": "950/1000"},
    )


async def main():
    """Demonstrate health status metrics integration."""
    print("🏥 Health Status Metrics Integration Example")
    print("=" * 50)

    # Initialize metrics registry
    print("\n1. Initializing metrics registry...")
    metrics_registry = initialize_metrics("example-service")
    print(f"   ✓ Metrics registry initialized for: {metrics_registry.service_name}")

    # Create health check registry
    print("\n2. Setting up health checks...")
    health_registry = HealthCheckRegistry()

    # Add health checks with different categories
    health_registry.add_check(
        HealthCheckDefinition(
            name="database",
            check_func=check_database,
            category=HealthCheckCategory.CRITICAL,
            timeout_seconds=5.0,
        )
    )

    health_registry.add_check(
        HealthCheckDefinition(
            name="redis_cache",
            check_func=check_redis,
            category=HealthCheckCategory.IMPORTANT,
            timeout_seconds=3.0,
        )
    )

    health_registry.add_check(
        HealthCheckDefinition(
            name="external_api",
            check_func=check_external_api,
            category=HealthCheckCategory.INFORMATIONAL,
            timeout_seconds=10.0,
        )
    )

    print("   ✓ Health checks registered:")
    print("     - database (CRITICAL)")
    print("     - redis_cache (IMPORTANT)")
    print("     - external_api (INFORMATIONAL)")

    # Run health checks multiple times to demonstrate metrics
    print("\n3. Running health checks and updating metrics...")

    for i in range(5):
        print(f"\n   Run {i+1}:")

        # Run comprehensive health checks (all categories)
        results = await health_registry.run_checks_for_type(HealthCheckType.DEEP)

        print(f"     Overall Status: {results['status']}")
        print("     Individual Checks:")

        for check_name, check_result in results["checks"].items():
            status = "✓" if check_result["healthy"] else "✗"
            response_time = check_result.get("response_time_ms", 0)
            print(f"       {status} {check_name}: {check_result['status']} ({response_time:.1f}ms)")

        # Wait a bit between runs
        await asyncio.sleep(1)

    print("\n4. Metrics that would be available in /metrics endpoint:")
    print('   📊 service_health_status{service="example-service"}')
    print("      - 3=healthy, 2=degraded, 1=unhealthy, 0=unknown")
    print(
        '   📊 health_check_status{service="example-service",check_name="...",check_category="..."}'
    )
    print("      - 1=healthy, 0=unhealthy")
    print(
        '   📊 health_check_duration_seconds{service="example-service",check_name="...",check_category="..."}'
    )
    print("      - Histogram of check execution times")
    print(
        '   📊 health_check_executions_total{service="example-service",check_name="...",check_category="...",status="..."}'
    )
    print("      - Counter of check executions by status")

    print("\n5. Grafana Query Examples:")
    print("   # Overall service health status")
    print('   service_health_status{service="example-service"}')
    print()
    print("   # Individual check health (replace blackbox complexity)")
    print('   health_check_status{service="example-service"}')
    print()
    print("   # Check response times")
    print(
        "   rate(health_check_duration_seconds_sum[5m]) / rate(health_check_duration_seconds_count[5m])"
    )
    print()
    print("   # Check failure rate")
    print('   rate(health_check_executions_total{status="unhealthy"}[5m])')

    print("\n🎉 Example completed! Health status metrics are now integrated.")
    print("   Use these metrics in Grafana instead of complex Blackbox JSON parsing.")


if __name__ == "__main__":
    asyncio.run(main())
