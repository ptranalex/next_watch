***REMOVED*** Next Watch Backend API

A FastAPI-based REST API for the Next Watch movie platform. This API serves movie data from the `movie-storage` library.

***REMOVED******REMOVED*** Features

- Movie listing API with pagination
- Movie details by ID or TMDB ID
- Genre listing and details
- PostgreSQL database integration with `movie-storage` library

***REMOVED******REMOVED*** Prerequisites

- Python 3.9+
- Poetry for dependency management
- PostgreSQL database

***REMOVED******REMOVED*** Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd apps/backend-api
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Create a configuration file:

   ```bash
   cp .env.example .env
   ```

   Update the `.env` file with your PostgreSQL database connection string.

   For local development with enhanced settings:

   ```bash
   cp .env.local.example .env.local  ***REMOVED*** If example exists
   ***REMOVED*** or create your own .env.local file with local settings
   ```

   The `.env.local` file overrides settings in `.env` and provides additional debugging options.

4. Initialize the database:
   ```bash
   ./setup_dev_env.sh
   ```

***REMOVED******REMOVED*** Running the API

Start the development server:

```bash
poetry run uvicorn backend_api.main:app --reload
```

The API will be available at http://localhost:8000

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** Movies

- `GET /movies`: Get a paginated list of movies
- `GET /movies/{movie_id}`: Get movie details by ID
- `GET /movies/tmdb/{tmdb_id}`: Get movie details by TMDB ID

***REMOVED******REMOVED******REMOVED*** Genres

- `GET /genres`: Get a list of all genres
- `GET /genres/{genre_id}`: Get genre details by ID
- `GET /genres/name/{name}`: Get genre details by name

***REMOVED******REMOVED*** Database Integration

This API integrates with the `movie-storage` library which provides database operations for movie data. Key integration points:

1. **Database Connection**: Uses `movie-storage`'s database connection and session management.
2. **Schema Translation**: Converts SQLModel objects from `movie-storage` to Pydantic models for API responses.
3. **API Operations**: Uses `movie-storage` operations for querying movies and genres.

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Adding New Endpoints

To add new endpoints, create or modify route files in `src/backend_api/routes/`.

***REMOVED******REMOVED******REMOVED*** Database Operations

All database operations should use the `movie-storage` library:

```python
from movie_storage.db.operations import get_movies

movies = get_movies(db, offset=0, limit=10)
```

***REMOVED******REMOVED******REMOVED*** Testing

Run tests with:

```bash
poetry run pytest
```

***REMOVED******REMOVED******REMOVED*** Type Checking

The codebase uses type annotations to ensure type safety. To run type checking:

1. First, install mypy:

```bash
poetry add --dev mypy
```

2. Run type checking:

```bash
poetry run mypy src/backend_api
```

Fix any type errors that appear to maintain code quality.

***REMOVED******REMOVED*** Docker (Optional)

Building the Docker image:

```bash
docker build -t next-watch-api .
```

Running with Docker:

```bash
docker run -p 8000:8000 -e DATABASE_URL=postgresql://user:password@host:5432/dbname next-watch-api
```
