***REMOVED*** Recommendation API

AI-powered movie recommendation service for the Next Watch platform, built with FastAPI and modern Python architecture patterns.

***REMOVED******REMOVED*** Overview

The Recommendation API provides intelligent movie recommendations using machine learning algorithms, vector similarity search, and collaborative filtering. It's designed with Clean Architecture principles, microservices integration, and comprehensive health monitoring.

***REMOVED******REMOVED*** 🏗️ Architecture

The application follows Clean Architecture with clear separation of concerns:

```
recommendation_api/
├── main.py              ***REMOVED*** Application entry point
├── __main__.py          ***REMOVED*** Module execution entry
├── __init__.py          ***REMOVED*** Package initialization
├── core/                ***REMOVED*** Application factory & lifecycle
├── routes/              ***REMOVED*** API endpoints & routing
├── services/            ***REMOVED*** Business logic layer
├── repositories/        ***REMOVED*** Data access layer
├── models/              ***REMOVED*** Data models & schemas
├── config/              ***REMOVED*** Configuration management
├── db/                  ***REMOVED*** Database operations
├── cli/                 ***REMOVED*** Command-line interface
└── utils/               ***REMOVED*** Utility functions
```

***REMOVED******REMOVED******REMOVED*** Layer Responsibilities

- **Routes**: FastAPI endpoints, request/response handling
- **Services**: Business logic, recommendation algorithms
- **Repositories**: Data access abstraction (Redis, Qdrant, PostgreSQL)
- **Models**: Pydantic models for data validation
- **Core**: Application factory, middleware, lifecycle management
- **Config**: Settings, environment configuration
- **CLI**: Command-line tools for operations

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Running the Application

```bash
***REMOVED*** Start the recommendation API server
rec-api serve start --port 8002

***REMOVED*** Or run directly with Python
python -m recommendation_api

***REMOVED*** Or using the main module
python src/recommendation_api/main.py
```

***REMOVED******REMOVED******REMOVED*** Health Checks

```bash
***REMOVED*** Comprehensive health check
curl http://localhost:8002/health

***REMOVED*** Simple liveness check
curl http://localhost:8002/health/live

***REMOVED*** Readiness check
curl http://localhost:8002/health/ready
```

***REMOVED******REMOVED******REMOVED*** API Documentation

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

***REMOVED******REMOVED*** 📡 API Endpoints

***REMOVED******REMOVED******REMOVED*** Core Endpoints

```
GET /                    ***REMOVED*** API information and available endpoints
GET /health             ***REMOVED*** Comprehensive health check (PostgreSQL, Redis, Qdrant)
GET /health/live        ***REMOVED*** Simple liveness check
GET /health/ready       ***REMOVED*** Readiness check for critical dependencies
```

***REMOVED******REMOVED******REMOVED*** Recommendation Endpoints

```
GET /reco/v1/recommendations/personalized/{user_id}  ***REMOVED*** Personalized recommendations
GET /reco/v1/recommendations/popular                 ***REMOVED*** Popular movies
GET /reco/v1/recommendations/similar/{movie_id}      ***REMOVED*** Similar movies
GET /reco/v1/recommendations/trending                ***REMOVED*** Trending movies
```

***REMOVED******REMOVED*** 🧠 Recommendation Algorithms

***REMOVED******REMOVED******REMOVED*** Content-Based Filtering

- **Vector Similarity**: Uses movie embeddings for semantic similarity
- **Feature Matching**: Matches based on genres, directors, actors
- **ML Integration**: Leverages external ML API for embedding generation

***REMOVED******REMOVED******REMOVED*** Collaborative Filtering

- **User-Based**: Recommendations based on similar users
- **Item-Based**: Recommendations based on item relationships
- **Hybrid Approach**: Combines multiple algorithms

***REMOVED******REMOVED******REMOVED*** Trending & Popular

- **Time-Based Trending**: Recent popularity with decay
- **Rating-Based Popular**: Highest-rated movies with minimum vote threshold
- **Personalized Trending**: Trending movies filtered by user preferences

***REMOVED******REMOVED*** 🏛️ Architecture Patterns

***REMOVED******REMOVED******REMOVED*** Application Factory Pattern

```python
from recommendation_api.core import create_app

***REMOVED*** Clean app creation with dependency injection
app = create_app()
```

***REMOVED******REMOVED******REMOVED*** Repository Pattern

```python
from recommendation_api.repositories.redis import RedisRepository
from recommendation_api.repositories.vector import VectorRepository

***REMOVED*** Clean data access abstraction
redis_repo = RedisRepository()
vector_repo = VectorRepository()
```

***REMOVED******REMOVED******REMOVED*** Service Layer Pattern

```python
from recommendation_api.services.recommendation import RecommendationService

***REMOVED*** Business logic encapsulation
service = RecommendationService(session)
recommendations = service.get_trending_recommendations()
```

***REMOVED******REMOVED*** 🔧 Dependencies & Infrastructure

***REMOVED******REMOVED******REMOVED*** External Services

- **PostgreSQL**: Primary database for movies, users, ratings
- **Redis**: Caching layer for recommendations and sessions
- **Qdrant**: Vector database for similarity search
- **ML API**: External service for embedding generation

***REMOVED******REMOVED******REMOVED*** Key Libraries

- **FastAPI**: Modern async web framework
- **SQLModel**: SQL databases with Python type hints
- **Pydantic**: Data validation and serialization
- **asyncpg**: Async PostgreSQL driver
- **redis-py**: Redis client
- **qdrant-client**: Vector database client
- **httpx**: Async HTTP client for ML API

***REMOVED******REMOVED*** 🛠️ Development Tools

***REMOVED******REMOVED******REMOVED*** Command Line Interface

```bash
***REMOVED*** Health checks
rec-api health check

***REMOVED*** Cache management
rec-api cache precompute --batch-size 10
rec-api cache clear --pattern "recommendations:*"

***REMOVED*** Embedding operations
rec-api embeddings generate --batch-size 100
rec-api embeddings repair --failed-only

***REMOVED*** Configuration
rec-api config show
rec-api config validate
```

***REMOVED******REMOVED******REMOVED*** Development Commands

```bash
***REMOVED*** Install dependencies
pip install -e .

***REMOVED*** Run tests
pytest

***REMOVED*** Code formatting
black src/
isort src/

***REMOVED*** Type checking
mypy src/

***REMOVED*** Linting
flake8 src/
```

***REMOVED******REMOVED*** 📊 Monitoring & Health

***REMOVED******REMOVED******REMOVED*** Health Monitoring

The application provides comprehensive health monitoring:

- **Database Health**: PostgreSQL connectivity and query performance
- **Cache Health**: Redis connectivity and operation latency
- **Vector DB Health**: Qdrant connectivity and collection status
- **External API Health**: ML API connectivity and response times

***REMOVED******REMOVED******REMOVED*** Metrics & Logging

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Performance Metrics**: Response times, cache hit rates, error rates
- **Health Dashboards**: Real-time monitoring of all dependencies
- **Alerting**: Automated alerts for service degradation

***REMOVED******REMOVED*** 🔒 Security & Configuration

***REMOVED******REMOVED******REMOVED*** Environment Configuration

```bash
***REMOVED*** Database
DATABASE_URL=postgresql://user:pass@localhost:5432/next_watch

***REMOVED*** Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

***REMOVED*** Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=movies

***REMOVED*** ML API
ML_API_URL=http://localhost:8001
ML_API_TIMEOUT=30

***REMOVED*** Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false
```

***REMOVED******REMOVED******REMOVED*** Security Features

- **CORS Configuration**: Configurable cross-origin policies
- **Host Validation**: Trusted host middleware in production
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without information leakage

***REMOVED******REMOVED*** 🧪 Testing

***REMOVED******REMOVED******REMOVED*** Test Structure

```
tests/
├── unit/               ***REMOVED*** Unit tests for individual components
├── integration/        ***REMOVED*** Integration tests for service interactions
├── e2e/               ***REMOVED*** End-to-end API tests
└── fixtures/          ***REMOVED*** Test data and fixtures
```

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
***REMOVED*** All tests
pytest

***REMOVED*** Unit tests only
pytest tests/unit/

***REMOVED*** Integration tests
pytest tests/integration/

***REMOVED*** With coverage
pytest --cov=recommendation_api
```

***REMOVED******REMOVED*** 📦 Deployment

***REMOVED******REMOVED******REMOVED*** Docker Support

```bash
***REMOVED*** Build image
docker build -t recommendation-api .

***REMOVED*** Run container
docker run -p 8002:8002 recommendation-api

***REMOVED*** Docker Compose
docker-compose up -d
```

***REMOVED******REMOVED******REMOVED*** Health Checks in Production

The application includes Docker health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1
```

***REMOVED******REMOVED*** 🔄 Data Flow

***REMOVED******REMOVED******REMOVED*** Recommendation Generation Flow

1. **Request**: User requests recommendations via API
2. **Cache Check**: Check Redis for cached results
3. **Algorithm Selection**: Choose appropriate recommendation algorithm
4. **Data Retrieval**: Fetch data from PostgreSQL and Qdrant
5. **ML Processing**: Generate embeddings via ML API if needed
6. **Ranking**: Apply business rules and ranking algorithms
7. **Caching**: Store results in Redis for future requests
8. **Response**: Return formatted recommendations

***REMOVED******REMOVED******REMOVED*** Embedding Generation Flow

1. **Movie Features**: Extract movie metadata (title, overview, genres)
2. **ML API Call**: Send features to external ML service
3. **Vector Storage**: Store embeddings in Qdrant
4. **Indexing**: Update vector indexes for similarity search
5. **Caching**: Cache embeddings for quick retrieval

***REMOVED******REMOVED*** 📚 Module Documentation

Each module has detailed documentation:

- **[Core](core/README.md)**: Application factory and lifecycle management
- **[Routes](routes/README.md)**: API endpoints and routing
- **[Services](services/README.md)**: Business logic and algorithms
- **[Repositories](repositories/README.md)**: Data access patterns
- **[Models](models/README.md)**: Data models and validation
- **[Config](config/README.md)**: Configuration management
- **[CLI](cli/README.md)**: Command-line interface
- **[Database](db/README.md)**: Database operations

***REMOVED******REMOVED*** 🤝 Contributing

***REMOVED******REMOVED******REMOVED*** Development Setup

1. **Clone Repository**: `git clone <repository-url>`
2. **Install Dependencies**: `pip install -e .[dev]`
3. **Setup Environment**: Copy `.env.example` to `.env`
4. **Run Services**: Start PostgreSQL, Redis, Qdrant
5. **Run Tests**: `pytest` to ensure everything works
6. **Start Development**: `rec-api serve start --reload`

***REMOVED******REMOVED******REMOVED*** Code Standards

- **Type Hints**: All functions must have type annotations
- **Documentation**: Docstrings for all public functions
- **Testing**: Minimum 80% test coverage
- **Formatting**: Use Black and isort for code formatting
- **Linting**: Pass flake8 and mypy checks

***REMOVED******REMOVED*** 📈 Performance

***REMOVED******REMOVED******REMOVED*** Optimization Strategies

- **Caching**: Multi-level caching (Redis, in-memory)
- **Connection Pooling**: Efficient database connections
- **Async Operations**: Non-blocking I/O for all external calls
- **Batch Processing**: Bulk operations for embeddings
- **Vector Indexing**: Optimized similarity search

***REMOVED******REMOVED******REMOVED*** Scalability

- **Horizontal Scaling**: Stateless application design
- **Microservices**: ML processing in separate service
- **Load Balancing**: Multiple API instances
- **Database Sharding**: Planned for large datasets

***REMOVED******REMOVED*** 🔮 Future Roadmap

***REMOVED******REMOVED******REMOVED*** Short Term

- [ ] User authentication and authorization
- [ ] A/B testing framework for algorithms
- [ ] Real-time recommendation updates
- [ ] Advanced caching strategies

***REMOVED******REMOVED******REMOVED*** Long Term

- [ ] Multi-modal recommendations (text, images, video)
- [ ] Real-time user behavior tracking
- [ ] Advanced personalization algorithms
- [ ] Recommendation explanation system

***REMOVED******REMOVED*** 📄 License

This project is part of the Next Watch platform. See the main repository for license information.

***REMOVED******REMOVED*** 🆘 Support

For questions, issues, or contributions:

1. **Documentation**: Check module-specific READMEs
2. **Issues**: Create GitHub issues for bugs
3. **Discussions**: Use GitHub discussions for questions
4. **Health Checks**: Use `/health` endpoints for diagnostics
