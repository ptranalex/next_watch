***REMOVED*** Next Watch

A movie and TV show tracking application with detailed credits information.

***REMOVED******REMOVED*** Features

- Movie database with detailed information including cast and crew
- Import data from TMDB and OMDB APIs
- Command-line interface for easy data management
- Credit information for cast and crew members

***REMOVED******REMOVED*** Project Structure

- `apps/data-importer/`: Tools for importing data from external sources
- `libs/movie-storage/`: Database models and operations for movie data

***REMOVED******REMOVED*** Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -e .
   ```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Importing Movie Data

Set your API keys:

```bash
export TMDB_API_KEY="your_tmdb_api_key_here"
export OMDB_API_KEY="your_omdb_api_key_here"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Sync movies by year range with credits:

```bash
data-importer sync movies 2022 2023 --credits --save
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Import a specific movie:

```bash
data-importer movie id 550  ***REMOVED*** Import Fight Club (TMDB ID: 550)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Import popular movies:

```bash
data-importer movie popular --limit 5  ***REMOVED*** Import 5 most popular movies
```

***REMOVED******REMOVED******REMOVED*** Interactive Shell

Explore and manipulate data using the interactive shell:

```bash
data-importer shell
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Adding New Functionality

1. Implement new features in the appropriate library
2. Add CLI commands to expose functionality
3. Update tests and documentation

***REMOVED******REMOVED*** License

MIT
