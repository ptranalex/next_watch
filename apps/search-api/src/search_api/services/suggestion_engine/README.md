# Suggestion Engine Module

A comprehensive Redis-backed search suggestion service that provides advanced features like prefix matching, entity-based suggestions, ranking, and fuzzy matching fallbacks.

## Overview

This module was reorganized from a single 791-line file into a well-structured module with focused components for better maintainability and testability.

## Features

- 🔍 **Prefix Matching** - Fast lexicographical prefix searches using Redis sorted sets
- 🎯 **Entity-Based Suggestions** - Rich suggestions with movie, actor, and director metadata
- 🏆 **Advanced Ranking** - Smart scoring with exact matches prioritized
- 🔧 **Fuzzy Matching** - Fallback strategies for partial word matching
- ⚡ **Performance Optimized** - Batch operations, caching, and time budgets
- 🛡️ **Graceful Degradation** - Continues working even if Redis is unavailable

## Module Structure

```
suggestion_engine/
├── __init__.py          # Public API exports
├── README.md           # This documentation
├── core.py             # Main SuggestionEngine class
├── matching.py         # Prefix & substring matching strategies
├── hydration.py        # Entity data fetching & enrichment
├── ranking.py          # Suggestion ranking & scoring algorithms
└── utils.py            # Helper functions & constants
```

### Component Responsibilities

| Component      | Lines | Purpose                                                     |
| -------------- | ----- | ----------------------------------------------------------- |
| `core.py`      | 389   | Main orchestration, public API, Redis connection management |
| `matching.py`  | 216   | Search strategies (lexicographic, SCAN, substring matching) |
| `hydration.py` | 287   | Entity data fetching, batch processing, enrichment          |
| `ranking.py`   | 108   | Suggestion sorting, scoring, and metadata enhancement       |
| `utils.py`     | 60    | Shared constants, helper functions, normalization           |

## Quick Start

```python
from search_api.services.suggestion_engine import SuggestionEngine

# Initialize the engine
engine = SuggestionEngine(
    redis_url="redis://localhost:6379/0",
    max_connections=10,
    suggestion_cache_ttl=900
)

# Initialize connection (call during app startup)
await engine.initialize()

# Get basic suggestions
suggestions = await engine.get_suggestions("inter", limit=5)
# Returns: ["interstellar", "inception", "interview"]

# Get rich entity suggestions
entity_suggestions = await engine.get_entity_suggestions("inter", limit=5)
# Returns: [
#   {
#     "text": "Interstellar",
#     "type": "movie",
#     "id": 157336,
#     "image_path": "https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg",
#     "year": 2014,
#     "popularity": 85.5,
#     "additional_info": {...}
#   },
#   ...
# ]

# Get ranked suggestions with fuzzy matching
ranked = await engine.get_ranked_suggestions("batman dark", limit=10)

# Health check
health = await engine.health_check()

# Shutdown (call during app teardown)
await engine.shutdown()
```

## API Reference

### SuggestionEngine

Main class that orchestrates all suggestion functionality.

#### Constructor Parameters

```python
SuggestionEngine(
    redis_url: str,                          # Redis connection URL
    max_connections: int = 10,               # Max Redis connections
    suggestion_key_prefix: str = "suggestions:",  # Redis key prefix
    entity_key_prefix: str = "entity:",      # Entity key prefix
    search_result_prefix: str = "search_results:",  # Results prefix
    entity_types: List[str] | None = None,   # Entity types to search
    suggestion_cache_ttl: int = 900,         # Cache TTL in seconds
    substring_min_length: int = 3,           # Min length for substring search
    substring_time_budget_ms: int = 80,      # Time budget for substring ops
    substring_scan_page_limit: int = 5       # Max pages to scan
)
```

#### Core Methods

##### `get_suggestions(query: str, limit: int = 10) -> List[str]`

Get basic text suggestions matching the query prefix.

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of suggestions to return

**Returns:** List of suggestion strings

**Example:**

```python
suggestions = await engine.get_suggestions("bat", 5)
# ["batman", "batman begins", "batman returns", ...]
```

##### `get_entity_suggestions(query: str, limit: int = 10) -> List[Dict[str, Any]]`

Get rich entity suggestions with metadata (movies, actors, directors).

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of suggestions to return

**Returns:** List of suggestion objects with entity details

**Example:**

```python
entities = await engine.get_entity_suggestions("batman", 3)
# [
#   {
#     "text": "Batman",
#     "type": "movie",
#     "id": 268,
#     "image_path": "https://image.tmdb.org/t/p/w500/...",
#     "year": 1989,
#     "popularity": 45.2,
#     "additional_info": {
#       "director": "Tim Burton",
#       "genre": ["Action", "Crime"]
#     }
#   },
#   ...
# ]
```

##### `get_ranked_suggestions(query: str, limit: int = 10, fallback_to_fuzzy: bool = True) -> List[Dict[str, Any]]`

Get ranked suggestions with advanced scoring and fuzzy matching.

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of suggestions to return
- `fallback_to_fuzzy`: Enable fuzzy matching fallback

**Returns:** List of ranked suggestion objects with search metadata

**Additional Fields:**

- `search_type`: "exact", "partial", or "fuzzy"
- `is_partial`: Boolean indicating partial match

##### `health_check() -> Dict[str, Any]`

Check Redis connection health and return status information.

**Returns:**

```python
{
    "status": "healthy",
    "redis_url": "redis://localhost:6379/0",
    "redis_version": "6.2.0",
    "max_connections": 10,
    "features": {
        "prefix_matching": True,
        "entity_lookup": True,
        "fuzzy_matching": True,
        "suggestion_caching": True
    }
}
```

#### Lifecycle Methods

##### `initialize() -> None`

Initialize Redis connection pool. Call during application startup.

##### `shutdown() -> None`

Close Redis connection pool. Call during application shutdown.

## Redis Data Structure

The engine expects specific Redis key patterns:

### Suggestion Keys

```
suggestions:batman -> "268"              # suggestion -> entity ID
suggestions:batman begins -> "272"
suggestions:christopher nolan -> "525"
```

### Entity Metadata Keys

```
suggestions_meta:batman -> "movie:268"   # suggestion -> type:id
suggestions_meta:christopher nolan -> "director:525"
```

### Entity Data Keys

```
entity:id:268 -> {"title": "Batman", "type": "movie", ...}
entity:movie:batman -> {"id": 268, "title": "Batman", ...}
entity:actor:christian bale -> {"id": 3894, "name": "Christian Bale", ...}
entity:director:christopher nolan -> {"id": 525, "name": "Christopher Nolan", ...}
```

### Suggestion Index

```
suggestions (ZSET) -> lexicographically ordered suggestion strings
```

## Performance Considerations

### Caching

- Suggestion results are cached with configurable TTL (default: 15 minutes)
- Cache keys: `cache:suggestions:{query}:{limit}`
- Failed cache operations don't break functionality

### Time Budgets

- Substring matching has configurable time budget (default: 80ms)
- SCAN operations are limited by page count (default: 5 pages)
- Automatic fallback to faster methods on timeout

### Batch Operations

- Entity hydration uses Redis pipelines for efficiency
- Bulk metadata fetching reduces round trips
- Concurrent scanning across entity types

### Graceful Degradation

- Returns empty results if Redis is unavailable
- Continues with partial results on errors
- Logs performance warnings for optimization

## Error Handling

The module uses decorators from `fast_core.errors`:

- `@critical_service_handler`: For connection management (initialize/shutdown)
- `@optional_service_handler`: For search operations (graceful fallback)

### Error Scenarios

1. **Redis Unavailable**: Returns empty lists, logs warnings
2. **Timeout**: Returns partial results within time budget
3. **Malformed Data**: Skips bad entries, continues processing
4. **Cache Failures**: Degrades to direct Redis queries

## Configuration Examples

### Basic Configuration

```python
engine = SuggestionEngine(
    redis_url="redis://localhost:6379/0"
)
```

### Production Configuration

```python
engine = SuggestionEngine(
    redis_url="redis://redis-cluster:6379/0",
    max_connections=50,
    suggestion_cache_ttl=1800,  # 30 minutes
    substring_time_budget_ms=100,
    substring_scan_page_limit=10
)
```

### Development Configuration

```python
engine = SuggestionEngine(
    redis_url="redis://localhost:6379/1",
    max_connections=5,
    suggestion_cache_ttl=300,   # 5 minutes
    substring_min_length=2,     # More aggressive matching
    substring_time_budget_ms=200
)
```

## Testing

The module is designed for easy testing with dependency injection:

```python
# Mock Redis for unit tests
from unittest.mock import AsyncMock

# Test individual components
from suggestion_engine.matching import MatchingStrategies
from suggestion_engine.hydration import EntityHydrator
from suggestion_engine.ranking import SuggestionRanker

# Integration testing with test Redis instance
engine = SuggestionEngine("redis://localhost:6379/15")  # Test DB
```

## Migration Notes

This module maintains 100% API compatibility with the original monolithic implementation:

- All public methods have identical signatures
- Return types and data structures unchanged
- Import paths remain the same
- Configuration parameters preserved

## Contributing

When modifying this module:

1. **Keep components focused** - Each file should have a single responsibility
2. **Maintain API compatibility** - Don't break existing interfaces
3. **Add comprehensive logging** - Use structured logging for debugging
4. **Include type hints** - All public APIs should be fully typed
5. **Write tests** - Test individual components and integration scenarios
6. **Update documentation** - Keep this README current with changes

## Related Modules

- **`../indexing/`** - Data population and index building (build-time)
- **`suggestion_engine/`** - Search and retrieval operations (runtime)

These modules work together but serve different phases of the search workflow.

## Dependencies

- `redis.asyncio` - Async Redis client
- `config.logging` - Application logging
- `fast_core.errors` - Error handling decorators
- `json` - Data serialization
- `asyncio` - Async operations
- `time` - Performance monitoring
- `typing` - Type annotations
