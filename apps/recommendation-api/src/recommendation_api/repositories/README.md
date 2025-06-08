***REMOVED*** Repositories Module

This module implements the Repository pattern for data access, providing a clean abstraction layer between the business logic and data storage systems.

***REMOVED******REMOVED*** Overview

The repositories module provides:

- **Data Access Abstraction**: Clean interfaces for different data stores
- **Repository Pattern**: Encapsulates data access logic and queries
- **Multiple Storage Types**: Support for relational, cache, and vector databases
- **Connection Management**: Proper connection handling and resource cleanup
- **Query Optimization**: Efficient data retrieval and storage operations

***REMOVED******REMOVED*** Architecture

The repositories module follows the Repository pattern with specialized repositories for different data types:

```
repositories/
├── __init__.py         ***REMOVED*** Module exports and repository registry
├── redis/              ***REMOVED*** Redis cache repository
│   ├── __init__.py     ***REMOVED*** Redis repository exports
│   ├── base.py         ***REMOVED*** Base Redis repository class
│   ├── cache.py        ***REMOVED*** Caching operations
│   └── session.py      ***REMOVED*** Redis session management
└── vector/             ***REMOVED*** Vector database repository
    ├── __init__.py     ***REMOVED*** Vector repository exports
    ├── base.py         ***REMOVED*** Base vector repository class
    ├── qdrant.py       ***REMOVED*** Qdrant-specific implementation
    └── operations.py   ***REMOVED*** Vector operations (search, store, etc.)
```

***REMOVED******REMOVED*** Repository Types

***REMOVED******REMOVED******REMOVED*** Redis Repository (`redis/`)

Handles caching and session data using Redis:

```python
from recommendation_api.repositories.redis import RedisRepository

***REMOVED*** Get repository instance
redis_repo = RedisRepository()

***REMOVED*** Cache operations
await redis_repo.set("key", value, ttl=3600)
cached_value = await redis_repo.get("key")

***REMOVED*** Batch operations
await redis_repo.mset({"key1": "value1", "key2": "value2"})
values = await redis_repo.mget(["key1", "key2"])
```

**Features:**

- **Caching**: Store and retrieve cached data with TTL
- **Session Management**: User session storage and retrieval
- **Batch Operations**: Efficient bulk operations
- **Connection Pooling**: Managed Redis connection pool
- **Serialization**: Automatic JSON serialization/deserialization

**Use Cases:**

- API response caching
- User session storage
- Temporary data storage
- Rate limiting counters
- Feature flags

***REMOVED******REMOVED******REMOVED*** Vector Repository (`vector/`)

Handles vector embeddings and similarity search using Qdrant:

```python
from recommendation_api.repositories.vector import VectorRepository

***REMOVED*** Get repository instance
vector_repo = VectorRepository()

***REMOVED*** Store movie embedding
await vector_repo.store_movie_embedding(
    movie_id=123,
    embedding=[0.1, 0.2, 0.3, ...],
    metadata={"title": "The Matrix", "year": 1999}
)

***REMOVED*** Search for similar movies
similar_movies = await vector_repo.search_similar_movies(
    embedding=[0.1, 0.2, 0.3, ...],
    limit=10,
    score_threshold=0.8
)
```

**Features:**

- **Vector Storage**: Store high-dimensional embeddings
- **Similarity Search**: Fast approximate nearest neighbor search
- **Metadata Filtering**: Filter results by movie attributes
- **Batch Operations**: Bulk embedding storage and retrieval
- **Collection Management**: Manage vector collections and indexes

**Use Cases:**

- Movie similarity search
- Content-based recommendations
- Semantic search
- Clustering and classification
- Duplicate detection

***REMOVED******REMOVED*** Repository Pattern Implementation

***REMOVED******REMOVED******REMOVED*** Base Repository Interface

All repositories implement a common interface:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseRepository(ABC):
    """Base repository interface."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data store."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data store."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the data store."""
        pass
```

***REMOVED******REMOVED******REMOVED*** Repository Registry

The module provides a registry for managing repository instances:

```python
from recommendation_api.repositories import get_repository

***REMOVED*** Get specific repository
redis_repo = get_repository("redis")
vector_repo = get_repository("vector")

***REMOVED*** Get all repositories
all_repos = get_repository("all")
```

***REMOVED******REMOVED*** Connection Management

***REMOVED******REMOVED******REMOVED*** Redis Connection

Redis connections are managed through connection pooling:

```python
from recommendation_api.repositories.redis import get_redis_pool

***REMOVED*** Get connection pool
pool = get_redis_pool()

***REMOVED*** Use connection
async with pool.get_connection() as conn:
    await conn.set("key", "value")
    value = await conn.get("key")
```

**Configuration:**

- Connection pooling with configurable pool size
- Automatic reconnection on connection loss
- Health checks and monitoring
- SSL/TLS support for production

***REMOVED******REMOVED******REMOVED*** Vector Database Connection

Qdrant connections are managed through the Qdrant client:

```python
from recommendation_api.repositories.vector import get_qdrant_client

***REMOVED*** Get Qdrant client
client = get_qdrant_client()

***REMOVED*** Use client for operations
collections = await client.get_collections()
```

**Configuration:**

- HTTP/gRPC client configuration
- Connection timeout and retry settings
- Collection and index management
- Authentication and security

***REMOVED******REMOVED*** Data Models

***REMOVED******REMOVED******REMOVED*** Redis Data Models

Redis repositories use structured data models:

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CacheEntry(BaseModel):
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: datetime
    accessed_at: Optional[datetime] = None

class UserSession(BaseModel):
    user_id: int
    session_id: str
    data: Dict[str, Any]
    expires_at: datetime
```

***REMOVED******REMOVED******REMOVED*** Vector Data Models

Vector repositories use embedding-specific models:

```python
from pydantic import BaseModel
from typing import List, Dict, Any

class MovieEmbedding(BaseModel):
    movie_id: int
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    model_version: str

class SimilarityResult(BaseModel):
    movie_id: int
    score: float
    metadata: Dict[str, Any]
```

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Caching Recommendations

```python
from recommendation_api.repositories.redis import RedisRepository

async def cache_recommendations(user_id: int, recommendations: List[Dict]):
    redis_repo = RedisRepository()
    cache_key = f"recommendations:user:{user_id}"

    await redis_repo.set(
        cache_key,
        recommendations,
        ttl=3600  ***REMOVED*** 1 hour
    )

async def get_cached_recommendations(user_id: int) -> Optional[List[Dict]]:
    redis_repo = RedisRepository()
    cache_key = f"recommendations:user:{user_id}"

    return await redis_repo.get(cache_key)
```

***REMOVED******REMOVED******REMOVED*** Vector Similarity Search

```python
from recommendation_api.repositories.vector import VectorRepository

async def find_similar_movies(movie_id: int, limit: int = 10) -> List[Dict]:
    vector_repo = VectorRepository()

    ***REMOVED*** Get movie embedding
    movie_embedding = await vector_repo.get_movie_embedding(movie_id)

    if not movie_embedding:
        return []

    ***REMOVED*** Search for similar movies
    similar_movies = await vector_repo.search_similar_movies(
        embedding=movie_embedding.embedding,
        limit=limit,
        score_threshold=0.7
    )

    return [
        {
            "movie_id": result.movie_id,
            "similarity_score": result.score,
            "metadata": result.metadata
        }
        for result in similar_movies
    ]
```

***REMOVED******REMOVED*** Error Handling

Repositories implement comprehensive error handling:

```python
from recommendation_api.repositories.exceptions import (
    RepositoryError,
    ConnectionError,
    DataNotFoundError,
    ValidationError
)

try:
    result = await redis_repo.get("nonexistent_key")
except DataNotFoundError:
    ***REMOVED*** Handle missing data
    result = None
except ConnectionError:
    ***REMOVED*** Handle connection issues
    logger.error("Redis connection failed")
    raise
except RepositoryError as e:
    ***REMOVED*** Handle general repository errors
    logger.error(f"Repository error: {e}")
    raise
```

***REMOVED******REMOVED*** Testing

Repositories are designed for easy testing with mock implementations:

```python
import pytest
from unittest.mock import AsyncMock
from recommendation_api.repositories.redis import RedisRepository

@pytest.fixture
def mock_redis_repo():
    repo = RedisRepository()
    repo.client = AsyncMock()
    return repo

async def test_cache_operations(mock_redis_repo):
    ***REMOVED*** Test set operation
    await mock_redis_repo.set("test_key", "test_value")
    mock_redis_repo.client.set.assert_called_once()

    ***REMOVED*** Test get operation
    mock_redis_repo.client.get.return_value = "test_value"
    result = await mock_redis_repo.get("test_key")
    assert result == "test_value"
```

***REMOVED******REMOVED*** Performance Considerations

***REMOVED******REMOVED******REMOVED*** Redis Performance

- **Connection Pooling**: Use connection pools to avoid connection overhead
- **Pipelining**: Batch operations for better throughput
- **Compression**: Compress large values to reduce memory usage
- **TTL Management**: Set appropriate TTL values to prevent memory bloat

***REMOVED******REMOVED******REMOVED*** Vector Database Performance

- **Batch Operations**: Store embeddings in batches for better performance
- **Index Optimization**: Configure appropriate vector indexes
- **Memory Management**: Monitor memory usage for large embedding collections
- **Query Optimization**: Use metadata filters to reduce search space

***REMOVED******REMOVED*** Monitoring and Health Checks

All repositories implement health check methods:

```python
***REMOVED*** Check repository health
redis_health = await redis_repo.health_check()
vector_health = await vector_repo.health_check()

***REMOVED*** Health check response format
{
    "status": "healthy",
    "response_time_ms": 15,
    "details": {
        "connected": True,
        "pool_size": 10,
        "active_connections": 3
    }
}
```

***REMOVED******REMOVED*** Future Enhancements

Planned improvements for the repositories module:

1. **Database Repository**: Add PostgreSQL repository for relational data
2. **Elasticsearch Repository**: Add full-text search capabilities
3. **S3 Repository**: Add object storage for large files
4. **Metrics Collection**: Add performance metrics and monitoring
5. **Circuit Breaker**: Implement circuit breaker pattern for resilience
6. **Caching Strategies**: Advanced caching patterns (write-through, write-behind)
7. **Sharding Support**: Horizontal scaling for large datasets
