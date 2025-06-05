***REMOVED*** Services Layer

This package contains service classes that implement the core business logic for the Recommendation API, following the principles of Clean Architecture.

***REMOVED******REMOVED*** Overview

The services layer sits between the API routes and data access repositories, providing:

1. Business logic for generating recommendations
2. Abstraction over data access
3. Domain-specific operations

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** RecommendationService

`recommendation.py` implements the `RecommendationService` class, which:

- Provides methods for generating different types of recommendations
- Integrates with the vector service for similarity searches
- Handles fallback strategies when primary recommendation methods fail
- Formats data for API responses

***REMOVED******REMOVED******REMOVED*** VectorService

`vector_service.py` implements the `VectorService` class, which:

- Provides high-level operations for vector embeddings
- Encapsulates the logic for vector storage and retrieval
- Performs similarity searches using the vector repository
- Handles batch processing of movie embeddings
- Communicates with ML API for embedding generation

***REMOVED******REMOVED******REMOVED*** ML API Client

`ml_api_client.py` implements the client for interacting with the ML API:

- Provides methods for generating embeddings through the ML API
- Handles HTTP communication with the ML API service
- Manages error handling and retries for API requests
- Offloads computationally intensive ML tasks to a dedicated service

***REMOVED******REMOVED******REMOVED*** EmbeddingService (Deprecated)

`embedding.py` previously contained local ML functionality, but has been replaced by the ML API client:

- ⚠️ **DEPRECATED**: This module is kept for backward compatibility only
- Redirects all calls to the ML API client
- Provides warning messages to guide developers to use the ML API client directly
- No longer performs local ML computation (removed SentenceTransformer dependency)

***REMOVED******REMOVED*** Architecture Changes

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

This architecture provides:

- Reduced resource usage in the recommendation API
- Independent scaling of ML workloads
- Specialized hardware utilization for ML operations
- Simplified deployment with reduced dependencies

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Using the RecommendationService

```python
from recommendation_api.services.recommendation import RecommendationService
from sqlmodel import Session

***REMOVED*** Create service with database session
service = RecommendationService(session)

***REMOVED*** Get trending recommendations
recommendations, filters = service.get_trending_recommendations(
    limit=20,
    days=7,
    min_rating=7.0
)

***REMOVED*** Get personalized recommendations for a user
recommendations, filters = service.get_user_recommendations(
    user_id=123,
    limit=20
)
```

***REMOVED******REMOVED******REMOVED*** Using the VectorService

```python
from recommendation_api.services.vector_service import get_vector_service
from sqlmodel import Session

***REMOVED*** Get the global vector service instance
vector_service = get_vector_service()

***REMOVED*** Generate and store an embedding for a movie (uses ML API)
embedding = await vector_service.generate_and_store_movie_embedding(
    session=session,
    movie_id=123
)

***REMOVED*** Find similar movies
similar_movies = vector_service.find_similar_movies_by_id(
    movie_id=123,
    limit=10
)
```

***REMOVED******REMOVED******REMOVED*** Using the ML API Client Directly

```python
from recommendation_api.services.ml_api_client import get_ml_api_client

***REMOVED*** Get the ML API client
ml_client = get_ml_api_client()

***REMOVED*** Generate an embedding for movie features
features = {
    "title": "The Matrix",
    "overview": "A computer hacker learns about the true nature of reality",
    "genres": ["Action", "Sci-Fi"]
}
embedding = await ml_client.generate_movie_embedding(features)

***REMOVED*** Test the connection to the ML API
is_connected = await ml_client.test_connection()
```

***REMOVED******REMOVED*** Service Layer Design Principles

This services layer follows these design principles:

1. **Single Responsibility**: Each service has a clear, focused purpose
2. **Dependency Injection**: Dependencies are injected rather than created internally
3. **Interface Segregation**: Services expose only what clients need
4. **Abstraction**: Services hide implementation details from API routes
5. **Testability**: Services can be tested in isolation with mocked dependencies
6. **Microservice Architecture**: Computationally intensive tasks are offloaded to specialized services
