***REMOVED*** Movie Storage

Database operations for movie data.

***REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Install with Poetry
poetry install
```

***REMOVED******REMOVED*** Usage

Example usage:

```python
from sqlmodel import Session, create_engine
from movie_storage.db import init_db
from movie_storage.movie_operations import create_movie, get_movies
from movie_storage.genre_operations import create_genre

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
```

***REMOVED******REMOVED*** Development

Install development dependencies:

```bash
***REMOVED*** Install with dev dependencies
poetry install --with dev
```

Run tests:

```bash
poetry run pytest
```
