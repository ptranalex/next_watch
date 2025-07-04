***REMOVED*** Recommendation API

A FastAPI service for generating movie recommendations for the Next Watch platform.

***REMOVED******REMOVED*** Overview

This API provides endpoints for various types of movie recommendations:

- Trending recommendations based on recent popularity
- Popular recommendations based on rating and vote count
- Personalized recommendations based on user preferences
- Similar movie recommendations based on content similarity

***REMOVED******REMOVED*** Architecture

The application follows a clean architecture approach with these main components:

```
recommendation_api/
├── models/           ***REMOVED*** Data models for API requests/responses
├── routes/           ***REMOVED*** API endpoints and request handling
├── services/         ***REMOVED*** Business logic and service layer
├── repositories/     ***REMOVED*** Data access layer
│   └── vector/       ***REMOVED*** Vector database access
│   └── redis/        ***REMOVED*** Redis cache access
├── db/               ***REMOVED*** Database connections and models
├── ml/               ***REMOVED*** Machine learning components
├── config/           ***REMOVED*** Application configuration
└── cli/              ***REMOVED*** Command-line interface
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
hatch run dev:test

***REMOVED*** Run tests with coverage
hatch run dev:test-cov

***REMOVED*** Run linters and formatters
hatch run dev:lint

***REMOVED*** Format code
hatch run dev:format
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

- `ENVIRONMENT`: Set to `production` by default
- `ML_API_URL`: URL of the ML API service
- `REDIS_URL`: URL for Redis cache (default: redis://localhost:6379/0)
- `PYTHONPATH`: Configured to include necessary modules

***REMOVED******REMOVED******REMOVED*** Microservices Architecture

The recommendation system now follows a microservices architecture:

```
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
rec-api health ping SERVICE  ***REMOVED*** SERVICE can be: api, db, qdrant, ml-api

***REMOVED*** Embeddings Management
rec-api embeddings generate [--batch-size SIZE] [--force] [--limit LIMIT] [--verbose]
rec-api embeddings status [--verbose]
rec-api embeddings cleanup [--dry-run/--execute] [--verbose]
rec-api embeddings info [--verbose]

***REMOVED*** ML API Commands
rec-api ml test-connection
rec-api ml info

***REMOVED*** Version Information
rec-api version

***REMOVED*** Cache Management
rec-api cache info [--verbose]
rec-api cache clear [--force]
rec-api cache precompute [--limit N] [--min-score SCORE] [--batch-size SIZE] [--ttl SECONDS] [--movie-id ID]
```

***REMOVED******REMOVED*** Configuration

The service is configured through environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8002)
- `DATABASE_URL`: SQLAlchemy database URL
- `QDRANT_URL`: Qdrant vector database URL
- `ML_API_URL`: URL for the ML API service
- `LOG_LEVEL`: Logging level (default: INFO)

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
hatch run dev:test
```

***REMOVED******REMOVED******REMOVED*** Code Style

```bash
***REMOVED*** Run all linters
hatch run dev:lint

***REMOVED*** Format code
hatch run dev:format
```

***REMOVED******REMOVED*** API Examples

***REMOVED******REMOVED******REMOVED*** Get trending recommendations

```bash
curl "http://localhost:8002/api/v1/recommendations/trending?limit=10&days=7"
```

***REMOVED******REMOVED******REMOVED*** Get personalized recommendations

```bash
curl "http://localhost:8002/api/v1/recommendations/user/123?limit=10"
```

***REMOVED******REMOVED******REMOVED*** Get similar movies

```bash
curl "http://localhost:8002/api/v1/recommendations/similar/456?limit=10"
```

***REMOVED******REMOVED*** System Integration

The Recommendation API integrates with several backend services:

```
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

***REMOVED*** TEST

---
