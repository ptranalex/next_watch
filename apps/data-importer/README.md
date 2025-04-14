***REMOVED*** Data Importer

A movie data importer for the Next Watch platform.

***REMOVED******REMOVED*** Features

- Fetch movie data from TMDB and OMDB APIs
- Store movie information in a database using the movie-storage module
- Filter movies by year, popularity, and other criteria
- Command-line interface for batch operations
- Interactive REPL for exploring data

***REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Install with Poetry
poetry install
```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Command Line

```bash
***REMOVED*** Sync movies from 2020-2021 and save to database
poetry run python -m data_importer.cli sync --start-year 2020 --end-year 2021 --save-to-db
```

***REMOVED******REMOVED******REMOVED*** API Example

```python
from data_importer.sync.movie_sync import sync_movies_by_year_range
from movie_storage.db import init_db

***REMOVED*** Initialize database
init_db("sqlite:///movies.db", create_tables=True)

***REMOVED*** Sync movies
results = await sync_movies_by_year_range(
    tmdb_client=tmdb_client,
    omdb_client=omdb_client,
    start_year=2020,
    end_year=2021,
    save_to_db=True
)
```

***REMOVED******REMOVED*** Example Scripts

The `examples` directory contains sample scripts that demonstrate various features:

```bash
***REMOVED*** Run the database sync example
poetry run python examples/sync_with_db.py
```
