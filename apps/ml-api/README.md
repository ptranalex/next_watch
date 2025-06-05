***REMOVED*** ML API

A dedicated microservice for machine learning operations to support the Next Watch recommendation system.

***REMOVED******REMOVED*** Overview

The ML API is a specialized service that handles all machine learning tasks for the Next Watch platform, specifically focused on generating embeddings for movies and user preferences. This service was extracted from the recommendation-api to:

1. Separate resource-intensive ML operations from recommendation logic
2. Allow independent scaling of ML components
3. Simplify the recommendation-api codebase
4. Enable specialized deployment options for ML workloads

***REMOVED******REMOVED*** Architecture

The ML API follows a clean architecture approach with these main components:

```
ml_api/
├── models/      ***REMOVED*** Data models for API requests/responses
├── routes/      ***REMOVED*** API endpoints and request handling
├── services/    ***REMOVED*** ML processing logic and model management
├── config/      ***REMOVED*** Application configuration
├── utils/       ***REMOVED*** Utility functions and helpers
└── tests/       ***REMOVED*** Unit and integration tests
```

***REMOVED******REMOVED******REMOVED*** Key Components

- **API Routes**: FastAPI endpoints for handling embedding generation requests
- **ML Service**: Manages the embedding model lifecycle and processing
- **Model Management**: Handles loading, caching, and versioning of ML models
- **Configuration**: Environment-based configuration for different deployment scenarios

***REMOVED******REMOVED*** System Integration

```
┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
│                   │         │                   │         │                   │
│  recommendation   │ ◄─────► │      ml-api       │         │      Qdrant       │
│      -api         │         │                   │         │  Vector Database  │
│                   │         │                   │         │                   │
└───────────────────┘         └───────────────────┘         └───────────────────┘
        ▲                                                           ▲
        │                                                           │
        │                                                           │
        ▼                                                           │
┌───────────────────┐                                               │
│                   │                                               │
│    PostgreSQL     │ ──────────────────────────────────────────────┘
│    Database       │          (recommendation-api stores vectors)
│                   │
└───────────────────┘
```

***REMOVED******REMOVED******REMOVED*** Data Flow

1. **recommendation-api** sends movie/user data to **ml-api**
2. **ml-api** processes data and returns vector embeddings
3. **recommendation-api** stores these embeddings in **Qdrant**
4. **recommendation-api** uses these embeddings for similarity searches and recommendations

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** Movie Embedding Generation

```
POST /api/v1/embeddings/movie
```

Request:

```json
{
  "movie_id": "123",
  "title": "The Matrix",
  "overview": "A computer hacker learns about the true nature of reality.",
  "genres": ["sci-fi", "action"],
  "additional_metadata": {
    "director": "Lana Wachowski, Lilly Wachowski",
    "actors": ["Keanu Reeves", "Laurence Fishburne"]
  }
}
```

Response:

```json
{
  "movie_id": "123",
  "embedding": [0.1, 0.2, ...],
  "model_id": "all-MiniLM-L6-v2",
  "dimensions": 384
}
```

***REMOVED******REMOVED******REMOVED*** User Preference Vector

```
POST /api/v1/embeddings/user
```

Request:

```json
{
  "user_id": "456",
  "liked_movies": [
    {
      "movie_id": "123",
      "rating": 5.0
    },
    {
      "movie_id": "124",
      "rating": 4.5
    }
  ],
  "watched_genres": {
    "action": 0.8,
    "sci-fi": 0.7,
    "comedy": 0.3
  }
}
```

Response:

```json
{
  "user_id": "456",
  "preference_vector": [0.3, 0.1, ...],
  "model_id": "all-MiniLM-L6-v2",
  "dimensions": 384
}
```

***REMOVED******REMOVED******REMOVED*** Model Information

```
GET /api/v1/info
```

Response:

```json
{
  "model_id": "all-MiniLM-L6-v2",
  "dimensions": 384,
  "version": "1.0.0",
  "status": "loaded",
  "health": "ok",
  "stats": {
    "requests_processed": 1250,
    "average_processing_time_ms": 45.3
  }
}
```

***REMOVED******REMOVED*** Installation

1. Clone the repository
2. Install dependencies with Hatch:
   ```bash
   cd apps/ml-api
   pip install hatch
   hatch env create
   ```
3. Configure environment:
   ```bash
   cp env.example .env
   ***REMOVED*** Edit .env with your configuration
   ```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Development Mode

Use Hatch for local development to benefit from its environment management:

```bash
***REMOVED*** Run the API in development mode
hatch run serve

***REMOVED*** Run the API with auto-reload
hatch run dev
```

***REMOVED******REMOVED******REMOVED*** Production Mode

For production environments, the service runs directly without Hatch:

```bash
***REMOVED*** Run with Python directly
python -m ml_api.app

***REMOVED*** Or using the installed CLI
ml-api serve start --workers 4
```

***REMOVED******REMOVED******REMOVED*** Development Tasks

```bash
***REMOVED*** Run tests
hatch run dev:test

***REMOVED*** Run tests with coverage
hatch run dev:test-cov

***REMOVED*** Format code
hatch run dev:format

***REMOVED*** Lint code
hatch run dev:lint
```

***REMOVED******REMOVED******REMOVED*** CLI Commands

Development (with Hatch):

```bash
***REMOVED*** Show available commands
hatch run ml-api --help

***REMOVED*** Server Management
hatch run ml-api serve start [--host HOST] [--port PORT] [--reload] [--log-level LEVEL]
```

Production (direct execution):

```bash
***REMOVED*** Show available commands
ml-api --help

***REMOVED*** Server Management
ml-api serve start [--host HOST] [--port PORT] [--workers WORKERS] [--log-level LEVEL]

***REMOVED*** Configuration
ml-api config show [--verbose]
ml-api config validate

***REMOVED*** Health and Model Commands
ml-api health check
ml-api model info
ml-api model status
```

***REMOVED******REMOVED*** Configuration

The service is configured through environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8004)
- `EMBEDDING_MODEL`: SentenceTransformer model name (default: all-MiniLM-L6-v2)
- `MODEL_CACHE_DIR`: Directory to cache downloaded models
- `LOG_LEVEL`: Logging level (default: INFO)
- `MAX_BATCH_SIZE`: Maximum batch size for embedding generation (default: 32)

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
***REMOVED*** Run all tests
hatch run dev:test

***REMOVED*** Run tests with coverage
hatch run dev:test-cov
```

***REMOVED******REMOVED******REMOVED*** Code Style

```bash
***REMOVED*** Run linters
hatch run dev:lint  ***REMOVED*** Runs black, isort, ruff, and mypy

***REMOVED*** Format code only
hatch run dev:format  ***REMOVED*** Runs black and isort
```

***REMOVED******REMOVED*** Docker

```bash
***REMOVED*** Build the image
docker build -t ml-api .

***REMOVED*** Run the container
docker run -p 8004:8004 ml-api
```
