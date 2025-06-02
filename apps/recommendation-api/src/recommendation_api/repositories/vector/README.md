***REMOVED*** Vector Repository

This package provides access to vector databases for similarity search operations in the Recommendation API.

***REMOVED******REMOVED*** Overview

The vector repository follows the repository pattern to abstract database access for vector operations, making it easier to:

1. Test the application with mock repositories
2. Swap out the underlying vector database without changing business logic
3. Maintain clear separation of concerns

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** Client

`client.py` provides a low-level wrapper around the Qdrant vector database client. It:

- Manages connection to the Qdrant server
- Provides methods for CRUD operations on vectors
- Handles connection pooling and error recovery
- Implements retry logic and logging

***REMOVED******REMOVED******REMOVED*** Repository

`repository.py` contains:

- The `VectorRepository` class that implements repository pattern
- Methods for storing, retrieving, and searching movie embeddings
- Standalone functions for backward compatibility

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Using the VectorRepository class

```python
from recommendation_api.repositories.vector import VectorRepository

***REMOVED*** Create repository instance
repository = VectorRepository()

***REMOVED*** Store a movie embedding
repository.store_movie_embedding(
    movie_id=123,
    embedding=[0.1, 0.2, 0.3, ...],
    metadata={"title": "The Matrix"}
)

***REMOVED*** Search for similar movies
similar_movies = repository.search_similar_movies(
    query_embedding=[0.1, 0.2, 0.3, ...],
    limit=10
)
```

***REMOVED******REMOVED******REMOVED*** Using standalone functions

```python
from recommendation_api.repositories.vector import (
    store_movie_embedding,
    search_similar_movies
)

***REMOVED*** Store a movie embedding
store_movie_embedding(
    movie_id=123,
    embedding=[0.1, 0.2, 0.3, ...],
    metadata={"title": "The Matrix"}
)

***REMOVED*** Search for similar movies
similar_movies = search_similar_movies(
    query_embedding=[0.1, 0.2, 0.3, ...],
    limit=10
)
```

***REMOVED******REMOVED*** Configuration

The repository is configured through environment variables:

- `QDRANT_URL`: URL of the Qdrant server
- `QDRANT_API_KEY`: API key for authentication
- `QDRANT_COLLECTION_NAME`: Name of the collection to use
- `EMBEDDING_DIMENSION`: Dimension of embedding vectors
