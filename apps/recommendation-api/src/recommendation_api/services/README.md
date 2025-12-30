# Services Layer

This package contains service classes that implement the core business logic for the Recommendation API, following the principles of Clean Architecture and the Service Layer pattern.

## Overview

The services layer sits between the API routes and data access repositories, providing:

1. **Business Logic**: Core recommendation algorithms and processing
2. **Data Orchestration**: Coordination between multiple data sources
3. **External API Integration**: Communication with ML API and other services
4. **Caching Strategy**: Intelligent caching of recommendations and embeddings
5. **Health Monitoring**: Comprehensive health checks for all dependencies

## Architecture

The services layer follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Routes Layer  │───▶│ Services Layer  │───▶│ Repositories    │
│   (FastAPI)     │    │ (Business Logic)│    │ (Data Access)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │                 │
                       │   External APIs │
                       │   (ML Service)  │
                       │                 │
                       └─────────────────┘
```

## Components

### Health Service (`health_service.py`)

Provides comprehensive health monitoring for all system dependencies:

```python
from recommendation_api.services.health_service import get_health_service

# Get the global health service instance
health_service = get_health_service()

# Check all dependencies
health_results = await health_service.check_all()

# Check specific dependency
postgres_health = await health_service.check_postgres()
redis_health = await health_service.check_redis()
qdrant_health = await health_service.check_qdrant()
```

**Features:**

- **Concurrent Checks**: All services checked in parallel using `asyncio.gather()`
- **Detailed Results**: Response times, connection details, and error information
- **Resource Management**: Proper cleanup of client connections
- **Integration**: Used by core module for application health monitoring

**Dependencies Monitored:**

- **PostgreSQL**: Database connectivity and query execution
- **Redis**: Cache connectivity and basic operations
- **Qdrant**: Vector database connectivity and collection status

### Recommendation Service (`recommendation.py`)

Implements the core recommendation algorithms and business logic:

```python
from recommendation_api.services.recommendation import RecommendationService
from sqlmodel import Session

# Create service with database session
service = RecommendationService(session)

# Get trending recommendations
recommendations, filters = service.get_trending_recommendations(
    limit=20,
    days=7,
    min_rating=7.0
)

# Get personalized recommendations for a user
recommendations, filters = service.get_user_recommendations(
    user_id=123,
    limit=20
)
```

**Features:**

- **Multiple Algorithms**: Trending, popular, personalized, and similarity-based
- **Fallback Strategies**: Graceful degradation when primary methods fail
- **Caching Integration**: Intelligent caching of recommendation results
- **Filter Support**: Dynamic filtering based on user preferences

### Vector Service (`vector_service.py`)

Manages vector embeddings and similarity search operations:

```python
from recommendation_api.services.vector_service import get_vector_service
from sqlmodel import Session

# Get the global vector service instance
vector_service = get_vector_service()

# Generate and store an embedding for a movie (uses ML API)
embedding = await vector_service.generate_and_store_movie_embedding(
    session=session,
    movie_id=123
)

# Find similar movies
similar_movies = vector_service.find_similar_movies_by_id(
    movie_id=123,
    limit=10
)
```

**Features:**

- **ML API Integration**: Delegates embedding generation to ML service
- **Vector Storage**: Manages embeddings in Qdrant vector database
- **Similarity Search**: Fast approximate nearest neighbor search
- **Batch Processing**: Efficient bulk operations for large datasets

### ML API Client (`ml_api_client.py`)

Handles communication with the external ML API service:

```python
from recommendation_api.services.ml_api_client import get_ml_api_client

# Get the ML API client
ml_client = get_ml_api_client()

# Generate an embedding for movie features
features = {
    "title": "The Matrix",
    "overview": "A computer hacker learns about the true nature of reality",
    "genres": ["Action", "Sci-Fi"]
}
embedding = await ml_client.generate_movie_embedding(features)

# Test the connection to the ML API
is_connected = await ml_client.test_connection()
```

**Features:**

- **HTTP Client**: Async HTTP communication with ML API
- **Error Handling**: Comprehensive error handling and retries
- **Connection Testing**: Health check integration
- **Resource Offloading**: Moves ML computation to dedicated service

### EmbeddingService (Deprecated)

`embedding.py` previously contained local ML functionality, but has been replaced by the ML API client:

- ⚠️ **DEPRECATED**: This module is kept for backward compatibility only
- Redirects all calls to the ML API client
- Provides warning messages to guide developers to use the ML API client directly
- No longer performs local ML computation (removed SentenceTransformer dependency)

## Integration with Core Module

The services layer integrates closely with the core module for application lifecycle management:

### Health Service Integration

```python
# In core/app.py lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    app.state.health_service = get_health_service()

    yield

    # Shutdown
    if hasattr(app.state, 'health_service') and app.state.health_service:
        app.state.health_service.close()
```

### Route Integration

```python
# In routes/health.py
@router.get("/health")
async def health_check(request: Request) -> JSONResponse:
    health_service = request.app.state.health_service
    health_results = await health_service.check_all()
    # ... process results
```

## Integration with Repositories

Services use the repository pattern for data access:

```python
# Example service using repositories
from recommendation_api.repositories.redis import RedisRepository
from recommendation_api.repositories.vector import VectorRepository

class RecommendationService:
    def __init__(self, session: Session):
        self.session = session
        self.redis_repo = RedisRepository()
        self.vector_repo = VectorRepository()

    async def get_cached_recommendations(self, user_id: int):
        cache_key = f"recommendations:user:{user_id}"
        return await self.redis_repo.get(cache_key)

    async def find_similar_movies(self, movie_id: int):
        return await self.vector_repo.search_similar_movies_by_id(movie_id)
```

## Microservices Architecture

The recommendation service now follows a microservices architecture for ML computation:

```
┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
│                   │         │                   │         │                   │
│  Recommendation   │ ◄─────► │   Vector Service  │ ◄─────► │      Qdrant       │
│     Service       │         │                   │         │  Vector Database  │
│                   │         │                   │         │                   │
└───────────────────┘         └───────────────────┘         └───────────────────┘
                                       │
                                       ▼
                              ┌───────────────────┐
                              │                   │
                              │   ML API Client   │
                              │                   │
                              └───────────────────┘
                                       │
                                       ▼
                              ┌───────────────────┐
                              │                   │
                              │      ML API       │
                              │     Service       │
                              │                   │
                              └───────────────────┘
```

**Benefits:**

- **Resource Efficiency**: Reduced memory usage in recommendation API
- **Independent Scaling**: ML workloads can scale independently
- **Specialized Hardware**: ML service can use GPU-optimized infrastructure
- **Simplified Deployment**: Fewer dependencies in main service

## Service Layer Design Principles

This services layer follows these design principles:

1. **Single Responsibility**: Each service has a clear, focused purpose
2. **Dependency Injection**: Dependencies are injected rather than created internally
3. **Interface Segregation**: Services expose only what clients need
4. **Abstraction**: Services hide implementation details from API routes
5. **Testability**: Services can be tested in isolation with mocked dependencies
6. **Microservice Architecture**: Computationally intensive tasks are offloaded to specialized services
7. **Health Monitoring**: All external dependencies are monitored for health
8. **Resource Management**: Proper lifecycle management of connections and resources

## Error Handling and Resilience

Services implement comprehensive error handling:

```python
from recommendation_api.services.exceptions import (
    ServiceError,
    ExternalServiceError,
    DataNotFoundError,
    CacheError
)

try:
    recommendations = await recommendation_service.get_user_recommendations(user_id)
except DataNotFoundError:
    # Handle missing user data
    recommendations = await recommendation_service.get_popular_recommendations()
except ExternalServiceError:
    # Handle ML API failures
    recommendations = await recommendation_service.get_cached_recommendations(user_id)
except ServiceError as e:
    # Handle general service errors
    logger.error(f"Service error: {e}")
    raise
```

**Resilience Patterns:**

- **Fallback Strategies**: Graceful degradation when services fail
- **Circuit Breaker**: Prevent cascading failures
- **Retry Logic**: Automatic retries with exponential backoff
- **Timeout Handling**: Prevent hanging requests
- **Health Checks**: Proactive monitoring of service health

## Caching Strategy

Services implement intelligent caching at multiple levels:

### Response Caching

```python
# Cache recommendation results
cache_key = f"recommendations:user:{user_id}:trending"
cached_result = await redis_repo.get(cache_key)

if not cached_result:
    result = await generate_recommendations(user_id)
    await redis_repo.set(cache_key, result, ttl=3600)
    return result

return cached_result
```

### Embedding Caching

```python
# Cache vector embeddings
embedding = await vector_repo.get_movie_embedding(movie_id)

if not embedding:
    features = await get_movie_features(movie_id)
    embedding = await ml_client.generate_movie_embedding(features)
    await vector_repo.store_movie_embedding(movie_id, embedding)

return embedding
```

## Testing

Services are designed for comprehensive testing:

```python
import pytest
from unittest.mock import AsyncMock, Mock
from recommendation_api.services.recommendation import RecommendationService

@pytest.fixture
def mock_session():
    return Mock()

@pytest.fixture
def recommendation_service(mock_session):
    service = RecommendationService(mock_session)
    service.redis_repo = AsyncMock()
    service.vector_repo = AsyncMock()
    return service

async def test_get_trending_recommendations(recommendation_service):
    # Mock database response
    recommendation_service.session.exec.return_value.all.return_value = [
        # Mock movie objects
    ]

    recommendations, filters = recommendation_service.get_trending_recommendations()

    assert len(recommendations) > 0
    assert filters is not None
```

## Performance Monitoring

Services include performance monitoring and metrics:

```python
import time
from recommendation_api.services.metrics import record_service_call

async def get_recommendations(self, user_id: int):
    start_time = time.time()

    try:
        result = await self._generate_recommendations(user_id)
        record_service_call("recommendations", "success", time.time() - start_time)
        return result
    except Exception as e:
        record_service_call("recommendations", "error", time.time() - start_time)
        raise
```

## Future Enhancements

Planned improvements for the services layer:

1. **Authentication Service**: User authentication and authorization
2. **Notification Service**: Real-time notifications for users
3. **Analytics Service**: User behavior tracking and analytics
4. **A/B Testing Service**: Recommendation algorithm testing
5. **Content Service**: Content management and metadata enrichment
6. **Search Service**: Full-text search capabilities
7. **Personalization Service**: Advanced user profiling and preferences
8. **Metrics Service**: Comprehensive performance and business metrics
