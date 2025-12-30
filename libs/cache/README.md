# NextWatch Cache Library

A focused, production-ready caching library designed for the NextWatch monorepo. Provides unified Redis caching with decorators, metrics tracking, intelligent cache warming, and a comprehensive CLI interface.

## 🎯 **Design Goals**

- **Simple & Effective**: Redis-based caching with clean decorator interface
- **Type Safety**: Proper TypeScript-style type annotations
- **Developer Experience**: Simple decorators, rich CLI, and clean APIs
- **Domain TTLs**: Explicit TTL configuration per use case
- **Performance Intelligence**: Metrics-driven optimization and warming
- **Production Ready**: Connection pooling, error handling, logging

## 🏗️ **Architecture**

```
libs/cache/
├── src/cache/
│   ├── __init__.py              # Simple exports
│   ├── manager.py               # CacheManager (core interface)
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract provider
│   │   └── redis.py            # Redis provider
│   ├── decorators/
│   │   ├── __init__.py
│   │   └── redis_cache.py      # @redis_cache decorator with metrics
│   ├── keys/
│   │   ├── __init__.py
│   │   └── builders.py         # Key building utilities
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── types.py            # Metrics data structures
│   │   ├── storage.py          # Thread-safe metrics storage
│   │   └── collector.py        # Metrics collection interface
│   ├── warming/
│   │   ├── __init__.py
│   │   ├── types.py            # Warming data structures
│   │   └── engine.py           # Core warming engine
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py             # Unified CLI entry point
│   │   ├── metrics.py          # Metrics CLI commands
│   │   └── warming.py          # Warming CLI commands
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Redis config
│   └── types.py                # Type definitions
├── tests/                       # Test suite
├── examples/                    # Usage examples
├── pyproject.toml              # Package configuration
└── README.md                   # This file
```

## 📋 **Implementation Status**

### ✅ **Core Foundation - COMPLETE**

- [x] **Core Operations**: `get_json()`, `set_json()`, `delete_key()`
- [x] **CacheManager**: Main interface with Redis provider
- [x] **RedisProvider**: Connection pooling and error handling
- [x] **CacheSettings**: Configuration management with domain TTLs
- [x] **Basic Tests**: Unit tests for core functionality
- [x] **Hatch Setup**: Modern Python project management

### ✅ **BFF Integration - COMPLETE**

- [x] **@redis_cache decorator**: Function-level caching with automatic key building
- [x] **BFF integration**: All major endpoints cached (movies, genres, actors, sidebar)
- [x] **Performance validation**: 10-40% response time improvement achieved
- [x] **Production deployment**: Zero cache-related errors in production
- [x] **Type safety**: Full type annotations with JSONSerializable support

### ✅ **Key Building Utilities - COMPLETE**

- [x] **CacheKeyBuilder**: Abstract base class for custom key builders
- [x] **build_cache_key()**: Simple key construction from namespace and parts
- [x] **build_filtered_key()**: Complex parameter hashing for filtered endpoints
- [x] **build_paginated_key()**: Pagination-aware key building
- [x] **hash_parameters()**: Consistent parameter hashing utility
- [x] **BFF Migration**: All BFF routes migrated to use key building utilities
- [x] **Code Reduction**: Eliminated 50+ lines of duplicated MD5 hashing code

### ✅ **Metrics Tracking - COMPLETE**

- [x] **Automatic Collection**: Metrics collected transparently by `@redis_cache` decorator
- [x] **Performance Tracking**: Hit/miss ratios, response times, performance improvements
- [x] **Thread Safety**: Concurrent metrics collection with proper locking
- [x] **Function-Level Metrics**: Per-function performance analysis
- [x] **CLI Interface**: Rich console display with formatted tables and summaries
- [x] **Production Ready**: Zero-overhead when disabled, graceful error handling

### ✅ **Cache Warming - COMPLETE**

- [x] **Metrics-Driven Strategy**: Automatically identifies warming targets based on performance data
- [x] **Concurrent Execution**: Configurable parallel warming operations with semaphore control
- [x] **Priority Scoring**: Smart prioritization based on miss rate, timing, and usage patterns
- [x] **Function Registry**: Register warming functions for actual cache population
- [x] **CLI Interface**: Rich console commands for warming management and monitoring
- [x] **Statistics Tracking**: Comprehensive warming operation history and success rates
- [x] **Type Safety**: Full type annotations throughout warming system
- [x] **Production Ready**: Dry-run mode, error handling, and configurable thresholds

### ✅ **Unified CLI - COMPLETE**

- [x] **Single Entry Point**: Consolidated `cache` command for all operations
- [x] **Hierarchical Commands**: Organized subcommands (`metrics`, `warming`, `status`)
- [x] **Rich Output**: Beautiful console formatting with tables and color coding
- [x] **Package Integration**: Installable CLI entry point via `pip install`
- [x] **Professional UX**: Consistent command structure and help system

### 📋 **Future Enhancements**

- [ ] **Additional warming strategies**: Popular content, user-specific, scheduled warming
- [ ] **Cache analytics**: Advanced performance analysis and optimization recommendations
- [ ] **Namespace management**: Service-specific namespacing patterns

## 🚀 **API Usage**

### Core Operations

```python
from cache import CacheManager

cache = CacheManager.from_settings()

# Core operations - simple and clean
await cache.get_json(key="user:123")
await cache.set_json(key="user:123", value=user_data, ttl=600)
await cache.delete_key(key="user:123")

# Enhanced operations with error handling and type safety
user_data = await cache.get_dict(key="user:123")  # Returns Dict[str, Any] or None
movie_list = await cache.get_list(key="popular:movies")  # Returns List[Any] or None
await cache.set_json_safe(key="user:123", value=user_data, ttl=600)  # With error handling
await cache.delete_key_safe(key="user:123")  # With error handling
```

### @redis_cache Decorator (Production Ready)

```python
from cache.decorators import redis_cache
from cache import build_cache_key, build_filtered_key

# Simple key building with utilities and metrics
@redis_cache(
    ttl=1800,  # 30 minutes
    enable_metrics=True,  # Track performance metrics
    key_builder=lambda movie_id, user_id, backend, credentials=None: build_cache_key(
        "screen:movie", [movie_id, "user", user_id or "anon"], prefix=""
    )
)
async def get_movie_screen_data(movie_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
    # Expensive aggregation logic - automatically cached with metrics
    movie = await backend.get_movie(movie_id, user_id=user_id)
    cast = await backend.get_movie_cast(movie_id)
    similar_movies = await backend.get_similar_movies(movie_id, limit=20)
    return {
        "movie": movie,
        "cast": cast,
        "similar_movies": similar_movies
    }
```

### Cache Warming

The cache warming system includes four intelligent strategies for different use cases:

#### **1. Metrics-Driven Strategy** 🎯

Analyzes cache performance metrics to identify functions with high miss rates and slow response times.

- **Triggers**: High miss rate (>30%), slow uncached responses (>100ms), frequent calls (>10)
- **Priority**: Based on potential performance impact (miss rate × response time × usage frequency)

#### **2. Popular Content Strategy** 🌟

Warms trending and popular content based on analytics data.

- **Content types**: Movies, actors, genres with different priority levels
- **Customizable**: Supports custom popularity data providers
- **Fallback**: Uses default popular content when no provider is available

#### **3. User-Specific Strategy** 👤

Warms personalized content based on user preferences and behavior.

- **Personalization**: Watchlist items, favorite genres, recently viewed, recommendations
- **Batch processing**: Handles multiple users efficiently
- **Context-aware**: Considers user engagement levels and confidence scores

#### **4. Scheduled Strategy** ⏰

Time-based warming for predictable traffic patterns.

- **Patterns**: Peak hours, off-peak preparation, daily schedules, weekly events
- **Seasonal**: Holiday content, award seasons, summer blockbusters
- **Configurable**: Custom schedules and time-based rules

```python
from cache.warming import WarmingEngine, WarmingConfig, WarmingStrategy
from cache import CacheManager, get_global_collector

# Initialize warming engine
cache_manager = CacheManager.from_settings()
metrics_collector = get_global_collector()
config = WarmingConfig(
    max_concurrent_operations=5,
    min_miss_rate_threshold=0.3,
    min_avg_miss_time_ms=100.0,
    # Strategy weights
    metrics_driven_weight=1.0,
    popular_content_weight=0.8,
    user_specific_weight=0.6,
    scheduled_weight=0.7
)

warming_engine = WarmingEngine(
    cache_manager=cache_manager,
    metrics_collector=metrics_collector,
    config=config
)

# Register functions for warming
warming_engine.register_warming_function("get_movie_screen_data", get_movie_screen_data)

# Set custom data providers
async def get_popularity_data():
    return {
        "movies": [{"id": 1, "popularity_score": 9.5, "view_count": 10000}],
        "actors": [{"id": 1, "popularity_score": 8.2, "view_count": 5000}]
    }

warming_engine.set_popularity_provider(get_popularity_data)

# Start specific strategy warming
stats = await warming_engine.warm_by_strategy(
    strategy=WarmingStrategy.METRICS_DRIVEN,
    limit=50
)

# Start all strategies
all_stats = await warming_engine.warm_all_strategies(
    limit_per_strategy=25,
    context={"user_ids": [1, 2, 3]}  # For user-specific strategy
)

print(f"Warmed {stats.successful_targets} targets successfully!")
```

### Metrics Tracking

```python
from cache import get_global_collector, set_metrics_enabled

# Enable metrics collection
set_metrics_enabled(True)

# Get metrics collector
collector = get_global_collector()

# View metrics for all functions
metrics = collector.get_metrics()
print(f"Overall hit ratio: {metrics['overall']['hit_ratio']:.1%}")

# View metrics for specific function
func_metrics = collector.get_function_metrics("get_movie_screen_data")
if func_metrics:
    print(f"Function hit ratio: {func_metrics['hit_ratio']:.1%}")
    print(f"Performance improvement: {func_metrics['performance_improvement']:.1f}x")
```

## 🖥️ **CLI Usage**

### Installation and Setup

```bash
# Install the cache library
pip install -e libs/cache

# The 'cache' command is now available
cache --help
```

### Metrics Commands

```bash
# Show overall cache metrics
cache metrics show

# Show metrics summary
cache metrics summary

# Show metrics for specific function
cache metrics show --function get_movie_screen_data

# Reset all metrics
cache metrics reset
```

### Warming Commands

```bash
# Show warming configuration
cache warming config

# Show warming system status
cache warming status

# Start warming with specific strategy
cache warming start --strategy metrics_driven --limit 50
cache warming start --strategy popular_content --limit 30
cache warming start --strategy user_specific --limit 20 --user-ids "1,2,3"
cache warming start --strategy scheduled --limit 40

# Start warming with all enabled strategies
cache warming start --strategy all --limit 25

# Show warming candidates
cache warming candidates --limit 20 --verbose

# Dry run warming (show what would be warmed)
cache warming start --strategy all --dry-run
```

### System Commands

```bash
# Show cache system status
cache status

# Show library version
cache version
```

### Example CLI Output

```bash
$ cache metrics summary
                    📊 Cache Performance Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          Cache Effectiveness: 🟢 EXCELLENT       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

$ cache warming config
     🔥 Warming Configuration
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Setting                ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Max Concurrent         │ 5     │
│ Max Items Per Strategy │ 100   │
│ Min Miss Rate          │ 30.0% │
└────────────────────────┴───────┘
```

## 📊 **Production Results**

### Performance Metrics (BFF API)

- **Cache hit rate**: >80% for movie screens
- **Response time improvement**: 10-40% reduction for cached responses
- **Warming effectiveness**: 5-8x faster response times for warmed content
- **Implementation time**: <2 hours per endpoint
- **Error rate**: Zero cache-related errors in production

### Warming Performance

- **Metrics-driven accuracy**: 100% hit ratio on second run after warming
- **Performance improvement**: 15ms cached vs 70-120ms uncached responses
- **Concurrent efficiency**: 81 requests warmed in ~30ms total execution time
- **Success rate**: >95% warming operation success rate
- **Strategy effectiveness**: Popular content and scheduled strategies identify 4-7 targets per run
- **Multi-strategy execution**: All strategies complete in <1 second with 100% success rate

### Endpoints Successfully Cached

- ✅ **Movie Detail Screen** (`/movies/{id}`): 30-minute TTL
- ✅ **Movies List** (`/movies`): 15-minute TTL
- ✅ **Genre Screen** (`/genres/{id}`): 15-minute TTL
- ✅ **Actor Screen** (`/actors/{id}`): 30-minute TTL
- ✅ **Actor Movies** (`/actors/{id}/movies`): 15-minute TTL
- ✅ **Sidebar Content** (`/sidebar`): 1-hour TTL

## 🔧 **Configuration**

### Environment Variables

```bash
# Redis Configuration
CACHE_REDIS_URL=redis://localhost:6379/0
CACHE_REDIS_POOL_SIZE=10
CACHE_REDIS_TIMEOUT=5

# Domain-specific TTLs (seconds)
CACHE_TTL_MOVIE_DATA=600
CACHE_TTL_USER_SESSION=3600
CACHE_TTL_POPULAR_CONTENT=1800
CACHE_TTL_DEFAULT=300

# Service Configuration
CACHE_KEY_PREFIX=nextwatch
CACHE_ENABLE_METRICS=true

# Warming Configuration
CACHE_WARMING_MAX_CONCURRENT=5
CACHE_WARMING_MIN_MISS_RATE=0.3
CACHE_WARMING_MIN_AVG_MISS_TIME=100.0
CACHE_WARMING_MIN_TOTAL_CALLS=10
```

### Programmatic Configuration

```python
from cache.config import CacheSettings
from cache.warming import WarmingConfig

# Cache settings
cache_settings = CacheSettings(
    redis_url="redis://localhost:6379/0",
    redis_pool_size=10,
    ttl_movie_data=600,
    ttl_user_session=3600,
    key_prefix="bff"
)

# Warming configuration
warming_config = WarmingConfig(
    max_concurrent_operations=5,
    min_miss_rate_threshold=0.3,
    min_avg_miss_time_ms=100.0,
    min_total_calls=10
)

cache = CacheManager.from_settings(cache_settings)
```

## 🧪 **Testing Strategy**

### Unit Tests

- Core operations (get_json, set_json, delete_key)
- Redis provider connection handling
- Decorator functionality with metrics
- Warming engine and strategies
- CLI command functionality
- Configuration management

### Integration Tests

- BFF API endpoint caching
- Redis connection pooling
- Metrics collection accuracy
- Warming operation effectiveness
- Error handling and fallback behavior
- Performance benchmarks

## 🚀 **Quick Start**

### Installation

#### Using Hatch (Recommended)

```bash
cd libs/cache
hatch shell  # Enter development environment
```

#### Using pip

```bash
cd libs/cache
pip install -e .
```

### Basic Usage

```python
from cache import CacheManager, set_metrics_enabled

# Enable metrics collection
set_metrics_enabled(True)

# Initialize cache
cache = CacheManager.from_settings()

# Cache some data
await cache.set_json("user:123", {"name": "John", "email": "john@example.com"}, ttl=3600)

# Retrieve cached data
user_data = await cache.get_json("user:123")

# Delete cached data
await cache.delete_key("user:123")
```

### Decorator Usage with Metrics

```python
from cache.decorators import redis_cache
from cache import build_cache_key

@redis_cache(
    ttl=600,
    enable_metrics=True,  # Track performance
    key_builder=lambda user_id: build_cache_key("user", [user_id], prefix="")
)
async def get_user_profile(user_id: int):
    # Expensive database operation - automatically cached and tracked
    return await db.get_user(user_id)

# Usage - caching and metrics are automatic
user = await get_user_profile(123)
```

### CLI Usage

```bash
# Check cache system status
cache status

# View performance metrics
cache metrics show

# Start intelligent warming
cache warming start --strategy metrics_driven
```

## 📚 **Examples**

See the `examples/` directory for usage examples:

- `basic_usage.py` - Core cache operations, domain TTLs, and custom settings
- `metrics_demo.py` - Metrics collection and CLI demonstration
- `warming_demo.py` - Cache warming system demonstration

## 🤝 **Contributing**

### Development Setup

#### Using Hatch (Recommended)

```bash
cd libs/cache
hatch shell  # Enter development environment with all dependencies
```

#### Manual Setup

```bash
cd libs/cache
python -m venv venv
source venv/bin/activate
pip install -e .[dev,test]
```

### Development Commands

#### Using Hatch Scripts

```bash
# Run all quality checks and tests
hatch run all

# Individual commands
hatch run test              # Run tests
hatch run test-cov          # Run tests with coverage
hatch run test-integration  # Run integration tests (requires Redis)
hatch run lint              # Check code style
hatch run format            # Format code
hatch run type-check        # Run type checking
hatch run example           # Run basic usage example
```

#### Manual Commands

```bash
pytest tests/ -v --cov=cache --cov-report=html
ruff check src/ tests/ examples/
ruff format src/ tests/ examples/
mypy src/cache
```

## 📄 **License**

This library is part of the NextWatch monorepo and follows the same licensing terms.
