***REMOVED*** Movie Storage Examples

This directory contains examples demonstrating how to use the `movie-storage` package.

***REMOVED******REMOVED*** Movie Import Example

The `import_tmdb_movie.py` script demonstrates how to import a movie from a TMDB API response JSON file into the database:

```bash
***REMOVED*** Run the migration to create the necessary tables first
python -m movie_storage.cli migrate --create-tables

***REMOVED*** Import a movie from a JSON file
python examples/import_tmdb_movie.py examples/avatar.json --create-tables
```

This example shows:

1. How to use the new extended Movie model with additional fields
2. How to process cast information into the new Credit model
3. How to handle genre relationships

The imported movie will include:

- Basic movie information (title, overview, etc.)
- Extended details (tagline, status, etc.)
- Cast information from the credits
- Genre associations

***REMOVED******REMOVED*** Logging Examples

***REMOVED******REMOVED******REMOVED*** Using the `@with_logging` Decorator

The `logging_example.py` demonstrates how to use the `@with_logging` decorator to easily add logging configuration to your functions:

```python
from movie_storage.config import with_logging
from pathlib import Path

@with_logging(log_level="DEBUG", log_dir=Path("./logs"), verbose=True)
def my_function():
    logger = logging.getLogger(__name__)
    logger.info("This will be logged")
    ***REMOVED*** Your function code here
```

***REMOVED******REMOVED******REMOVED*** Key Features of the Logging System

1. **Central Configuration**: All logging is configured through a single function
2. **Flexible Output**: Can log to both console and files
3. **SQL Integration**: Special handling for SQLAlchemy and SQLModel logging
4. **Decorators**: Easy to apply with the `@with_logging` decorator
5. **Rich Console Output**: Uses different log levels for clear visualization

***REMOVED******REMOVED******REMOVED*** Configuring Logging Manually

If you need more control, you can also use the `configure_logging` function directly:

```python
from movie_storage.config import configure_logging
from pathlib import Path

***REMOVED*** Configure logging at the start of your script
configure_logging(
    log_level="INFO",           ***REMOVED*** DEBUG, INFO, WARNING, ERROR
    log_dir=Path("./logs"),     ***REMOVED*** None for console-only logging
    verbose=True,               ***REMOVED*** Show debug messages in console
    quiet=False                 ***REMOVED*** Suppress console output except errors
)

***REMOVED*** Then use standard logging
import logging
logger = logging.getLogger(__name__)
logger.info("Application started")
logger.debug("This is a debug message")
logger.warning("Something unexpected happened")
logger.error("An error occurred")
```

***REMOVED******REMOVED******REMOVED*** Using the Setup Utility

For a complete setup including database initialization, use the `setup_movie_storage` utility:

```python
from movie_storage.utils import setup_movie_storage
from pathlib import Path

***REMOVED*** Set up movie storage with logging
setup_info = setup_movie_storage(
    database_url="sqlite:///./movies.db",  ***REMOVED*** Optional database URL
    create_tables=True,                   ***REMOVED*** Whether to create database tables
    run_migrations=True,                  ***REMOVED*** Whether to run database migrations
    log_dir=Path("./logs"),               ***REMOVED*** Log directory (optional)
    log_level="DEBUG",                    ***REMOVED*** Log level (optional)
    verbose=True,                         ***REMOVED*** Whether to show verbose output
    quiet=False                           ***REMOVED*** Whether to suppress output
)
```

***REMOVED******REMOVED******REMOVED*** Running the Examples

To run the logging example:

```bash
python examples/logging_example.py
```

This will demonstrate logging configuration with both the decorator and direct approaches.
