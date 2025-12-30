# Recommendation API

AI-powered movie recommendation service for the Next Watch platform, built with FastAPI and modern Python architecture patterns.

## Overview

The Recommendation API provides intelligent movie recommendations using machine learning algorithms, vector similarity search, and collaborative filtering. It's designed with Clean Architecture principles, microservices integration, and comprehensive health monitoring.

## 🏗️ Architecture

The application follows Clean Architecture with clear separation of concerns:

```
recommendation_api/
├── main.py              # Application entry point
├── __main__.py          # Module execution entry
├── __init__.py          # Package initialization
├── core/                # Application factory & lifecycle
├── routes/              # API endpoints & routing
├── services/            # Business logic layer
├── repositories/        # Data access layer
├── models/              # Data models & schemas
├── config/              # Configuration management
├── db/                  # Database operations
├── cli/                 # Command-line interface
└── utils/               # Utility functions
```

### Layer Responsibilities

- **Routes**: FastAPI endpoints, request/response handling
- **Services**: Business logic, recommendation algorithms
- **Repositories**: Data access abstraction (Redis, Qdrant, PostgreSQL)
- **Models**: Pydantic models for data validation
- **Core**: Application factory, middleware, lifecycle management
- **Config**: Settings, environment configuration
- **CLI**: Command-line tools for operations

## 🚀 Quick Start

### Running the Application

```bash
# Start the recommendation API server
rec-api serve start --port 8002

# Or run directly with Python
python -m recommendation_api

# Or using the main module
python src/recommendation_api/main.py
```

### Health Checks

```bash
# Comprehensive health check
curl http://localhost:8002/health

# Simple liveness check
curl http://localhost:8002/health/live

# Readiness check
curl http://localhost:8002/health/ready
```

### API Documentation

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

## 📡 API Endpoints

### Core Endpoints

```
GET /                    # API information and available endpoints
GET /health             # Comprehensive health check (PostgreSQL, Redis, Qdrant)
GET /health/live        # Simple liveness check
GET /health/ready       # Readiness check for critical dependencies
```

### Recommendation Endpoints

```
GET /reco/v1/recommendations/personalized/{user_id}  # Personalized recommendations
GET /reco/v1/recommendations/popular                 # Popular movies
GET /reco/v1/recommendations/similar/{movie_id}      # Similar movies
GET /reco/v1/recommendations/trending                # Trending movies
```

## 🧠 Recommendation Algorithms

### Content-Based Filtering

- **Vector Similarity**: Uses movie embeddings for semantic similarity
- **Feature Matching**: Matches based on genres, directors, actors
- **ML Integration**: Leverages external ML API for embedding generation

### Collaborative Filtering

- **User-Based**: Recommendations based on similar users
- **Item-Based**: Recommendations based on item relationships
- **Hybrid Approach**: Combines multiple algorithms

### Trending & Popular

- **Time-Based Trending**: Recent popularity with decay
- **Rating-Based Popular**: Highest-rated movies with minimum vote threshold
- **Personalized Trending**: Trending movies filtered by user preferences

## 🏛️ Architecture Patterns

### Application Factory Pattern

```python
from recommendation_api.core import create_app

# Clean app creation with dependency injection
app = create_app()
```

### Repository Pattern

```python
from recommendation_api.repositories.redis import RedisRepository
from recommendation_api.repositories.vector import VectorRepository

# Clean data access abstraction
redis_repo = RedisRepository()
vector_repo = VectorRepository()
```

### Service Layer Pattern

```python
from recommendation_api.services.recommendation import RecommendationService

# Business logic encapsulation
service = RecommendationService(session)
recommendations = service.get_trending_recommendations()
```

## 🔧 Dependencies & Infrastructure

### External Services

- **PostgreSQL**: Primary database for movies, users, ratings
- **Redis**: Caching layer for recommendations and sessions
- **Qdrant**: Vector database for similarity search
- **ML API**: External service for embedding generation

### Key Libraries

- **FastAPI**: Modern async web framework
- **SQLModel**: SQL databases with Python type hints
- **Pydantic**: Data validation and serialization
- **asyncpg**: Async PostgreSQL driver
- **redis-py**: Redis client
- **qdrant-client**: Vector database client
- **httpx**: Async HTTP client for ML API

## 🛠️ Development Tools

### Command Line Interface

```bash
# Health checks
rec-api health check

# Cache management
rec-api cache precompute --batch-size 10
rec-api cache clear --pattern "recommendations:*"

# Embedding operations
rec-api embeddings generate --batch-size 100
rec-api embeddings repair --failed-only

# Configuration
rec-api config show
rec-api config validate
```

### Development Commands

```bash
# Install dependencies
pip install -e .

# Run tests
pytest

# Code formatting
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

## 📊 Monitoring & Health

### Health Monitoring

The application provides comprehensive health monitoring:

- **Database Health**: PostgreSQL connectivity and query performance
- **Cache Health**: Redis connectivity and operation latency
- **Vector DB Health**: Qdrant connectivity and collection status
- **External API Health**: ML API connectivity and response times

### Metrics & Logging

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Performance Metrics**: Response times, cache hit rates, error rates
- **Health Dashboards**: Real-time monitoring of all dependencies
- **Alerting**: Automated alerts for service degradation

## 🔒 Security & Configuration

### Environment Configuration

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/next_watch

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=movies

# ML API
ML_API_URL=http://localhost:8001
ML_API_TIMEOUT=30

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false
```

### Security Features

- **CORS Configuration**: Configurable cross-origin policies
- **Host Validation**: Trusted host middleware in production
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without information leakage

## 🧪 Testing

### Test Structure

```
tests/
├── unit/               # Unit tests for individual components
├── integration/        # Integration tests for service interactions
├── e2e/               # End-to-end API tests
└── fixtures/          # Test data and fixtures
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=recommendation_api
```

## 📦 Deployment

### Docker Support

```bash
# Build image
docker build -t recommendation-api .

# Run container
docker run -p 8002:8002 recommendation-api

# Docker Compose
docker-compose up -d
```

### Health Checks in Production

The application includes Docker health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1
```

## 🔄 Data Flow

### Recommendation Generation Flow

1. **Request**: User requests recommendations via API
2. **Cache Check**: Check Redis for cached results
3. **Algorithm Selection**: Choose appropriate recommendation algorithm
4. **Data Retrieval**: Fetch data from PostgreSQL and Qdrant
5. **ML Processing**: Generate embeddings via ML API if needed
6. **Ranking**: Apply business rules and ranking algorithms
7. **Caching**: Store results in Redis for future requests
8. **Response**: Return formatted recommendations

### Embedding Generation Flow

1. **Movie Features**: Extract movie metadata (title, overview, genres)
2. **ML API Call**: Send features to external ML service
3. **Vector Storage**: Store embeddings in Qdrant
4. **Indexing**: Update vector indexes for similarity search
5. **Caching**: Cache embeddings for quick retrieval

## 📚 Module Documentation

Each module has detailed documentation:

- **[Core](core/README.md)**: Application factory and lifecycle management
- **[Routes](routes/README.md)**: API endpoints and routing
- **[Services](services/README.md)**: Business logic and algorithms
- **[Repositories](repositories/README.md)**: Data access patterns
- **[Models](models/README.md)**: Data models and validation
- **[Config](config/README.md)**: Configuration management
- **[CLI](cli/README.md)**: Command-line interface
- **[Database](db/README.md)**: Database operations

## 🤝 Contributing

### Development Setup

1. **Clone Repository**: `git clone <repository-url>`
2. **Install Dependencies**: `pip install -e .[dev]`
3. **Setup Environment**: Copy `.env.example` to `.env`
4. **Run Services**: Start PostgreSQL, Redis, Qdrant
5. **Run Tests**: `pytest` to ensure everything works
6. **Start Development**: `rec-api serve start --reload`

### Code Standards

- **Type Hints**: All functions must have type annotations
- **Documentation**: Docstrings for all public functions
- **Testing**: Minimum 80% test coverage
- **Formatting**: Use Black and isort for code formatting
- **Linting**: Pass flake8 and mypy checks

## 📈 Performance

### Optimization Strategies

- **Caching**: Multi-level caching (Redis, in-memory)
- **Connection Pooling**: Efficient database connections
- **Async Operations**: Non-blocking I/O for all external calls
- **Batch Processing**: Bulk operations for embeddings
- **Vector Indexing**: Optimized similarity search

### Scalability

- **Horizontal Scaling**: Stateless application design
- **Microservices**: ML processing in separate service
- **Load Balancing**: Multiple API instances
- **Database Sharding**: Planned for large datasets

## 🔮 Future Roadmap

### Short Term

- [ ] User authentication and authorization
- [ ] A/B testing framework for algorithms
- [ ] Real-time recommendation updates
- [ ] Advanced caching strategies

### Long Term

- [ ] Multi-modal recommendations (text, images, video)
- [ ] Real-time user behavior tracking
- [ ] Advanced personalization algorithms
- [ ] Recommendation explanation system

## 📄 License

This project is part of the Next Watch platform. See the main repository for license information.

## 🆘 Support

For questions, issues, or contributions:

1. **Documentation**: Check module-specific READMEs
2. **Issues**: Create GitHub issues for bugs
3. **Discussions**: Use GitHub discussions for questions
4. **Health Checks**: Use `/health` endpoints for diagnostics
