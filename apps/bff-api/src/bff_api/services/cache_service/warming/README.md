# BFF Cache Warming Module

This module provides a production-ready cache warming implementation for the BFF API that integrates with the NextWatch Cache Library. It demonstrates best practices for implementing domain-specific cache warming while leveraging a reusable warming framework.

## 🏗️ Architecture Overview

The warming module follows a **modular architecture** that cleanly separates framework responsibilities from domain-specific business logic:

```
warming/
├── service.py      # 🎯 Main orchestration service
├── functions.py    # 🔥 Cache population functions
├── providers.py    # 📊 Data sourcing for strategies
├── factories.py    # 🏭 Target generation logic
├── config.py       # ⚙️  Configuration management
└── __init__.py     # 📦 Public API surface
```

## 🎯 Core Components

### 1. **BFFWarmingService** (`service.py`)

The main orchestration service that coordinates all warming components:

```python
from bff_api.services.cache_service.warming import get_bff_warming_service

# Get the configured warming service
warming_service = get_bff_warming_service()

# Test a specific warming function
result = await warming_service.test_warming_function(
    "movie_screen",
    movie_id=1,
    user_id=None
)

# Access the warming engine for advanced operations
engine = warming_service.get_warming_engine()
```

**Key Features**:

- Auto-configures warming system on initialization
- Registers BFF-specific warming functions
- Sets up data providers and target factories
- Integrates with cache library's strategy system
- Provides health checks and testing capabilities

### 2. **BFFWarmingFunctions** (`functions.py`)

Implements warming functions that call **actual cached BFF endpoints**:

```python
async def warm_movie_screen(self, movie_id: int, user_id: Optional[int] = None, **kwargs):
    # Import the actual cached function
    from bff_api.routes.v1.movies import _get_movie_screen_data
    from bff_api.services.backend_client import BackendClient

    # Create dependencies
    backend_client = BackendClient(config=self.settings)

    # Call the cached function - this populates the cache
    warmed_data = await _get_movie_screen_data(
        movie_id=movie_id,
        user_id=user_id,
        backend=backend_client,
        credentials=None
    )

    return {"cache_populated": True, "warming_type": "movie_screen", ...}
```

**Available Functions**:

- `warm_movie_screen` - Movie detail pages
- `warm_movies_list` - Movie listing pages
- `warm_actor_screen` - Actor profile pages
- `warm_genre_screen` - Genre listing pages
- `warm_user_dashboard` - User dashboard pages
- `warm_homepage` - Homepage data

**Why This Approach Works**:

- ✅ Calls **actual cached functions** with `@redis_cache` decorator
- ✅ Populates cache with **real data**, not mock/simulation
- ✅ Reuses existing business logic and validation
- ✅ Ensures warming matches production behavior exactly

### 3. **BFFDataProviders** (`providers.py`)

Provides domain-specific data for warming strategies:

```python
# Popular content data (movies, actors, genres)
popularity_data = await data_providers.get_popularity_data()

# User-specific data (preferences, history)
user_data = await data_providers.get_user_data(user_id=123)

# Personalized recommendations
recommendations = await data_providers.get_user_recommendations(user_id=123)
```

**Data Sources**:

- **Backend API Integration**: Fetches real movie data through pagination
- **Popularity Scoring**: Calculates scores based on ratings, recency, vote counts
- **User Behavior**: Provides user preferences and viewing history
- **Recommendations**: Supplies personalized content suggestions

### 4. **BFFTargetFactories** (`factories.py`)

Generates warming targets from business data:

```python
# Create warming targets for a popular movie
movie_targets = target_factories.create_movie_targets({
    "id": 550,
    "popularity_score": 8.5,
    "view_count": 5000,
    "title": "Fight Club"
})

# Results in multiple warming targets:
# - Anonymous user view: movie_screen(movie_id=550, user_id=None)
# - Authenticated views: movie_screen(movie_id=550, user_id=1)
# - Different priorities based on popularity
```

**Target Types**:

- **Movies**: Detail pages for anonymous and authenticated users
- **Actors**: Profile pages with filmography
- **Genres**: Listing pages with different sort options

## 🚀 Usage Patterns

### Basic Usage

```python
from bff_api.services.cache_service.warming import get_bff_warming_service

# Get warming service (auto-configured)
service = get_bff_warming_service()

# Test individual warming functions
result = await service.test_warming_function("movie_screen", movie_id=1)
print(f"Cached: {result['cache_populated']}")
```

### CLI Integration

The warming system integrates with the BFF CLI:

```bash
# Use cache library's warming CLI (auto-configured with BFF data)
bff-api warming start --strategy metrics_driven --limit 50
bff-api warming status
bff-api warming stop

# Test warming functions directly
bff-api warming-test movie_screen --movie-id 1 --user-id 123
bff-api warming-test movies_list --page 1 --genre-id 28
```

### Programmatic Strategy Execution

```python
from cache.warming import WarmingStrategy

# Get the warming engine
engine = service.get_warming_engine()

# Execute different warming strategies
stats = await engine.warm_by_strategy(
    strategy=WarmingStrategy.POPULAR_CONTENT,
    limit=100,
    dry_run=False
)

print(f"Warmed {stats.successful_targets} targets")
```

### Background Warming

```python
from bff_api.services.cache_service import start_background_warming

# Start scheduled background warming
await start_background_warming()

# Runs on schedule:
# - Morning warmup (7 AM): Popular content
# - Evening warmup (5 PM): Metrics-driven
# - Night optimization (1 AM): Scheduled
# - Continuous metrics (every 10 min): Metrics-driven
```

## 🎛️ Configuration

Warming behavior can be configured via environment variables:

```bash
# Warming thresholds
WARMING_MAX_CONCURRENT=5
WARMING_MAX_ITEMS_PER_STRATEGY=100
WARMING_MIN_MISS_RATE=0.3
WARMING_MIN_AVG_MISS_TIME=100.0
WARMING_MIN_TOTAL_CALLS=10

# Strategy weights
WARMING_METRICS_DRIVEN_WEIGHT=1.0
WARMING_POPULAR_CONTENT_WEIGHT=0.8
WARMING_USER_SPECIFIC_WEIGHT=0.6
WARMING_SCHEDULED_WEIGHT=0.7
```

Or programmatically:

```python
from bff_api.services.cache_service.warming.config import get_bff_warming_config

config = get_bff_warming_config()
print(f"Max concurrent: {config.max_concurrent_operations}")
print(f"Strategies enabled: {config.enable_popular_content}")
```

## 🧩 Integration with Cache Library

### Framework Responsibilities (Cache Library)

The cache library provides the **barebone framework**:

- ✅ **Strategy orchestration** - When and how to warm
- ✅ **Concurrency management** - Threading and async coordination
- ✅ **Metrics collection** - Performance and success tracking
- ✅ **Configuration framework** - Settings and limits
- ✅ **CLI integration** - Command-line tools
- ✅ **Scheduling** - Time-based and event-driven triggers

### BFF Implementation Responsibilities

The BFF warming module provides **domain-specific logic**:

- ✅ **Business knowledge** - What content to warm
- ✅ **Data sourcing** - Backend API integration
- ✅ **Cache population** - Calling actual cached functions
- ✅ **Target generation** - Creating warming targets from business data
- ✅ **Priority calculation** - Business logic for importance scoring

### Integration Points

```python
# Register warming functions
engine.register_warming_function("movie_screen", warm_movie_screen)

# Set data providers
engine.set_popularity_provider(get_popularity_data)
engine.set_user_data_provider(get_user_data)

# Register target factories
popular_strategy.register_target_factory("movies", create_movie_targets)
```

## 📊 Monitoring & Observability

### Health Checks

```python
# Check warming service health
healthy = await service.health_check()

# Components checked:
# - Cache manager connectivity
# - Strategy availability
# - Configuration validity
```

### Logging

All warming operations include structured logging:

```python
logger.info(
    "Successfully warmed movie screen data",
    movie_id=movie_id,
    user_id=user_id,
    has_movie_data=bool(warmed_data.get("movie")),
    cast_count=len(warmed_data.get("cast", [])),
    service="bff",
    component="warming_functions",
)
```

### Metrics

Warming statistics are collected automatically:

```python
stats = await engine.warm_by_strategy(WarmingStrategy.POPULAR_CONTENT)

print(f"Total targets: {stats.total_targets}")
print(f"Successful: {stats.successful_targets}")
print(f"Failed: {stats.failed_targets}")
print(f"Duration: {stats.duration_ms}ms")
```

## 🧪 Testing

### Unit Testing Warming Functions

```python
import pytest
from bff_api.services.cache_service.warming.functions import BFFWarmingFunctions

@pytest.mark.asyncio
async def test_movie_screen_warming():
    functions = BFFWarmingFunctions()

    result = await functions.warm_movie_screen(movie_id=1, user_id=None)

    assert result["cache_populated"] is True
    assert result["warming_type"] == "movie_screen"
    assert "timestamp" in result
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_warming_service_integration():
    from bff_api.services.cache_service.warming import get_bff_warming_service

    service = get_bff_warming_service()

    # Test service health
    assert await service.health_check() is True

    # Test function registration
    engine = service.get_warming_engine()
    assert "movie_screen" in engine._warming_functions

    # Test warming execution
    result = await service.test_warming_function("movie_screen", movie_id=1)
    assert result["success"] is True
```

## 🔧 Extending the System

### Adding New Warming Functions

1. **Create the cached endpoint function**:

```python
@redis_cache(ttl=600, key_builder=my_key_builder)
async def _get_my_screen_data(param1: int, backend: BackendClient):
    # Fetch and aggregate data
    return {"data": "cached_result"}
```

2. **Add warming function**:

```python
async def warm_my_screen(self, param1: int, **kwargs):
    from my_module import _get_my_screen_data

    backend_client = BackendClient(config=self.settings)
    warmed_data = await _get_my_screen_data(param1=param1, backend=backend_client)

    return {
        "cache_populated": True,
        "warming_type": "my_screen",
        "timestamp": datetime.now().isoformat(),
    }
```

3. **Register the function**:

```python
self.engine.register_warming_function("my_screen", self.warming_functions.warm_my_screen)
```

### Adding New Content Types

1. **Extend data providers**:

```python
async def _get_popular_my_content(self, backend_client):
    # Fetch content data
    return [{"id": 1, "popularity_score": 8.0, "view_count": 1000}]
```

2. **Create target factory**:

```python
def create_my_content_targets(self, item: Dict[str, Any]) -> List[WarmingTarget]:
    return [WarmingTarget(
        function_name="my_screen",
        parameters={"param1": item["id"]},
        priority=item["popularity_score"],
        estimated_benefit=item["view_count"],
        strategy=WarmingStrategy.POPULAR_CONTENT,
    )]
```

3. **Register with strategy**:

```python
popular_strategy.register_target_factory("my_content", self.target_factories.create_my_content_targets)
```

## 🏆 Best Practices Demonstrated

1. **Real Cache Population**: Calls actual cached functions, not simulations
2. **Separation of Concerns**: Clean boundaries between framework and domain logic
3. **Strategy Pattern**: Leverages library's extensible strategy system
4. **Error Resilience**: Comprehensive error handling and fallback behavior
5. **Observability**: Rich logging, metrics, and health checks
6. **Configuration**: Environment-driven configuration with sensible defaults
7. **Testability**: Modular design enables thorough unit and integration testing

This implementation serves as a reference architecture for enterprise-grade cache warming that balances reusability with domain-specific requirements.
