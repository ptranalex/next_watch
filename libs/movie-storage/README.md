***REMOVED*** Movie Storage

A shared Python library for movie data models and database operations.

***REMOVED******REMOVED*** Features

- Movie data storage and retrieval
- Genre management
- Cast and crew information
- User authentication system
- Password hashing with bcrypt
- JWT token generation and validation
- SQLModel-based ORM with SQLAlchemy core
- Migration support with Alembic
- Comprehensive test suite

***REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Install with Poetry
cd libs/movie-storage
poetry install
```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Basic Usage

```python
from sqlmodel import Session, create_engine
from movie_storage.db import init_db
from movie_storage.db.operations import (
    create_movie, get_movies, create_user, authenticate_user
)
from movie_storage.db.operations import create_genre

***REMOVED*** Initialize database
db_url = "sqlite:///movies.db"
init_db(db_url, create_tables=True)

***REMOVED*** Create a session
engine = create_engine(db_url)
with Session(engine) as session:
    ***REMOVED*** Create a genre
    action = create_genre(session, "Action")
    comedy = create_genre(session, "Comedy")

    ***REMOVED*** Create a movie
    movie_data = {
        "tmdb_id": 123,
        "title": "Example Movie",
        "overview": "This is an example movie.",
        "release_date": "2023-01-01"
    }

    ***REMOVED*** Create movie with genres
    movie = create_movie(session, movie_data, genre_ids=[action.id, comedy.id])

    ***REMOVED*** Get all movies
    movies = get_movies(session)
    print(f"Found {len(movies)} movies")

    ***REMOVED*** User management
    ***REMOVED*** Create a new user
    user = create_user(
        session,
        email="user@example.com",
        password="secure_password",
        username="exampleuser"
    )

    ***REMOVED*** Authenticate user
    authenticated_user = authenticate_user(
        session,
        email="user@example.com",
        password="secure_password"
    )

    if authenticated_user:
        print(f"User authenticated: {authenticated_user.username}")
    else:
        print("Authentication failed")
```

***REMOVED******REMOVED******REMOVED*** User Management

```python
from movie_storage.db.operations.user import (
    create_user, get_user_by_email, authenticate_user,
    update_user, delete_user
)

***REMOVED*** Create a user
user = create_user(
    session,
    email="user@example.com",
    password="secure_password",
    username="exampleuser",
    full_name="Example User"
)

***REMOVED*** Find a user
found_user = get_user_by_email(session, "user@example.com")

***REMOVED*** Update user information
updated_user = update_user(
    session,
    user_id=user.id,
    username="newusername",
    full_name="New Name"
)

***REMOVED*** Check credentials
authenticated = authenticate_user(
    session,
    email="user@example.com",
    password="secure_password"
)
```

***REMOVED******REMOVED******REMOVED*** Movie Operations

```python
from movie_storage.db.operations.movie import (
    create_movie, get_movie_by_id, update_movie, delete_movie,
    search_movies, get_movies_by_genre, mark_movie_watched,
    add_movie_to_watchlist, like_movie
)

***REMOVED*** Create a movie
movie = create_movie(session, {
    "tmdb_id": 123,
    "title": "Example Movie",
    "overview": "This is an example movie.",
    "release_date": "2023-01-01",
    "poster_path": "/path/to/poster.jpg",
    "backdrop_path": "/path/to/backdrop.jpg",
    "vote_average": 7.5,
    "vote_count": 1000,
    "runtime": 120
})

***REMOVED*** Add user interaction
user_id = 1
movie_id = movie.id

***REMOVED*** Mark movie as watched by user
mark_movie_watched(session, user_id, movie_id)

***REMOVED*** Add movie to user's watchlist
add_movie_to_watchlist(session, user_id, movie_id)

***REMOVED*** Like a movie
like_movie(session, user_id, movie_id)

***REMOVED*** Search movies
action_movies = search_movies(
    session,
    genre_names=["Action"],
    sort_by="release_date",
    order="desc",
    limit=10
)
```

***REMOVED******REMOVED*** Database Migrations

The library includes Alembic migration support:

```bash
***REMOVED*** Run from libs/movie-storage directory
./migrate.sh
```

To reset the database:

```bash
***REMOVED*** Run from libs/movie-storage directory
./reset-db.sh
```

***REMOVED******REMOVED*** Development

Install development dependencies:

```bash
***REMOVED*** Install with dev dependencies
poetry install --with dev
```

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
***REMOVED*** Run all tests
poetry run pytest

***REMOVED*** Run with coverage report
poetry run pytest --cov=movie_storage

***REMOVED*** Run specific test file
poetry run pytest tests/operations/test_movie.py
```

***REMOVED******REMOVED******REMOVED*** Project Structure

```
movie_storage/
├── movie_storage/           ***REMOVED*** Main package
│   ├── db/                  ***REMOVED*** Database operations
│   │   ├── models/          ***REMOVED*** SQLModel data models
│   │   ├── operations/      ***REMOVED*** CRUD operations
│   │   ├── engine.py        ***REMOVED*** Database connection setup
│   │   └── migrations/      ***REMOVED*** Alembic migrations
│   ├── auth/                ***REMOVED*** Authentication utilities
│   │   ├── jwt.py           ***REMOVED*** JWT token handling
│   │   └── password.py      ***REMOVED*** Password hashing
│   └── utils/               ***REMOVED*** Utility functions
├── tests/                   ***REMOVED*** Test suite
│   ├── conftest.py          ***REMOVED*** Test fixtures
│   ├── models/              ***REMOVED*** Model tests
│   └── operations/          ***REMOVED*** Operation tests
├── examples/                ***REMOVED*** Usage examples
├── pyproject.toml           ***REMOVED*** Project metadata and dependencies
└── README.md                ***REMOVED*** This file
```

***REMOVED******REMOVED*** License

MIT
