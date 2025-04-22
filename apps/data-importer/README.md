***REMOVED*** Data Importer

This application provides tools to import movie and TV show data from external sources into the Next Watch database.

***REMOVED******REMOVED*** Features

- Import movies from TMDB (The Movie Database) with cast and crew information
- Support for syncing by year range or importing specific movies by ID
- CLI interface for easy integration
- Interactive shell for data exploration

***REMOVED******REMOVED*** Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -e .
   ```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Environment Setup

Set your API keys as environment variables:

```bash
export TMDB_API_KEY="your_tmdb_api_key_here"
export OMDB_API_KEY="your_omdb_api_key_here"
```

***REMOVED******REMOVED******REMOVED*** CLI Commands

***REMOVED******REMOVED******REMOVED******REMOVED*** Sync Movies by Year Range

```bash
data-importer sync movies 2022 2023 --credits --save
```

Options:

- `--limit`, `-l`: Maximum movies per year (default: 20)
- `--tmdb-key`, `-t`: TMDB API key (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--save/--no-save`: Save movies to database (default: --no-save)
- `--credits/--no-credits`: Include cast and crew information (default: --no-credits)
- `--verbose`, `-v`: Show detailed output

***REMOVED******REMOVED******REMOVED******REMOVED*** Import a Specific Movie

```bash
data-importer movie id 550  ***REMOVED*** Import Fight Club (TMDB ID: 550)
```

Options:

- `--api-key`, `-k`: TMDB API key (if not set as environment variable)
- `--language`, `-l`: Language for movie data (default: en-US)
- `--verbose`, `-v`: Show detailed output

***REMOVED******REMOVED******REMOVED******REMOVED*** Import Popular Movies

```bash
data-importer movie popular --limit 5  ***REMOVED*** Import 5 most popular movies
```

Options:

- `--limit`, `-n`: Number of movies to import (default: 10)
- `--api-key`, `-k`: TMDB API key (if not set as environment variable)
- `--language`, `-l`: Language for movie data (default: en-US)
- `--verbose`, `-v`: Show detailed output

***REMOVED******REMOVED******REMOVED*** Interactive Shell

Launch an interactive shell to explore and manipulate data:

```bash
data-importer shell
```

In the shell, you can use various functions:

```python
***REMOVED*** Sync movies for a year range with credits
sync_movies(2022, 2023, include_credits=True, save_to_db=True)

***REMOVED*** Access the synced movies
jprint(synced_movies[0])  ***REMOVED*** Print the first movie in nice format
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Project Structure

- `src/data_importer/`: Main package
  - `cli/`: CLI commands
  - `services/`: Service implementations
    - `tmdb.py`: TMDB API client
    - `omdb.py`: OMDB API client
  - `sync/`: Data synchronization logic
    - `movie_sync.py`: Movie synchronization functions

***REMOVED******REMOVED******REMOVED*** Adding Support for New Data Sources

To add a new data source:

1. Create a new client in the `services/` directory
2. Update the sync functions to use the new source
3. Add CLI commands to interact with the new source

***REMOVED******REMOVED*** License

MIT
