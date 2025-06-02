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
- Encapsulates the logic for generating and storing embeddings
- Performs similarity searches using the vector repository
- Handles batch processing of movie embeddings

***REMOVED******REMOVED******REMOVED*** EmbeddingService

`embedding.py` contains functionality for generating embeddings:

- Uses SentenceTransformer models to generate text embeddings
- Provides methods for generating movie embeddings from features
- Creates user preference vectors from multiple movie embeddings
- Handles normalization and averaging of embeddings

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

***REMOVED*** Generate and store an embedding for a movie
embedding = vector_service.generate_and_store_movie_embedding(
    session=session,
    movie_id=123
)

***REMOVED*** Find similar movies
similar_movies = vector_service.find_similar_movies_by_id(
    movie_id=123,
    limit=10
)
```

***REMOVED******REMOVED*** Service Layer Design Principles

This services layer follows these design principles:

1. **Single Responsibility**: Each service has a clear, focused purpose
2. **Dependency Injection**: Dependencies are injected rather than created internally
3. **Interface Segregation**: Services expose only what clients need
4. **Abstraction**: Services hide implementation details from API routes
5. **Testability**: Services can be tested in isolation with mocked dependencies
