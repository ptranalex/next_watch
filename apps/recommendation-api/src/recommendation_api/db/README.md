***REMOVED*** Database Module

This module handles all database interactions for the Recommendation API service, providing connection management and data operations.

***REMOVED******REMOVED*** Overview

The database module provides:

- Connection management for PostgreSQL
- Database session handling
- Data access operations
- Entity mapping and conversion

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** `connection.py`

Manages database connections:

- `get_db_engine()`: Creates and returns a SQLAlchemy engine
- `get_db_context()`: Provides a context manager for database sessions
- `test_connection()`: Tests database connectivity
- `initialize_db()`: Sets up database schema if needed

***REMOVED******REMOVED******REMOVED*** `operations.py`

Contains all data access operations:

- Movie operations (get, search, filter)
- User operations (get, create, update)
- Rating operations (get, create, update)
- Recommendation operations (fetch, store)
- Movie metadata operations (fetch features for embeddings)

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Database Sessions

```python
from recommendation_api.db.connection import get_db_context

***REMOVED*** Using a context manager for automatic session handling
with get_db_context() as session:
    ***REMOVED*** Use session for database operations
    movies = session.query(Movie).all()
```

***REMOVED******REMOVED******REMOVED*** Movie Operations

```python
from recommendation_api.db.operations import (
    get_movie_by_id,
    get_movies_by_ids,
    get_movies_for_embeddings,
    get_movie_features
)

***REMOVED*** Get a single movie
with get_db_context() as session:
    movie = get_movie_by_id(session, movie_id=123)

***REMOVED*** Get multiple movies
with get_db_context() as session:
    movies = get_movies_by_ids(session, [123, 456, 789])

***REMOVED*** Get movies for embedding generation
with get_db_context() as session:
    movies = get_movies_for_embeddings(session, limit=100)

***REMOVED*** Get movie features for embedding generation
with get_db_context() as session:
    features = get_movie_features(session, movie_id=123)
```

***REMOVED******REMOVED*** Database Schema

The module interacts with the following tables:

- `movies`: Movie metadata (title, release date, genres, etc.)
- `users`: User information
- `ratings`: User ratings for movies
- `genres`: Movie genres
- `movie_genres`: Many-to-many relationship between movies and genres
- `cast_members`: Movie cast information
- `directors`: Movie directors

***REMOVED******REMOVED*** Error Handling

Database operations use consistent error handling:

- Specific exceptions for common database errors
- Logging of database errors with context
- Graceful handling of connection issues

***REMOVED******REMOVED*** Connection Configuration

Database connection is configured via:

- `DATABASE_URL` environment variable
- `database_url` setting in configuration
- Default value from application config

The URL format follows SQLAlchemy's connection string format:

```
postgresql://username:password@host:port/database
```
