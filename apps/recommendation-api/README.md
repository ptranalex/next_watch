***REMOVED*** Recommendation API

A FastAPI service for generating movie recommendations for the Next Watch platform.

***REMOVED******REMOVED*** Overview

This API provides endpoints for various types of movie recommendations:

- Trending recommendations based on recent popularity
- Popular recommendations based on rating and vote count
- Personalized recommendations based on user preferences
- Similar movie recommendations based on content similarity

Base URL: `/reco/v1`

***REMOVED******REMOVED*** Architecture

The application follows a clean architecture approach with these main components:

```text
recommendation_api/
├── models/           ***REMOVED*** Data models for API requests/responses
├── routes/           ***REMOVED*** API endpoints and request handling
│   └── v1/           ***REMOVED*** Versioned recommendation endpoints
├── services/         ***REMOVED*** Business logic and integrations
│   └── cache_service ***REMOVED*** Cache helpers and background warming
│   └── clients/      ***REMOVED*** Backend/Movies HTTP clients
├── repositories/     ***REMOVED*** Data access layer
│   └── vector/       ***REMOVED*** Qdrant vector DB access
│   └── redis/        ***REMOVED*** Redis cache access
├── db/               ***REMOVED*** Database utilities and operations
├── core/             ***REMOVED*** App factory, middleware, metrics (fast-core)
├── config/           ***REMOVED*** Application configuration (via shared config lib)
└── cli/              ***REMOVED*** Typer-based command-line interface
```

***REMOVED******REMOVED******REMOVED*** Key Components

- **API Routes**: FastAPI endpoints for handling HTTP requests
- **Service Layer**: Business logic for recommendations
- **Repository Layer**: Data access abstractions
- **Vector Storage**: Qdrant vector database for similarity search
- **Redis Cache**: Redis for caching similar movie recommendations
- **ML API Client**: Client for communicating with the ML API service

***REMOVED******REMOVED*** Dependencies

The service relies on several key dependencies:

- **FastAPI**: Web framework for building APIs
- **SQLAlchemy/SQLModel**: ORM for database interactions
- **Qdrant Client**: Client for vector database operations
- **Asyncpg**: Async PostgreSQL driver (required for CLI health checks and database operations)
- **Typer/Rich**: CLI framework and formatting
- **HTTPX**: Async HTTP client for ML API communication

***REMOVED******REMOVED*** Development with Hatch

The project now uses [Hatch](https://hatch.pypa.io/) for project management, which provides isolated environments, streamlined dependency management, and standardized development workflows.

***REMOVED******REMOVED******REMOVED*** Getting Started with Hatch

1. Install Hatch:

   ```bash
   pip install hatch
   ```

2. Create development environment:

   ```bash
   ***REMOVED*** This will create an isolated environment with all dependencies
   hatch env create
   ```

3. Run the API in development mode:

   ```bash
   ***REMOVED*** Start the API with hot reloading
   hatch run dev
   ```

***REMOVED******REMOVED******REMOVED*** Common Hatch Commands

```bash
***REMOVED*** Run the application
hatch run serve

***REMOVED*** Run development server with hot reloading
hatch run dev

***REMOVED*** Run CLI commands
hatch run cli -- embeddings status

***REMOVED*** Run tests
hatch run test

***REMOVED*** Run tests with coverage
hatch run test-cov

***REMOVED*** Run linters and formatters
hatch run lint

***REMOVED*** Format code
hatch run format
```

***REMOVED******REMOVED*** Docker

The service includes an optimized Dockerfile that significantly reduces image size and build time.

***REMOVED******REMOVED******REMOVED*** Dockerfile Features

- **Lightweight Image**: ~835MB (45% smaller than the original ~1.5GB image)
- **ML Dependencies Optional**: Excludes heavy ML libraries (PyTorch, transformers) to reduce size
- **Production-Ready**: Includes health checks, non-root user, and proper environment setup

***REMOVED******REMOVED******REMOVED*** Docker Build Options

***REMOVED******REMOVED******REMOVED******REMOVED*** Lightweight Build (Default)

```bash
***REMOVED*** Build the lightweight image (no ML dependencies)
docker build -t recommendation-api .

***REMOVED*** Run the container
docker run -p 8002:8002 recommendation-api
```

***REMOVED******REMOVED******REMOVED*** Environment Variables

- `ENVIRONMENT`: Environment name (`development`, `staging`, `production`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8002`)
- `LOG_LEVEL`: Logging level (default: `INFO`; `DEBUG` in development)
- `BACKEND_API_URL`: Backend API base URL (default: `http://localhost:8000`)
- `ML_API_URL`: ML API base URL (default: `http://localhost:8004`)
- `QDRANT_URL`: Qdrant vector DB URL
- `REDIS_URL`: Redis URL for caching
- `INTERNAL_API_KEY`: Internal key for backend communication
- Uvicorn tuning (used in production mode via `__main__.py`):
  - `WORKERS` (default `1`), `TIMEOUT` (keep-alive, default `120`),
    `LIMIT_MAX_REQUESTS` (default `1000`), `BACKLOG` (default `1024`),
    `FORWARDED_ALLOW_IPS` (default `*`)

***REMOVED******REMOVED******REMOVED*** Microservices Architecture

The recommendation system now follows a microservices architecture:

```text
┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
│                   │         │                   │         │                   │
│  Recommendation   │ ◄─────► │   Vector Service  │ ◄─────► │      Qdrant       │
│     Service       │         │                   │         │  Vector Database  │
│                   │         │                   │         │                   │
└───────────────────┘         └───────────────────┘         └───────────────────┘
         │                              │
         ▼                              ▼
┌───────────────────┐          ┌───────────────────┐
│                   │          │                   │
│    Redis Cache    │          │   ML API Client   │
│                   │          │                   │
└───────────────────┘          └───────────────────┘
                                        │
                                        ▼
                               ┌───────────────────┐
                               │                   │
                               │      ML API       │
                               │     Service       │
                               │                   │
                               └───────────────────┘
```

This architecture provides:

- Reduced resource usage in the recommendation API
- Independent scaling of ML workloads
- Specialized hardware utilization for ML operations
- Simplified deployment with reduced dependencies

***REMOVED******REMOVED*** Installation

1. Clone the repository
2. Install using Hatch:

   ```bash
   pip install hatch
   hatch env create
   ```

3. Configure environment:

   ```bash
   cp .env.example .env
   ***REMOVED*** Edit .env with your configuration
   ```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Running the API

```bash
***REMOVED*** Development mode with hot reloading
hatch run dev

***REMOVED*** Production mode
hatch run serve
```

***REMOVED******REMOVED******REMOVED*** CLI Commands

```bash
***REMOVED*** Using Hatch
hatch run cli -- [COMMAND]

***REMOVED*** Or using the installed CLI (if package is installed)
rec-api [COMMAND]

***REMOVED*** Show available commands
rec-api --help

***REMOVED*** Server Management
rec-api serve start [--host HOST] [--port PORT] [--reload] [--log-level LEVEL] [--verbose] [--quiet]
rec-api serve stop
rec-api serve restart

***REMOVED*** Configuration
rec-api config show [--show-secrets] [--verbose]
rec-api config validate
rec-api config env

***REMOVED*** Health Checks
rec-api health check
rec-api health ping SERVICE  ***REMOVED*** SERVICE can be: api, db, qdrant

***REMOVED*** Embeddings Management
rec-api embeddings generate [--batch-size SIZE] [--force] [--limit LIMIT] [--movie-id ID] [--verbose]
rec-api embeddings status [--verbose]
rec-api embeddings cleanup [--dry-run/--execute] [--verbose]
rec-api embeddings info [--verbose]
rec-api embeddings repair_embeddings [--batch-size SIZE] [--movie-id ID] [--dry-run] [--verbose]

***REMOVED*** ML API Commands
rec-api ml test-connection
rec-api ml generate-embedding "Title" "Overview..." --genres "Drama,Thriller" --id 123

***REMOVED*** Version Information
rec-api version

***REMOVED*** Cache Management
rec-api cache info [--verbose]
rec-api cache clear [--force]
rec-api cache precompute [--limit N] [--min-score SCORE] [--batch-size SIZE] [--ttl SECONDS] [--movie-id ID]
```

***REMOVED******REMOVED*** Configuration

The service is configured via environment variables and the shared `config` library. See Environment Variables above for the most important keys.

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
hatch run test
```

***REMOVED******REMOVED******REMOVED*** Code Style

```bash
***REMOVED*** Run all linters
hatch run lint

***REMOVED*** Format code
hatch run format
```

***REMOVED******REMOVED*** API Examples

Base URL: `http://localhost:8002/reco/v1`

***REMOVED******REMOVED******REMOVED*** Get trending recommendations

```bash
curl "http://localhost:8002/reco/v1/trending?limit=10&days=7"
```

***REMOVED******REMOVED******REMOVED*** Get popular recommendations

```bash
curl "http://localhost:8002/reco/v1/popular?limit=10&min_rating=7.0&min_vote_count=1000"
```

***REMOVED******REMOVED******REMOVED*** Get personalized recommendations

```bash
curl "http://localhost:8002/reco/v1/users/123/recommendations?limit=10"
```

***REMOVED******REMOVED******REMOVED*** Get similar movies

```bash
curl "http://localhost:8002/reco/v1/movies/456/similar?limit=10"
```

***REMOVED******REMOVED*** System Integration

The Recommendation API integrates with several backend services:

```text
┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
│                   │         │                   │         │                   │
│    Backend API    │ ◄─────► │  Recommendation   │ ◄─────► │      Qdrant       │
│                   │         │       API         │         │  Vector Database  │
│                   │         │                   │         │                   │
└───────────────────┘         └───────────────────┘         └───────────────────┘
                                       │
                                       ▼
                              ┌───────────────────┐
                              │                   │
                              │      ML API       │
                              │                   │
                              └───────────────────┘
```
