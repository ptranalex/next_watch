#!/usr/bin/env python3
"""Demo script showing cache warming functionality."""

import asyncio
import time

from cache import CacheManager, get_global_collector, set_metrics_enabled
from cache.decorators import redis_cache
from cache.warming import WarmingConfig, WarmingEngine, WarmingStrategy

# Enable metrics for the demo
set_metrics_enabled(True)


@redis_cache(ttl=300, enable_metrics=True)
async def expensive_function(item_id: int, category: str = "default") -> dict:
    """Simulate an expensive function that benefits from caching."""
    # Simulate expensive work
    await asyncio.sleep(0.1)  # 100ms delay

    return {
        "item_id": item_id,
        "category": category,
        "data": f"Expensive computation result for {item_id}",
        "timestamp": time.time(),
    }


@redis_cache(ttl=600, enable_metrics=True)
async def another_expensive_function(user_id: int) -> dict:
    """Another expensive function for demo."""
    await asyncio.sleep(0.05)  # 50ms delay

    return {"user_id": user_id, "profile": f"User profile for {user_id}", "timestamp": time.time()}


async def simulate_traffic():
    """Simulate some traffic to generate metrics."""
    print("🚀 Simulating traffic to generate cache metrics...")

    # Call functions multiple times to generate metrics
    tasks = []

    # Popular items (will have high hit rates after first call)
    for i in range(5):
        for item_id in [1, 2, 3]:  # Popular items
            tasks.append(expensive_function(item_id, "popular"))

        for user_id in [101, 102]:  # Popular users
            tasks.append(another_expensive_function(user_id))

    # Less popular items (will have lower hit rates)
    for item_id in range(10, 20):
        tasks.append(expensive_function(item_id, "rare"))

    await asyncio.gather(*tasks)
    print(f"✅ Completed {len(tasks)} function calls")


async def demonstrate_warming():
    """Demonstrate the cache warming system."""
    print("\n" + "=" * 60)
    print("🔥 CACHE WARMING DEMONSTRATION")
    print("=" * 60)

    # Initialize cache and warming
    cache_manager = CacheManager.from_settings()
    metrics_collector = get_global_collector()

    # Configure warming with lower thresholds for demo
    config = WarmingConfig(
        min_miss_rate_threshold=0.1,  # Lower threshold for demo
        min_avg_miss_time_ms=30.0,  # Lower threshold for demo
        min_total_calls=3,  # Lower threshold for demo
        max_concurrent_operations=3,
        max_items_per_strategy=10,
    )

    warming_engine = WarmingEngine(
        cache_manager=cache_manager, metrics_collector=metrics_collector, config=config
    )

    # Register warming functions
    warming_engine.register_warming_function("expensive_function", expensive_function)
    warming_engine.register_warming_function(
        "another_expensive_function", another_expensive_function
    )

    print("\n📊 Current metrics before warming:")
    all_metrics = metrics_collector.get_all_metrics()
    for func_name, metrics in all_metrics.items():
        print(f"  {func_name}:")
        print(f"    Total calls: {metrics.total_calls}")
        print(f"    Miss rate: {metrics.miss_rate:.1%}")
        print(f"    Avg miss time: {metrics.avg_cache_miss_time:.1f}ms")
        print(f"    Avg hit time: {metrics.avg_cache_hit_time:.1f}ms")

    print("\n🔥 Starting metrics-driven warming...")

    # Perform warming
    start_time = time.time()
    stats = await warming_engine.warm_by_strategy(
        strategy=WarmingStrategy.METRICS_DRIVEN, limit=10, dry_run=False
    )
    warming_time = time.time() - start_time

    print(f"\n✅ Warming completed in {warming_time:.2f}s")
    print("📈 Warming Statistics:")
    print(f"  Total targets: {stats.total_targets}")
    print(f"  Successful: {stats.successful_targets}")
    print(f"  Failed: {stats.failed_targets}")
    print(f"  Success rate: {stats.success_rate:.1%}")
    print(f"  Total execution time: {stats.total_execution_time_ms:.1f}ms")
    print(f"  Average execution time: {stats.average_execution_time_ms:.1f}ms")

    # Show warming history
    history = warming_engine.get_warming_history()
    if history:
        print(f"\n📋 Warming History ({len(history)} operations):")
        for result in history[-5:]:  # Show last 5
            status_emoji = "✅" if result.success else "❌"
            print(f"  {status_emoji} {result.target.function_name} - {result.status.value}")
            if result.error:
                print(f"    Error: {result.error}")

    print("\n🎯 Warming demonstration complete!")
    print("The cache is now pre-populated with data based on usage patterns.")


async def main():
    """Main demo function."""
    print("🔥 NextWatch Cache Warming Demo")
    print("This demo shows how cache warming uses metrics to improve performance")

    # Step 1: Generate some traffic and metrics
    await simulate_traffic()

    # Step 2: Demonstrate warming
    await demonstrate_warming()

    print("\n" + "=" * 60)
    print("Demo complete! 🎉")
    print("Key benefits of cache warming:")
    print("• Eliminates cold cache penalties")
    print("• Uses real metrics to guide decisions")
    print("• Improves user experience with faster responses")
    print("• Runs in background without affecting normal operations")


if __name__ == "__main__":
    asyncio.run(main())
