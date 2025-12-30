# Recommendation API

A FastAPI service for generating movie recommendations for the Next Watch platform.

## Overview

This API provides endpoints for various types of movie recommendations:

- Trending recommendations based on recent popularity
- Popular recommendations based on rating and vote count
- Personalized recommendations based on user preferences
- Similar movie recommendations based on content similarity

Base URL: `/reco/v1`

## Architecture

The application follows a clean architecture approach with these main components:

```text
recommendation_api/
├── models/           # Data models for API requests/responses
├── routes/           # API endpoints and request handling
│   └── v1/           # Versioned recommendation endpoints
├── services/         # Business logic and integrations
│   └── cache_service # Cache helpers and background warming
│   └── clients/      # Backend/Movies HTTP clients
├── repositories/     # Data access layer
│   └── vector/       # Qdrant vector DB access
│   └── redis/        # Redis cache access
├── db/               # Database utilities and operations
├── core/             # App factory, middleware, metrics (fast-core)
├── config/           # Application configuration (via shared config lib)
└── cli/              # Typer-based command-line interface
```

### Key Components

- **API Routes**: FastAPI endpoints for handling HTTP requests
- **Service Layer**: Business logic for recommendations
- **Repository Layer**: Data access abstractions
- **Vector Storage**: Qdrant vector database for similarity search
- **Redis Cache**: Redis for caching similar movie recommendations
- **ML API Client**: Client for communicating with the ML API service

## Dependencies

The service relies on several key dependencies:

- **FastAPI**: Web framework for building APIs
- **SQLAlchemy/SQLModel**: ORM for database interactions
- **Qdrant Client**: Client for vector database operations
- **Asyncpg**: Async PostgreSQL driver (required for CLI health checks and database operations)
- **Typer/Rich**: CLI framework and formatting
- **HTTPX**: Async HTTP client for ML API communication

## Development with Hatch

The project now uses [Hatch](https://hatch.pypa.io/) for project management, which provides isolated environments, streamlined dependency management, and standardized development workflows.

### Getting Started with Hatch

1. Install Hatch:

   ```bash
   pip install hatch
   ```

2. Create development environment:

   ```bash
   # This will create an isolated environment with all dependencies
   hatch env create
   ```

3. Run the API in development mode:

   ```bash
   # Start the API with hot reloading
   hatch run dev
   ```

### Common Hatch Commands

```bash
# Run the application
hatch run serve

# Run development server with hot reloading
hatch run dev

# Run CLI commands
hatch run cli -- embeddings status

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run linters and formatters
hatch run lint

# Format code
hatch run format
```

## Docker

The service includes an optimized Dockerfile that significantly reduces image size and build time.

### Dockerfile Features

- **Lightweight Image**: ~835MB (45% smaller than the original ~1.5GB image)
- **ML Dependencies Optional**: Excludes heavy ML libraries (PyTorch, transformers) to reduce size
- **Production-Ready**: Includes health checks, non-root user, and proper environment setup

### Docker Build Options

#### Lightweight Build (Default)

```bash
# Build the lightweight image (no ML dependencies)
docker build -t recommendation-api .

# Run the container
docker run -p 8002:8002 recommendation-api
```

### Environment Variables

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

### Microservices Architecture

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

## Installation

1. Clone the repository
2. Install using Hatch:

   ```bash
   pip install hatch
   hatch env create
   ```

3. Configure environment:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Usage

### Running the API

```bash
# Development mode with hot reloading
hatch run dev

# Production mode
hatch run serve
```

### CLI Commands

```bash
# Using Hatch
hatch run cli -- [COMMAND]

# Or using the installed CLI (if package is installed)
rec-api [COMMAND]

# Show available commands
rec-api --help

# Server Management
rec-api serve start [--host HOST] [--port PORT] [--reload] [--log-level LEVEL] [--verbose] [--quiet]
rec-api serve stop
rec-api serve restart

# Configuration
rec-api config show [--show-secrets] [--verbose]
rec-api config validate
rec-api config env

# Health Checks
rec-api health check
rec-api health ping SERVICE  # SERVICE can be: api, db, qdrant

# Embeddings Management
rec-api embeddings generate [--batch-size SIZE] [--force] [--limit LIMIT] [--movie-id ID] [--verbose]
rec-api embeddings status [--verbose]
rec-api embeddings cleanup [--dry-run/--execute] [--verbose]
rec-api embeddings info [--verbose]
rec-api embeddings repair_embeddings [--batch-size SIZE] [--movie-id ID] [--dry-run] [--verbose]

# ML API Commands
rec-api ml test-connection
rec-api ml generate-embedding "Title" "Overview..." --genres "Drama,Thriller" --id 123

# Version Information
rec-api version

# Cache Management
rec-api cache info [--verbose]
rec-api cache clear [--force]
rec-api cache precompute [--limit N] [--min-score SCORE] [--batch-size SIZE] [--ttl SECONDS] [--movie-id ID]
```

## Configuration

The service is configured via environment variables and the shared `config` library. See Environment Variables above for the most important keys.

## Development

### Running Tests

```bash
hatch run test
```

### Code Style

```bash
# Run all linters
hatch run lint

# Format code
hatch run format
```

## API Examples

Base URL: `http://localhost:8002/reco/v1`

### Get trending recommendations

```bash
curl "http://localhost:8002/reco/v1/trending?limit=10&days=7"
```

### Get popular recommendations

```bash
curl "http://localhost:8002/reco/v1/popular?limit=10&min_rating=7.0&min_vote_count=1000"
```

### Get personalized recommendations

```bash
curl "http://localhost:8002/reco/v1/users/123/recommendations?limit=10"
```

### Get similar movies

```bash
curl "http://localhost:8002/reco/v1/movies/456/similar?limit=10"
```

## System Integration

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
