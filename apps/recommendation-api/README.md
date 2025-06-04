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
- **Embedding Generation**: Text embedding generation using SentenceTransformer

***REMOVED******REMOVED*** Docker

The service includes an optimized Dockerfile that significantly reduces image size and build time.

***REMOVED******REMOVED******REMOVED*** Dockerfile Features

- **Lightweight Image**: ~835MB (45% smaller than the original ~1.5GB image)
- **ML Dependencies Optional**: Excludes heavy ML libraries (PyTorch, transformers) to reduce size
- **Mock ML Implementation**: Provides mock implementations for ML features when running in lightweight mode
- **Fast Builds**: Optimized layer caching for quicker rebuilds
- **Production-Ready**: Includes health checks, non-root user, and proper environment setup

***REMOVED******REMOVED******REMOVED*** Docker Build Options

***REMOVED******REMOVED******REMOVED******REMOVED*** Lightweight Build (Default)

```bash
***REMOVED*** Build the lightweight image (no ML dependencies)
docker build -t recommendation-api .

***REMOVED*** Run the container
docker run -p 8002:8002 recommendation-api
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Full ML Build

```bash
***REMOVED*** Build the full image with ML dependencies
docker build -t recommendation-api-ml -f Dockerfile.ml .

***REMOVED*** Run the container with ML capabilities
docker run -p 8002:8002 recommendation-api-ml
```

***REMOVED******REMOVED******REMOVED*** Environment Variables

- `ENVIRONMENT`: Set to `production` by default
- `DISABLE_ML_FEATURES`: Set to `true` in the lightweight image, `false` in the ML image
- `PYTHONPATH`: Configured to include mock modules when needed

***REMOVED******REMOVED******REMOVED*** ML Features

The project provides two deployment options:

1. **Lightweight Mode** (`Dockerfile`): Uses mock ML implementations for faster startup and smaller image size
2. **Full ML Mode** (`Dockerfile.ml`): Includes all ML dependencies for complete functionality

***REMOVED******REMOVED******REMOVED******REMOVED*** When to Use Each Option

- **Use Lightweight Mode (`Dockerfile`) when**:

  - You need a smaller Docker image
  - You're running in development or testing environments
  - You're only using non-ML API endpoints (trending, popular)
  - You have pre-computed embeddings stored in Qdrant

- **Use Full ML Mode (`Dockerfile.ml`) when**:
  - You need to generate new embeddings
  - You require personalized recommendations based on content
  - You need accurate similar movie recommendations
  - You have sufficient system resources for ML operations

***REMOVED******REMOVED******REMOVED*** Docker Optimization Details

The Docker image was optimized to address two main issues:

1. **Size Reduction**: The original image was ~1.5GB, primarily due to ML dependencies:

   - PyTorch (~333MB)
   - Transformers (~56MB)
   - SentenceTransformers and related libraries

2. **Build Time**: The original build process was inefficient and slow

***REMOVED******REMOVED******REMOVED******REMOVED*** Optimization Approach

1. **Multi-stage Build**: Separates build dependencies from runtime dependencies
2. **Dependency Filtering**: Excludes ML libraries that account for most of the image size
3. **Mock Implementation**: Provides mock classes for ML functionality to maintain API compatibility
4. **Layer Caching**: Organizes Dockerfile commands to maximize cache hits during rebuilds

***REMOVED******REMOVED******REMOVED******REMOVED*** Trade-offs

- **Limited ML Functionality**: The lightweight image can't perform actual embedding generation
- **Mock Data**: Returns zero vectors instead of real embeddings
- **Deployment Strategy**: For full ML functionality, consider:
  - Using the `Dockerfile.ml` with ML dependencies
  - Implementing a separate ML microservice
  - Pre-computing embeddings and storing them in the vector database

***REMOVED******REMOVED*** Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   ***REMOVED*** Edit .env with your configuration
   ```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Running the API

```bash
***REMOVED*** Development mode
rec-api serve start --reload

***REMOVED*** Production mode
rec-api serve start --workers 4
```

***REMOVED******REMOVED******REMOVED*** API Endpoints

- `GET /api/v1/recommendations/` - General recommendations
- `GET /api/v1/recommendations/trending` - Trending recommendations
- `GET /api/v1/recommendations/popular` - Popular recommendations
- `GET /api/v1/recommendations/user/{user_id}` - User-specific recommendations
- `GET /api/v1/recommendations/similar/{movie_id}` - Similar movies

***REMOVED******REMOVED******REMOVED*** CLI Commands

```bash
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
rec-api embeddings generate [--batch-size SIZE] [--force] [--limit LIMIT] [--verbose]
rec-api embeddings status [--verbose]
rec-api embeddings cleanup [--dry-run/--execute] [--verbose]
rec-api embeddings info [--verbose]

***REMOVED*** Version Information
rec-api version
```

***REMOVED******REMOVED*** Configuration

The service is configured through environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DATABASE_URL`: SQLAlchemy database URL
- `QDRANT_URL`: Qdrant vector database URL
- `EMBEDDING_MODEL`: SentenceTransformer model name
- `LOG_LEVEL`: Logging level (default: INFO)

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
pytest
```

***REMOVED******REMOVED******REMOVED*** Code Style

```bash
***REMOVED*** Run linters
ruff check .

***REMOVED*** Run type checking
mypy .
```

***REMOVED******REMOVED*** API Examples

***REMOVED******REMOVED******REMOVED*** Get trending recommendations

```bash
curl "http://localhost:8000/api/v1/recommendations/trending?limit=10&days=7"
```

***REMOVED******REMOVED******REMOVED*** Get personalized recommendations

```bash
curl "http://localhost:8000/api/v1/recommendations/user/123?limit=10"
```

***REMOVED******REMOVED******REMOVED*** Get similar movies

```bash
curl "http://localhost:8000/api/v1/recommendations/similar/456?limit=10"
```
