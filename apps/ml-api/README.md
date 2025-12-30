# ML API

Machine Learning API for the Next Watch platform, providing embedding generation services for movies and user preferences.

## Overview

The ML API is built with FastAPI and uses the sentence-transformers library to generate embeddings for movies and user preference vectors. It's now integrated with the fast-core framework for standardized patterns across Next Watch services.

## Features

- **Movie Embeddings**: Generate vector embeddings for movies based on metadata
- **User Preference Vectors**: Create preference vectors for users based on viewing history
- **Model Management**: Load and manage embedding models
- **Health Monitoring**: Comprehensive health checks and metrics
- **Fast-Core Integration**: Standardized middleware, configuration, and monitoring

## Quick Start

### Installation

```bash
cd apps/ml-api

# Install local dependencies
hatch run install-libs

# Run development server
hatch run dev
```

### Basic Usage

When running in development (`hatch run dev`), the ML API will be available at `http://localhost:8004` with the following endpoints:

- `POST /api/v1/embeddings/movie` - Generate movie embeddings
- `POST /api/v1/embeddings/user` - Generate user preference vectors
- `GET /api/v1/embeddings/info` - Get model information
- `GET /health` - Comprehensive health check (aggregated)
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe (critical dependencies)
- `GET /health/deep` - Deep diagnostics

### API Documentation

Interactive API documentation is available (in debug mode) at:

- Swagger UI: `http://localhost:8004/docs`
- ReDoc: `http://localhost:8004/redoc`

## Configuration

### Environment Variables

```bash
# Service configuration
SERVICE_NAME=ml-api
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# ML-specific configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
MODEL_CACHE_DIR=/app/model_cache
MAX_BATCH_SIZE=32
EMBEDDINGS_DB_PATH=/app/embeddings.db

# Feature flags
ENABLE_EMBEDDINGS=true
ENABLE_BATCH_PROCESSING=true
ENABLE_MODEL_CACHING=true
ENABLE_METRICS=true
```

### Configuration Files

The ML API supports configuration through:

- Environment variables
- `.env` files (`.env`, `.env.local`)
- Configuration validation with Pydantic

## Development

### Available Commands

```bash
# Development server with auto-reload
hatch run dev

# Production server
hatch run serve

# CLI interface
hatch run cli

# Code quality
hatch run lint
hatch run format

# Testing
hatch run test
hatch run test-cov

# Health checks
hatch run health-check

# Model management
hatch run model-info
hatch run model-load
```

### Package Structure

```text
src/ml_api/
├── main.py              # Main application entry point
├── __main__.py          # Module execution support
├── app.py               # Legacy FastAPI app (updated)
├── config/
│   ├── app.py           # MLAPIConfig (ServiceConfig-based)
│   └── fast_core_config.py  # Fast-core configuration adapter
├── core/
│   ├── __init__.py      # Exports create_app
│   ├── app_fast_core.py # Fast-core application factory
│   └── metrics.py       # ML-specific Prometheus metrics
├── cli/
│   ├── main.py          # CLI entry point
│   ├── __main__.py      # CLI module execution
│   └── commands/        # CLI command implementations
├── routes/
│   ├── embeddings.py    # Embedding API endpoints
│   └── health.py        # Health check endpoints
├── services/
│   └── embedding_service.py  # Embedding service implementation
├── models/
│   └── ...              # Pydantic models for API requests/responses
└── utils/
    └── ...              # Utility functions
```

## API Endpoints

### Movie Embeddings

```bash
# Generate movie embedding
curl -X POST "http://localhost:8004/api/v1/embeddings/movie" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": "123",
    "title": "The Matrix",
    "overview": "A computer hacker learns about the true nature of reality...",
    "genres": ["Action", "Sci-Fi"]
  }'
```

### User Preference Vectors

```bash
# Generate user preference vector
curl -X POST "http://localhost:8004/api/v1/embeddings/user" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "456",
    "liked_movies": [
      {"movie_id": "123", "rating": 5.0},
      {"movie_id": "124", "rating": 4.5}
    ],
    "watched_genres": {"Action": 1.0, "Sci-Fi": 0.8}
  }'
```

### Health Checks

```bash
# Comprehensive health check (all categories)
curl http://localhost:8004/health

# Liveness probe
curl http://localhost:8004/health/live

# Readiness probe (critical dependencies)
curl http://localhost:8004/health/ready

# Deep diagnostics
curl http://localhost:8004/health/deep

# Model information
curl http://localhost:8004/api/v1/embeddings/info
```

## Monitoring

### Metrics

The ML API exposes Prometheus metrics at `/metrics` including:

- `ml_embedding_requests_total` - Request counters by model and batch size
- `ml_embedding_duration_seconds` - Processing time histograms
- `ml_embedding_batch_size` - Batch size distribution
- `ml_model_load_duration_seconds` - Model loading performance
- `ml_model_memory_usage_bytes` - Model memory consumption
- `ml_embedding_errors_total` - Error counters by type

### Rate Limiting

- `/api/v1/embeddings/*`: 100 requests/minute
- `/health/*`: 1000 requests/minute

## Production Deployment

### Docker

The ML API can be deployed using Docker with the following considerations:

1. **Model Caching**: Mount a volume for model cache to avoid re-downloading
2. **Memory**: Ensure sufficient memory for model loading (typically 2-4GB)
3. **Environment**: Set production environment variables
4. **Security**: Configure proper CORS and allowed hosts

### Environment Configuration

```bash
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_HOSTS=ml-api.example.com
CORS_ORIGINS=https://backend.example.com,https://recommendation.example.com

# Performance settings
MAX_BATCH_SIZE=64
ENABLE_MODEL_CACHING=true
ENABLE_METRICS=true
```

## Fast-Core Integration

The ML API now uses the fast-core framework providing:

- **Standardized Configuration**: ServiceConfig-based configuration with validation
- **Enhanced Middleware**: CORS, security headers, rate limiting, logging, and metrics
- **Error Handling**: Consistent error responses and service error contexts
- **Monitoring**: Built-in health checks and Prometheus metrics
- **Security**: Production-ready security policies by default

For detailed information about the fast-core integration, see [FAST_CORE_INTEGRATION.md](FAST_CORE_INTEGRATION.md).

## Contributing

1. Follow the established patterns from other Next Watch services
2. Use the fast-core framework for consistency
3. Add tests for new features
4. Update documentation for API changes
5. Follow the coding standards (black, isort, ruff, mypy)

## License

MIT License - see LICENSE file for details.
