***REMOVED*** Suggestion Engine Module

A comprehensive Redis-backed search suggestion service that provides advanced features like prefix matching, entity-based suggestions, ranking, and fuzzy matching fallbacks.

***REMOVED******REMOVED*** Overview

This module was reorganized from a single 791-line file into a well-structured module with focused components for better maintainability and testability.

***REMOVED******REMOVED*** Features

- 🔍 **Prefix Matching** - Fast lexicographical prefix searches using Redis sorted sets
- 🎯 **Entity-Based Suggestions** - Rich suggestions with movie, actor, and director metadata
- 🏆 **Advanced Ranking** - Smart scoring with exact matches prioritized
- 🔧 **Fuzzy Matching** - Fallback strategies for partial word matching
- ⚡ **Performance Optimized** - Batch operations, caching, and time budgets
- 🛡️ **Graceful Degradation** - Continues working even if Redis is unavailable

***REMOVED******REMOVED*** Module Structure

```
suggestion_engine/
├── __init__.py          ***REMOVED*** Public API exports
├── README.md           ***REMOVED*** This documentation
├── core.py             ***REMOVED*** Main SuggestionEngine class
├── matching.py         ***REMOVED*** Prefix & substring matching strategies
├── hydration.py        ***REMOVED*** Entity data fetching & enrichment
├── ranking.py          ***REMOVED*** Suggestion ranking & scoring algorithms
└── utils.py            ***REMOVED*** Helper functions & constants
```

***REMOVED******REMOVED******REMOVED*** Component Responsibilities

| Component      | Lines | Purpose                                                     |
| -------------- | ----- | ----------------------------------------------------------- |
| `core.py`      | 389   | Main orchestration, public API, Redis connection management |
| `matching.py`  | 216   | Search strategies (lexicographic, SCAN, substring matching) |
| `hydration.py` | 287   | Entity data fetching, batch processing, enrichment          |
| `ranking.py`   | 108   | Suggestion sorting, scoring, and metadata enhancement       |
| `utils.py`     | 60    | Shared constants, helper functions, normalization           |

***REMOVED******REMOVED*** Quick Start

```python
from search_api.services.suggestion_engine import SuggestionEngine

***REMOVED*** Initialize the engine
engine = SuggestionEngine(
    redis_url="redis://localhost:6379/0",
    max_connections=10,
    suggestion_cache_ttl=900
)

***REMOVED*** Initialize connection (call during app startup)
await engine.initialize()

***REMOVED*** Get basic suggestions
suggestions = await engine.get_suggestions("inter", limit=5)
***REMOVED*** Returns: ["interstellar", "inception", "interview"]

***REMOVED*** Get rich entity suggestions
entity_suggestions = await engine.get_entity_suggestions("inter", limit=5)
***REMOVED*** Returns: [
***REMOVED***   {
***REMOVED***     "text": "Interstellar",
***REMOVED***     "type": "movie",
***REMOVED***     "id": 157336,
***REMOVED***     "image_path": "https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg",
***REMOVED***     "year": 2014,
***REMOVED***     "popularity": 85.5,
***REMOVED***     "additional_info": {...}
***REMOVED***   },
***REMOVED***   ...
***REMOVED*** ]

***REMOVED*** Get ranked suggestions with fuzzy matching
ranked = await engine.get_ranked_suggestions("batman dark", limit=10)

***REMOVED*** Health check
health = await engine.health_check()

***REMOVED*** Shutdown (call during app teardown)
await engine.shutdown()
```

***REMOVED******REMOVED*** API Reference

***REMOVED******REMOVED******REMOVED*** SuggestionEngine

Main class that orchestrates all suggestion functionality.

***REMOVED******REMOVED******REMOVED******REMOVED*** Constructor Parameters

```python
SuggestionEngine(
    redis_url: str,                          ***REMOVED*** Redis connection URL
    max_connections: int = 10,               ***REMOVED*** Max Redis connections
    suggestion_key_prefix: str = "suggestions:",  ***REMOVED*** Redis key prefix
    entity_key_prefix: str = "entity:",      ***REMOVED*** Entity key prefix
    search_result_prefix: str = "search_results:",  ***REMOVED*** Results prefix
    entity_types: List[str] | None = None,   ***REMOVED*** Entity types to search
    suggestion_cache_ttl: int = 900,         ***REMOVED*** Cache TTL in seconds
    substring_min_length: int = 3,           ***REMOVED*** Min length for substring search
    substring_time_budget_ms: int = 80,      ***REMOVED*** Time budget for substring ops
    substring_scan_page_limit: int = 5       ***REMOVED*** Max pages to scan
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Core Methods

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** `get_suggestions(query: str, limit: int = 10) -> List[str]`

Get basic text suggestions matching the query prefix.

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of suggestions to return

**Returns:** List of suggestion strings

**Example:**

```python
suggestions = await engine.get_suggestions("bat", 5)
***REMOVED*** ["batman", "batman begins", "batman returns", ...]
```

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** `get_entity_suggestions(query: str, limit: int = 10) -> List[Dict[str, Any]]`

Get rich entity suggestions with metadata (movies, actors, directors).

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of suggestions to return

**Returns:** List of suggestion objects with entity details

**Example:**

```python
entities = await engine.get_entity_suggestions("batman", 3)
***REMOVED*** [
***REMOVED***   {
***REMOVED***     "text": "Batman",
***REMOVED***     "type": "movie",
***REMOVED***     "id": 268,
***REMOVED***     "image_path": "https://image.tmdb.org/t/p/w500/...",
***REMOVED***     "year": 1989,
***REMOVED***     "popularity": 45.2,
***REMOVED***     "additional_info": {
***REMOVED***       "director": "Tim Burton",
***REMOVED***       "genre": ["Action", "Crime"]
***REMOVED***     }
***REMOVED***   },
***REMOVED***   ...
***REMOVED*** ]
```

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** `get_ranked_suggestions(query: str, limit: int = 10, fallback_to_fuzzy: bool = True) -> List[Dict[str, Any]]`

Get ranked suggestions with advanced scoring and fuzzy matching.

**Parameters:**

- `query`: Search query string
- `limit`: Maximum number of suggestions to return
- `fallback_to_fuzzy`: Enable fuzzy matching fallback

**Returns:** List of ranked suggestion objects with search metadata

**Additional Fields:**

- `search_type`: "exact", "partial", or "fuzzy"
- `is_partial`: Boolean indicating partial match

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** `health_check() -> Dict[str, Any]`

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

***REMOVED******REMOVED******REMOVED******REMOVED*** Lifecycle Methods

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** `initialize() -> None`

Initialize Redis connection pool. Call during application startup.

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** `shutdown() -> None`

Close Redis connection pool. Call during application shutdown.

***REMOVED******REMOVED*** Redis Data Structure

The engine expects specific Redis key patterns:

***REMOVED******REMOVED******REMOVED*** Suggestion Keys

```
suggestions:batman -> "268"              ***REMOVED*** suggestion -> entity ID
suggestions:batman begins -> "272"
suggestions:christopher nolan -> "525"
```

***REMOVED******REMOVED******REMOVED*** Entity Metadata Keys

```
suggestions_meta:batman -> "movie:268"   ***REMOVED*** suggestion -> type:id
suggestions_meta:christopher nolan -> "director:525"
```

***REMOVED******REMOVED******REMOVED*** Entity Data Keys

```
entity:id:268 -> {"title": "Batman", "type": "movie", ...}
entity:movie:batman -> {"id": 268, "title": "Batman", ...}
entity:actor:christian bale -> {"id": 3894, "name": "Christian Bale", ...}
entity:director:christopher nolan -> {"id": 525, "name": "Christopher Nolan", ...}
```

***REMOVED******REMOVED******REMOVED*** Suggestion Index

```
suggestions (ZSET) -> lexicographically ordered suggestion strings
```

***REMOVED******REMOVED*** Performance Considerations

***REMOVED******REMOVED******REMOVED*** Caching

- Suggestion results are cached with configurable TTL (default: 15 minutes)
- Cache keys: `cache:suggestions:{query}:{limit}`
- Failed cache operations don't break functionality

***REMOVED******REMOVED******REMOVED*** Time Budgets

- Substring matching has configurable time budget (default: 80ms)
- SCAN operations are limited by page count (default: 5 pages)
- Automatic fallback to faster methods on timeout

***REMOVED******REMOVED******REMOVED*** Batch Operations

- Entity hydration uses Redis pipelines for efficiency
- Bulk metadata fetching reduces round trips
- Concurrent scanning across entity types

***REMOVED******REMOVED******REMOVED*** Graceful Degradation

- Returns empty results if Redis is unavailable
- Continues with partial results on errors
- Logs performance warnings for optimization

***REMOVED******REMOVED*** Error Handling

The module uses decorators from `fast_core.errors`:

- `@critical_service_handler`: For connection management (initialize/shutdown)
- `@optional_service_handler`: For search operations (graceful fallback)

***REMOVED******REMOVED******REMOVED*** Error Scenarios

1. **Redis Unavailable**: Returns empty lists, logs warnings
2. **Timeout**: Returns partial results within time budget
3. **Malformed Data**: Skips bad entries, continues processing
4. **Cache Failures**: Degrades to direct Redis queries

***REMOVED******REMOVED*** Configuration Examples

***REMOVED******REMOVED******REMOVED*** Basic Configuration

```python
engine = SuggestionEngine(
    redis_url="redis://localhost:6379/0"
)
```

***REMOVED******REMOVED******REMOVED*** Production Configuration

```python
engine = SuggestionEngine(
    redis_url="redis://redis-cluster:6379/0",
    max_connections=50,
    suggestion_cache_ttl=1800,  ***REMOVED*** 30 minutes
    substring_time_budget_ms=100,
    substring_scan_page_limit=10
)
```

***REMOVED******REMOVED******REMOVED*** Development Configuration

```python
engine = SuggestionEngine(
    redis_url="redis://localhost:6379/1",
    max_connections=5,
    suggestion_cache_ttl=300,   ***REMOVED*** 5 minutes
    substring_min_length=2,     ***REMOVED*** More aggressive matching
    substring_time_budget_ms=200
)
```

***REMOVED******REMOVED*** Testing

The module is designed for easy testing with dependency injection:

```python
***REMOVED*** Mock Redis for unit tests
from unittest.mock import AsyncMock

***REMOVED*** Test individual components
from suggestion_engine.matching import MatchingStrategies
from suggestion_engine.hydration import EntityHydrator
from suggestion_engine.ranking import SuggestionRanker

***REMOVED*** Integration testing with test Redis instance
engine = SuggestionEngine("redis://localhost:6379/15")  ***REMOVED*** Test DB
```

***REMOVED******REMOVED*** Migration Notes

This module maintains 100% API compatibility with the original monolithic implementation:

- All public methods have identical signatures
- Return types and data structures unchanged
- Import paths remain the same
- Configuration parameters preserved

***REMOVED******REMOVED*** Contributing

When modifying this module:

1. **Keep components focused** - Each file should have a single responsibility
2. **Maintain API compatibility** - Don't break existing interfaces
3. **Add comprehensive logging** - Use structured logging for debugging
4. **Include type hints** - All public APIs should be fully typed
5. **Write tests** - Test individual components and integration scenarios
6. **Update documentation** - Keep this README current with changes

***REMOVED******REMOVED*** Related Modules

- **`../indexing/`** - Data population and index building (build-time)
- **`suggestion_engine/`** - Search and retrieval operations (runtime)

These modules work together but serve different phases of the search workflow.

***REMOVED******REMOVED*** Dependencies

- `redis.asyncio` - Async Redis client
- `config.logging` - Application logging
- `fast_core.errors` - Error handling decorators
- `json` - Data serialization
- `asyncio` - Async operations
- `time` - Performance monitoring
- `typing` - Type annotations
