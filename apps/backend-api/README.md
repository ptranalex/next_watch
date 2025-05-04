***REMOVED*** Next Watch Backend API

A FastAPI-based backend service for the Next Watch application.

***REMOVED******REMOVED*** Features

- Movie data API endpoints
- Genre information
- Cast and crew information
- Movie search functionality
- Database health checking
- User authentication with JWT
- User registration and profile management

***REMOVED******REMOVED*** Setup

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Python 3.10+
- Poetry for dependency management
- PostgreSQL database

***REMOVED******REMOVED******REMOVED*** Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/next_watch.git
   cd next_watch/apps/backend-api
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Configure environment variables by creating a `.env` file based on `.env.example`.

4. Run the development server:

   ```bash
   ***REMOVED*** Using the CLI (recommended):
   poetry run backend-api server start

   ***REMOVED*** Or with explicit options:
   poetry run backend-api server start --port 8080 --log-level DEBUG

   ***REMOVED*** Alternative methods:
   ***REMOVED*** Using Python's module runner:
   poetry run python -m backend_api.main

   ***REMOVED*** Using uvicorn directly:
   poetry run uvicorn backend_api.main:app --reload --port $(grep API_PORT .env | cut -d= -f2)
   ```

***REMOVED******REMOVED******REMOVED*** CLI Reference

The backend API comes with a CLI tool that provides various commands:

```bash
***REMOVED*** Server management
poetry run backend-api server start  ***REMOVED*** Start the API server
poetry run backend-api server start --help  ***REMOVED*** Show all available options

***REMOVED*** Available options:
***REMOVED*** --host TEXT                 Host to bind the server to
***REMOVED*** --port INTEGER              Port to bind the server to (overrides config)
***REMOVED*** --log-level TEXT            Log level (DEBUG, INFO, WARNING, ERROR)
***REMOVED*** --reload / --no-reload      Enable auto-reload on code changes
***REMOVED*** --log-dir PATH              Directory to store log files
***REMOVED*** --sqlalchemy-level TEXT     Log level for SQLAlchemy
```

***REMOVED******REMOVED*** Configuration

The backend API uses a structured configuration system:

- Environment variables for basic settings
- Support for `.env` and `.env.local` files
- Centralized logging configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

| Variable                      | Description                                 | Default                                                    |
| ----------------------------- | ------------------------------------------- | ---------------------------------------------------------- |
| `DATABASE_URL`                | PostgreSQL connection string                | `postgresql://postgres:postgres@localhost:5432/next_watch` |
| `API_PORT`                    | Port for the API server                     | `8000`                                                     |
| `LOG_LEVEL`                   | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO`                                                     |
| `DEBUG`                       | Enable debug mode                           | `false`                                                    |
| `CORS_ORIGINS`                | Comma-separated list of allowed origins     | `*`                                                        |
| `ENABLE_PERFORMANCE_METRICS`  | Enable performance metrics middleware       | `false`                                                    |
| `SQLALCHEMY_LOG_LEVEL`        | Specific logging level for SQLAlchemy       | `WARNING`                                                  |
| `LOGS_DIR`                    | Directory to store log files                | `logs`                                                     |
| `DATABASE_ECHO`               | Enable SQL statement logging                | `false`                                                    |
| `JWT_SECRET`                  | Secret key for JWT token generation         | `change_this_in_production_very_important`                 |
| `JWT_ALGORITHM`               | Algorithm for JWT token generation          | `HS256`                                                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutes until access token expires          | `30`                                                       |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Days until refresh token expires            | `7`                                                        |

***REMOVED******REMOVED******REMOVED*** Configuration Structure

The configuration system is organized in the `config` package:

```
config/
├── __init__.py   ***REMOVED*** Exports configuration classes and utilities
├── app.py        ***REMOVED*** Core application settings and environment variables
└── logging.py    ***REMOVED*** Centralized logging configuration
```

***REMOVED******REMOVED******REMOVED*** Using the Configuration

```python
***REMOVED*** Import settings
from backend_api.config.app import settings

***REMOVED*** Access configuration
database_url = settings.database_url
api_port = settings.api_port

***REMOVED*** Configure logging
from backend_api.config import configure_logging
log_config = configure_logging(
    log_level=settings.log_level,
    log_dir=Path("logs"),
    verbose=settings.debug
)
```

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Authenticate and get access/refresh tokens
- `POST /api/v1/auth/login/json` - JSON-based login alternative
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current authenticated user details

***REMOVED******REMOVED******REMOVED*** Movies

- `GET /movies/` - List movies with pagination
- `GET /movies/{movie_id}` - Get details for a specific movie
- `GET /movies/tmdb/{tmdb_id}` - Get movie by TMDB ID

***REMOVED******REMOVED******REMOVED*** Genres

- `GET /genres/` - List all genres
- `GET /genres/{genre_id}` - Get details for a specific genre
- `GET /genres/{genre_id}/movies` - Get movies for a specific genre

***REMOVED******REMOVED******REMOVED*** Cast

- `GET /cast/movie/{movie_id}` - Get cast and crew information for a specific movie

***REMOVED******REMOVED******REMOVED*** Health Checks

- `GET /health` - API health check
- `GET /db-health` - Database health check

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
poetry run pytest
```

***REMOVED******REMOVED******REMOVED*** Project Structure

```
backend-api/
├── src/
│   └── backend_api/
│       ├── routes/       ***REMOVED*** API route handlers
│       ├── schemas/      ***REMOVED*** Pydantic models for request/response
│       ├── db/           ***REMOVED*** Database models and utilities
│       ├── config/       ***REMOVED*** Configuration and settings
│       └── main.py       ***REMOVED*** Application entry point
├── tests/                ***REMOVED*** Test cases
└── README.md             ***REMOVED*** You are here
```

***REMOVED******REMOVED*** Dependencies

- FastAPI - Web framework
- SQLModel - SQL database interaction
- Pydantic - Data validation
- movie-storage - Internal library for movie data storage

***REMOVED******REMOVED*** License

[MIT License](LICENSE)
