#!/usr/bin/env python3
"""
Cache Metrics Demo

This example demonstrates the cache metrics functionality, showing:
1. How metrics are automatically collected
2. How to view performance data
3. Cache hit/miss ratios and timing information
"""

import asyncio
import time
from typing import Any

from cache import get_global_collector, redis_cache
from cache.manager import CacheManager


# Mock expensive operations
async def expensive_database_query(user_id: int) -> dict[str, Any]:
    """Simulate an expensive database query."""
    await asyncio.sleep(0.1)  # 100ms delay
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": "2024-01-01T00:00:00Z",
    }


async def expensive_api_call(product_id: int) -> dict[str, Any]:
    """Simulate an expensive external API call."""
    await asyncio.sleep(0.05)  # 50ms delay
    return {
        "product_id": product_id,
        "name": f"Product {product_id}",
        "price": 99.99,
        "in_stock": True,
    }


# Cached functions
@redis_cache(ttl=300, key_prefix="user")
async def get_user_profile(user_id: int) -> dict[str, Any]:
    """Get user profile with caching."""
    return await expensive_database_query(user_id)


@redis_cache(ttl=600, key_prefix="product")
async def get_product_details(product_id: int) -> dict[str, Any]:
    """Get product details with caching."""
    return await expensive_api_call(product_id)


async def simulate_traffic() -> None:
    """Simulate realistic application traffic patterns."""
    print("🚀 Simulating application traffic...")

    # Simulate various access patterns
    tasks = []

    # Popular users (will have high cache hit rates)
    popular_users = [1, 2, 3]
    for _ in range(10):
        for user_id in popular_users:
            tasks.append(get_user_profile(user_id))

    # Less popular users (will have lower cache hit rates)
    for user_id in range(4, 20):
        tasks.append(get_user_profile(user_id))

    # Popular products
    popular_products = [101, 102, 103]
    for _ in range(8):
        for product_id in popular_products:
            tasks.append(get_product_details(product_id))

    # Various products
    for product_id in range(104, 115):
        tasks.append(get_product_details(product_id))

    # Execute all requests concurrently
    print(f"📊 Executing {len(tasks)} requests...")
    start_time = time.time()

    results = await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"✅ Completed {len(results)} requests in {end_time - start_time:.2f} seconds")


def display_metrics() -> None:
    """Display comprehensive metrics information."""
    collector = get_global_collector()
    metrics = collector.get_metrics()

    if not metrics:
        print("❌ No metrics available")
        return

    print("\n" + "=" * 60)
    print("📊 CACHE PERFORMANCE METRICS")
    print("=" * 60)

    # Overall metrics
    overall = metrics["overall"]
    print("\n🎯 OVERALL PERFORMANCE:")
    print(f"   Total Calls: {overall['total_calls']}")
    print(f"   Cache Hits:  {overall['total_hits']} ({overall['hit_ratio']:.1f}%)")
    print(f"   Cache Misses: {overall['total_misses']} ({overall['miss_ratio']:.1f}%)")
    print(f"   Started: {overall['started_at']}")

    # Function-specific metrics
    functions = metrics["functions"]
    if functions:
        print("\n📈 FUNCTION PERFORMANCE:")
        print("-" * 60)

        for func_name, func_data in functions.items():
            # Extract just the function name for cleaner display
            clean_name = func_name.split(".")[-1]

            print(f"\n🔧 {clean_name}:")
            print(f"   Calls: {func_data['total_calls']}")
            print(f"   Hit Ratio: {func_data['hit_ratio']:.1f}%")
            print(f"   Avg Cache Time: {func_data['avg_cache_time_ms']:.1f}ms")
            print(f"   Avg Uncached Time: {func_data['avg_uncached_time_ms']:.1f}ms")

            if func_data["performance_improvement"] > 0:
                print(f"   Performance Gain: {func_data['performance_improvement']:.1f}x faster")

            if func_data["last_hit"]:
                print(f"   Last Hit: {func_data['last_hit']}")
            if func_data["last_miss"]:
                print(f"   Last Miss: {func_data['last_miss']}")


def display_summary() -> None:
    """Display a quick summary of cache effectiveness."""
    collector = get_global_collector()
    summary = collector.get_summary()

    if not summary:
        print("❌ No summary available")
        return

    print("\n" + "=" * 40)
    print("📋 CACHE SUMMARY")
    print("=" * 40)

    hit_ratio = summary["overall_hit_ratio"]
    if hit_ratio >= 80:
        status = "🟢 EXCELLENT"
    elif hit_ratio >= 60:
        status = "🟡 GOOD"
    elif hit_ratio >= 40:
        status = "🟠 FAIR"
    else:
        status = "🔴 POOR"

    print(f"Cache Status: {status}")
    print(f"Hit Ratio: {hit_ratio:.1f}%")
    print(f"Total Calls: {summary['total_calls']}")
    print(f"Functions Tracked: {summary['function_count']}")


async def main() -> None:
    """Main demo function."""
    print("🎬 Cache Metrics Demo")
    print("=" * 50)

    # Initialize cache manager (this would normally be done in your app startup)
    try:
        CacheManager.from_settings()
        print("✅ Cache manager initialized")
    except Exception as e:
        print(f"⚠️  Cache manager initialization failed: {e}")
        print("📝 Note: This demo requires Redis to be running")
        print("   You can still see the metrics structure with mock data")

    # Simulate application traffic
    await simulate_traffic()

    # Display metrics
    display_metrics()
    display_summary()

    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\n💡 Key Takeaways:")
    print("   • Metrics are collected automatically")
    print("   • Popular items show high cache hit rates")
    print("   • Performance improvements are clearly visible")
    print("   • Thread-safe metrics work in concurrent environments")
    print("\n🔧 Try the CLI commands:")
    print("   python -m cache.cli.metrics show")
    print("   python -m cache.cli.metrics summary")


if __name__ == "__main__":
    asyncio.run(main())
