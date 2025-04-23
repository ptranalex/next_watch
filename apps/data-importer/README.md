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
export TMDB_ACCESS_TOKEN="your_tmdb_access_token_here"
export OMDB_API_KEY="your_omdb_api_key_here"
```

***REMOVED******REMOVED******REMOVED*** CLI Commands

***REMOVED******REMOVED******REMOVED******REMOVED*** Sync Movies by Year Range

```bash
data-importer sync movies 2022 2023 --credits --save
```

Options:

- `--limit`, `-l`: Maximum movies per year (default: 20)
- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--save/--no-save`: Save movies to database (default: --no-save)
- `--credits/--no-credits`: Include cast and crew information (default: --no-credits)
- `--verbose`, `-v`: Show detailed output

***REMOVED******REMOVED******REMOVED******REMOVED*** Interactive Shell

Launch an interactive shell to explore and manipulate data:

```bash
data-importer shell
```

Options:

- `--config-dir`, `-c`: Configuration directory
- `--logs-dir`, `-l`: Directory to save log files
- `--data-dir`, `-d`: Directory for movie data files
- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--imdb-api-key`, `-i`: IMDb API key (if not set as environment variable)
- `--omdb-api-key`, `-o`: OMDB API key (if not set as environment variable)
- `--verbose`, `-v`: Enable verbose logging
- `--quiet`, `-q`: Suppress non-essential output
- `--theme`, `-th`: Color theme for the shell (default, monokai, solarized, pastie, vs, manni, autumn, murphy, monochrome)
- `--plain`, `-p`: Use plain output without syntax highlighting

In the shell, you can use various functions:

```python
***REMOVED*** Get popular movies from TMDB
movies = run_async(tmdb_client.get_popular_movies())

***REMOVED*** Search for a movie
results = run_async(tmdb_client.search_movies("Inception"))
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Interactive Mode (Experimental)

Launch an interactive interface for data import operations:

```bash
data-importer interactive
```

Options:

- `--config-dir`, `-c`: Configuration directory
- `--logs-dir`, `-l`: Directory to save log files
- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--verbose`, `-v`: Enable verbose logging
- `--quiet`, `-q`: Suppress non-essential output

Note: This feature is experimental and not fully implemented yet.

***REMOVED******REMOVED******REMOVED*** API Key Configuration

The application requires API keys for external services:

- **TMDB Access Token**: Get from [The Movie Database](https://www.themoviedb.org/settings/api)
- **OMDB API Key**: Get from [OMDb API](https://www.omdbapi.com/apikey.aspx)

You can provide these keys either as command-line options or environment variables:

```bash
export TMDB_ACCESS_TOKEN="your_tmdb_access_token_here"
export OMDB_API_KEY="your_omdb_api_key_here"
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Project Structure

- `src/data_importer/`: Main package
  - `cli/`: CLI commands
    - `commands/`: Command implementations
    - `utils.py`: CLI utilities
  - `services/`: Service implementations
    - `tmdb.py`: TMDB API client
    - `omdb.py`: OMDB API client
    - `imdb.py`: IMDB API client
  - `sync/`: Data synchronization logic
    - `movie_sync.py`: Movie synchronization functions
  - `config/`: Application configuration

***REMOVED******REMOVED******REMOVED*** Adding Support for New Data Sources

To add a new data source:

1. Create a new client in the `services/` directory
2. Update the sync functions to use the new source
3. Add CLI commands to interact with the new source

***REMOVED******REMOVED*** License

MIT
