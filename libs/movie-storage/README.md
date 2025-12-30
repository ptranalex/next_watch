# Movie Storage

A shared Python library for movie data models and database operations.

## Features

- Movie data storage and retrieval
- Genre management
- Cast and crew information
- User authentication system
- Password hashing with bcrypt
- JWT token generation and validation
- SQLModel-based ORM with SQLAlchemy core
- Migration support with Alembic
- Comprehensive test suite

## Installation

```bash
# Install with Poetry
cd libs/movie-storage
poetry install
```

## Usage

### Basic Usage

```python
from sqlmodel import Session, create_engine
from movie_storage.db import init_db
from movie_storage.db.operations import (
    create_movie, get_movies, create_user, authenticate_user
)
from movie_storage.db.operations import create_genre

# Initialize database
db_url = "sqlite:///movies.db"
init_db(db_url, create_tables=True)

# Create a session
engine = create_engine(db_url)
with Session(engine) as session:
    # Create a genre
    action = create_genre(session, "Action")
    comedy = create_genre(session, "Comedy")

    # Create a movie
    movie_data = {
        "tmdb_id": 123,
        "title": "Example Movie",
        "overview": "This is an example movie.",
        "release_date": "2023-01-01"
    }

    # Create movie with genres
    movie = create_movie(session, movie_data, genre_ids=[action.id, comedy.id])

    # Get all movies
    movies = get_movies(session)
    print(f"Found {len(movies)} movies")

    # User management
    # Create a new user
    user = create_user(
        session,
        email="user@example.com",
        password="secure_password",
        username="exampleuser"
    )

    # Authenticate user
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

### User Management

```python
from movie_storage.db.operations.user import (
    create_user, get_user_by_email, authenticate_user,
    update_user, delete_user
)

# Create a user
user = create_user(
    session,
    email="user@example.com",
    password="secure_password",
    username="exampleuser",
    full_name="Example User"
)

# Find a user
found_user = get_user_by_email(session, "user@example.com")

# Update user information
updated_user = update_user(
    session,
    user_id=user.id,
    username="newusername",
    full_name="New Name"
)

# Check credentials
authenticated = authenticate_user(
    session,
    email="user@example.com",
    password="secure_password"
)
```

### Movie Operations

```python
from movie_storage.db.operations.movie import (
    create_movie, get_movie_by_id, update_movie, delete_movie,
    search_movies, get_movies_by_genre, mark_movie_watched,
    add_movie_to_watchlist, like_movie
)

# Create a movie
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

# Add user interaction
user_id = 1
movie_id = movie.id

# Mark movie as watched by user
mark_movie_watched(session, user_id, movie_id)

# Add movie to user's watchlist
add_movie_to_watchlist(session, user_id, movie_id)

# Like a movie
like_movie(session, user_id, movie_id)

# Search movies
action_movies = search_movies(
    session,
    genre_names=["Action"],
    sort_by="release_date",
    order="desc",
    limit=10
)
```

## Database Migrations

The library includes Alembic migration support:

```bash
# Run from libs/movie-storage directory
./migrate.sh
```

To reset the database:

```bash
# Run from libs/movie-storage directory
./reset-db.sh
```

## Development

Install development dependencies:

```bash
# Install with dev dependencies
poetry install --with dev
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=movie_storage

# Run specific test file
poetry run pytest tests/operations/test_movie.py
```

### Project Structure

```
movie_storage/
├── movie_storage/           # Main package
│   ├── db/                  # Database operations
│   │   ├── models/          # SQLModel data models
│   │   ├── operations/      # CRUD operations
│   │   ├── engine.py        # Database connection setup
│   │   └── migrations/      # Alembic migrations
│   ├── auth/                # Authentication utilities
│   │   ├── jwt.py           # JWT token handling
│   │   └── password.py      # Password hashing
│   └── utils/               # Utility functions
├── tests/                   # Test suite
│   ├── conftest.py          # Test fixtures
│   ├── models/              # Model tests
│   └── operations/          # Operation tests
├── examples/                # Usage examples
├── pyproject.toml           # Project metadata and dependencies
└── README.md                # This file
```

## License

MIT
