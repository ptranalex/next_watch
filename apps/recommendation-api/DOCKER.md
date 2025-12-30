# Recommendation API Docker Build Guide

This document explains how to properly build and run the Recommendation API Docker container.

## Prerequisites

- Docker installed on your system
- Access to the Next Watch monorepo

## Building the Docker Image

The Recommendation API depends on the `movie-storage` package from the monorepo. The Dockerfile is designed to be built from the monorepo root to access all dependencies.

### Building from Monorepo Root

Always build the Docker image from the monorepo root directory:

```bash
# From the monorepo root (/Users/alex/Sandbox/next_watch)
docker build -t recommendation-api:latest -f apps/recommendation-api/Dockerfile .
```

This ensures that all dependencies, including the `movie-storage` package, are correctly included in the build.

## Running the Container

To run the container:

```bash
docker run -d --name recommendation-api \
  -p 8002:8002 \
  -e DATABASE_URL=postgresql://user:password@db-host:5432/next_watch \
  -e QDRANT_URL=http://qdrant-host:6333 \
  -e ENVIRONMENT=production \
  recommendation-api:latest
```

### Environment Variables

The following environment variables can be set:

- `DATABASE_URL`: PostgreSQL connection string
- `QDRANT_URL`: URL to the Qdrant vector database
- `QDRANT_COLLECTION`: Collection name in Qdrant (default: movies)
- `ENVIRONMENT`: Set to `production` for production mode
- `LOG_LEVEL`: Logging level (default: INFO)
- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to listen on (default: 8002)

## Health Check

The container includes a health check endpoint at `/health`. You can test it with:

```bash
curl http://localhost:8002/health
```

## Docker Compose Example

```yaml
version: "3.8"

services:
  recommendation-api:
    image: recommendation-api:latest
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/next_watch
      - QDRANT_URL=http://qdrant:6333
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - qdrant
```
