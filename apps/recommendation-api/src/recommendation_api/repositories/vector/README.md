***REMOVED*** Vector Repository Module

This module provides a high-level interface for interacting with the vector database (Qdrant) used for similarity search and recommendations.

***REMOVED******REMOVED*** Overview

The vector repository module is responsible for:

- Managing connections to the Qdrant vector database
- Storing movie embeddings (vector representations)
- Performing similarity searches
- Handling vector database operations
- Providing fallback mechanisms for embedding retrieval

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** `client.py`

Manages the low-level connection to Qdrant:

- `QdrantClient`: Wrapper for the Qdrant client with enhanced functionality
- `get_qdrant_client()`: Singleton function to get a shared client instance
- Connection management and configuration
- Error handling and retries

***REMOVED******REMOVED******REMOVED*** `repository.py`

Provides high-level repository functions:

- `VectorRepository`: Main class for vector operations
- Collection management (create, check, list)
- Embedding operations (store, retrieve, delete)
- Similarity search methods
- Batch operations for efficiency
- Fallback mechanisms for retrieval

***REMOVED******REMOVED******REMOVED*** `__init__.py`

Exports key functions and classes:

- Repository class
- Standalone functions for backward compatibility
- Type definitions

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Basic Operations

```python
from recommendation_api.repositories.vector import (
    create_collection,
    store_movie_embedding,
    get_movie_embedding,
    search_similar_movies
)

***REMOVED*** Create collection if needed
create_collection()

***REMOVED*** Store an embedding
movie_id = 123
embedding = [0.1, 0.2, 0.3, ...]  ***REMOVED*** Vector from embedding model
metadata = {"title": "Movie Title", "release_year": 2023}
store_movie_embedding(movie_id, embedding, metadata)

***REMOVED*** Retrieve an embedding
vector = get_movie_embedding(movie_id)

***REMOVED*** Find similar movies
similar_movies = search_similar_movies(
    query_embedding=vector,
    limit=10,
    score_threshold=0.7
)
```

***REMOVED******REMOVED******REMOVED*** Using the Repository Class

```python
from recommendation_api.repositories.vector import VectorRepository

***REMOVED*** Create repository instance
repo = VectorRepository()

***REMOVED*** Store embedding
repo.store_movie_embedding(movie_id, embedding, metadata)

***REMOVED*** Search by movie ID
similar_movies = repo.search_by_movie_id(
    movie_id=123,
    limit=20,
    score_threshold=0.6
)

***REMOVED*** Batch operations
embeddings_data = [
    (movie_id1, embedding1, metadata1),
    (movie_id2, embedding2, metadata2),
    ***REMOVED*** ...
]
repo.batch_store_embeddings(embeddings_data)
```

***REMOVED******REMOVED*** Vector Database Schema

The module works with the following Qdrant collection structure:

- Collection name: `movies` (configurable)
- Vector size: 384 (configurable, based on embedding model)
- Distance metric: Cosine similarity
- Metadata payload fields:
  - `movie_id`: Movie ID (integer)
  - `title`: Movie title (string)
  - `release_year`: Release year (integer)
  - `genres`: List of genres (array of strings)
  - `imdb_rating`: IMDb rating (float)

***REMOVED******REMOVED*** Fallback Mechanisms

The repository implements several fallback mechanisms:

1. **Direct point retrieval**: Primary method using point ID
2. **Search with filtering**: Fallback when vector is missing
3. **Dummy vector search**: Last resort for metadata-only points

These fallbacks ensure robust operation even when embeddings have issues.

***REMOVED******REMOVED*** Error Handling

The repository provides robust error handling:

- Specific exceptions for vector operations
- Logging of errors with context
- Graceful degradation with fallbacks
- Retry mechanisms for transient errors

***REMOVED******REMOVED*** Configuration

Vector database connection is configured via:

- `QDRANT_URL` environment variable
- `qdrant_url` setting in configuration
- Default: `http://localhost:6333`

Collection settings:

- `QDRANT_COLLECTION_NAME`: Collection name (default: `movies`)
- `EMBEDDING_DIMENSION`: Vector size (default: 384)
