# Recommendation API Cache Warming Module

This module provides a production-ready cache warming implementation for the Recommendation API that integrates with the NextWatch Cache Library. It demonstrates best practices for implementing domain-specific cache warming while leveraging a reusable warming framework.

## 🏗️ Architecture Overview

The warming module follows a **flattened architecture** that cleanly separates framework responsibilities from domain-specific business logic:

```Text
warming/
├── service.py              # 🎯 Main orchestration service
├── functions.py            # 🔥 Cache population functions
├── providers.py            # 📊 Data sourcing for strategies
├── factories.py            # 🏭 Target generation logic
├── config.py               # ⚙️  Configuration management
├── __init__.py             # 📦 Public API surface
└── README.md               # 📄 Documentation
```

## 🎯 Core Components

### 1. **RecommendationWarmingService** (`service.py`)

The main orchestration service that coordinates all warming components:

```python
from recommendation_api.services.cache_service.warming import get_recommendation_warming_service

# Get the configured warming service
warming_service = get_recommendation_warming_service()

# Test a specific warming function
result = await warming_service.test_warming_function(
    "similar_movies",
    movie_id=1234
)

# Access the warming engine for advanced operations
engine = warming_service.get_warming_engine()
```

**Key Features**:

- Auto-configures warming system on initialization
- Registers recommendation-specific warming functions
- Sets up data providers and target factories
- Integrates with cache library's strategy system
- Provides health checks and testing capabilities

### 2. **RecommendationWarmingFunctions** (`functions.py`)

Implements warming functions that call **actual cached endpoints**:

```python
async def warm_similar_movies(self, movie_id: int, limit: int = 20, min_score: float = 0.01):
    # Import the actual cached function
    from recommendation_api.routes.v1.similar import get_similar_movies

    # Call the cached function - this populates the cache
    similar_movies = await get_similar_movies(
        movie_id=movie_id,
        limit=limit,
        min_score=min_score,
        movie_adapter=self.movie_adapter
    )

    return {"cache_populated": True, "warming_type": "similar_movies", ...}
```

**Available Functions**:

- `warm_similar_movies` - Similar movie recommendations
- `warm_popular_movies` - Popular movie recommendations
- `warm_trending_movies` - Trending movie recommendations

**Why This Approach Works**:

- ✅ Calls **actual cached functions** with `@redis_cache` decorator
- ✅ Populates cache with **real data**, not mock/simulation
- ✅ Reuses existing business logic and validation
- ✅ Ensures warming matches production behavior exactly

### 3. **RecommendationDataProviders** (`providers.py`)

Provides domain-specific data for warming strategies:

```python
# Popular content data (movies, trending)
popularity_data = await data_providers.get_popularity_data()
```

**Data Sources**:

- **Popular Movies**: High-rated, frequently accessed movies (via `/movies/top` endpoint)
- **Trending Movies**: Recently popular movies (via `/movies/top` endpoint)
- **Recent Movies**: Recently updated movies (via `/movies` endpoint with `sort_by=release_date`)

### 4. **RecommendationTargetFactories** (`factories.py`)

Creates warming targets for different strategies:

```python
# Create targets for similar movies
similar_targets = target_factories.create_similar_movies_targets(movie_ids=[1, 2, 3])

# Create targets for popular movies with different parameters
popular_targets = target_factories.create_popular_movies_targets()

# Create targets based on popularity data
all_targets = target_factories.create_popular_content_targets(popularity_data)
```

**Factory Types**:

- **Similar Movies**: Creates targets for warming similar movie recommendations
- **Popular Movies**: Creates targets with different parameter combinations
- **Trending Movies**: Creates targets for trending movie recommendations
- **Popular Content**: Creates a comprehensive set of targets based on popularity data

## 🚀 Usage

### Basic Usage

```python
from recommendation_api.services.cache_service import configure_recommendation_warming

# Configure warming system
configure_recommendation_warming()
```

### Manual Warming

```python
from recommendation_api.services.cache_service import get_recommendation_warming_service
from cache import WarmingStrategy

warming_service = get_recommendation_warming_service()

# Warm using popular content strategy
await warming_service.warm_by_strategy(WarmingStrategy.POPULAR_CONTENT)

# Warm using metrics-driven strategy
await warming_service.warm_by_strategy(WarmingStrategy.METRICS_DRIVEN)
```

### Background Warming Service

The module includes a background warming service that periodically warms the cache:

```python
from recommendation_api.services.cache_service import (
    start_background_warming,
    stop_background_warming,
)

# Start background warming
await start_background_warming()

# Stop background warming
await stop_background_warming()
```

### Testing Functions

```python
warming_service = get_recommendation_warming_service()

# Test similar movies warming
result = await warming_service.test_warming_function(
    "similar_movies",
    movie_id=12345,
    limit=10
)
```

## 📝 Implementation Notes

- The warming module gracefully handles API limitations and falls back to alternative endpoints when needed.
- Maximum request limits are respected (50 items for `/movies/top`, 100 items for `/movies`).
- Error handling ensures the warming process continues even if individual requests fail.
- The module avoids circular dependencies by keeping the recommendation service and cache service separate.
