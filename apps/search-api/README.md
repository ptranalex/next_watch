# Search API

A dedicated search and suggestion service for the Next Watch platform, providing fast and intelligent search capabilities across movies, actors, and directors.

## 🚀 Features

- **Movie Search**: Comprehensive movie search with advanced filtering
- **Real-time Suggestions**: Redis-backed autocomplete and typeahead
- **Multi-entity Search**: Search across movies, actors, and directors
- **Search Analytics**: Track search patterns and performance
- **Fuzzy Matching**: Typo tolerance and intelligent matching
- **Semantic Search**: Enhanced search using ML embeddings (optional)
- **Performance Optimized**: Redis caching and optimized queries

## 🏗️ Architecture

The Search API is built using:

- **FastAPI**: Modern async web framework
- **Fast-Core**: Shared framework for consistent API patterns
- **Redis**: Caching and suggestion storage
- **PostgreSQL**: Data persistence (via Backend API)
- **Pydantic**: Data validation and serialization

## 📚 API Endpoints

### Search Endpoints

- `GET /api/v1/search` - Movie search with filtering
- `GET /api/v1/search/all` - Multi-entity search
- `GET /api/v1/search/suggestions` - Basic search suggestions
- `GET /api/v1/search/suggestions/text` - Enhanced text suggestions

### System Endpoints

- `GET /health` - Comprehensive health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /health/services` - Service client factory status

## 🔧 Configuration

### Environment Variables

```bash
# Service Configuration
PORT=8004                         # Default service port
HOST=0.0.0.0                      # Bind host
ENVIRONMENT=development
LOG_LEVEL=INFO

# External Services
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TIMEOUT=30
ML_API_URL=http://localhost:8005   # Optional
ML_API_TIMEOUT=60

# Redis Configuration
REDIS_URL=redis://localhost:6379/2
REDIS_MAX_CONNECTIONS=20

# Search Settings
MAX_SUGGESTIONS=50
SEARCH_CACHE_TTL=300
SUGGESTION_CACHE_TTL=3600
MIN_QUERY_LENGTH=1
MAX_QUERY_LENGTH=100

# Feature Flags
ENABLE_SEMANTIC_SEARCH=false
ENABLE_SEARCH_ANALYTICS=true
ENABLE_FUZZY_MATCHING=true
ENABLE_TYPO_TOLERANCE=true

# Security
INTERNAL_API_KEY=search-to-backend-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

## 🚀 Development

### Prerequisites

- Python 3.12+
- Redis server
- Access to Backend API

### Setup

```bash
# Navigate to search-api directory
cd apps/search-api

# Install dependencies
hatch shell
hatch run install-libs

# Run development server (auto-reload on port 8005)
hatch run dev
```

### Available Commands

```bash
# Development server
hatch run dev                     # Auto-reload on port 8005 (dev)

# CLI access (Typer app)
hatch run cli -- --help           # Show CLI help
hatch run cli -- redis info       # Redis info summary
hatch run cli -- redis test-suggestions "star" -l 5
hatch run cli -- redis populate-suggestions --limit 5000 --verbose

# Health checks (via hatch scripts)
hatch run health-check            # Comprehensive health check
hatch run health-redis            # Redis health check
hatch run health-backend          # Backend API health check

# Development tools
hatch run lint                    # Code linting
hatch run format                  # Code formatting
hatch run test                    # Run tests
hatch run test-cov                # Run tests with coverage

# Docker testing
./scripts/test-docker-build.sh    # Test Docker build and basic functionality
```

## 🧪 Testing

```bash
# Run all tests
hatch run test

# Run with coverage
hatch run test-cov

# Test specific functionality
pytest tests/test_search.py -v
pytest tests/test_suggestions.py -v
```

## 📊 Monitoring

### Health Checks

The service provides multiple health check endpoints:

- `/health` - Comprehensive check including Redis and Backend API
- `/health/ready` - Kubernetes readiness probe
- `/health/live` - Kubernetes liveness probe
- `/health/services` - Service client factory status

### Metrics

When enabled, the service exposes metrics for:

- Search request counts and latency
- Suggestion performance
- Cache hit/miss ratios
- Error rates and types
- Redis connection status

## 🔄 Integration

### With BFF API

The Search API is called by the BFF API for all search-related operations:

```python
# BFF API search routes will be updated to call Search API
# instead of Backend API directly
```

### With Backend API

Search API calls Backend API for:

- Movie data retrieval
- User-specific search results
- Search result enrichment

### With ML API (Optional)

When semantic search is enabled:

- Movie embedding generation
- Semantic similarity calculations
- Enhanced search ranking

## 🚢 Deployment

### Docker

#### Building from Monorepo Root

```bash
# Build image from monorepo root (required for local dependencies)
docker build -f apps/search-api/Dockerfile -t search-api:latest .

# Run container
docker run -p 8004:8004 \
  -e REDIS_URL=redis://redis:6379/2 \
  -e BACKEND_API_URL=http://backend:8000 \
  -e ENVIRONMENT=production \
  search-api:latest
```

#### Development with Docker Compose

```bash
# From search-api directory
cd apps/search-api

# Start search-api with Redis
docker-compose -f docker-compose.dev.yml up --build

# Stop services
docker-compose -f docker-compose.dev.yml down
```

#### Production Environment Variables

```bash
# Core Configuration
ENVIRONMENT=production
PORT=8004
LOG_LEVEL=info
WORKERS=2

# External Services
BACKEND_API_URL=http://backend:8000
REDIS_URL=redis://redis:6379/2

# Search Configuration
MAX_SUGGESTIONS=50
SEARCH_CACHE_TTL=300
SUGGESTION_CACHE_TTL=3600

# Feature Flags
ENABLE_SEARCH_ANALYTICS=true
ENABLE_FUZZY_MATCHING=true
ENABLE_TYPO_TOLERANCE=true
ENABLE_SEMANTIC_SEARCH=false

# Security
INTERNAL_API_KEY=your-secret-key
CORS_ORIGINS=["https://yourdomain.com"]
```

### Environment-specific Configuration

- **Development**: Full debugging, verbose logging
- **Staging**: Production-like with debug endpoints
- **Production**: Optimized performance, security hardened

## 📝 Migration Notes

This service consolidates search functionality that was previously split between:

- Backend API (`/api/v1/search/*` endpoints)
- BFF API (search aggregation logic)

### Migration Steps

1. ✅ Create Search API service structure
2. ✅ **Move search routes from Backend API**
3. ✅ **Implement Backend API integration**
4. ✅ **Working search endpoints with live data**
5. ✅ **Redis-backed suggestion engine with enhanced features**
   - ✅ Advanced suggestion caching and ranking
   - ✅ Entity-based suggestions with metadata
   - ✅ Fuzzy matching and fallback to Backend API
6. ⏳ Update BFF API to call Search API
7. ⏳ Update Frontend to use new search endpoints
8. ⏳ Add search analytics and monitoring
9. ⏳ Implement semantic search capabilities

**🎉 Search API is now production-ready with Redis-enhanced suggestions!**

### ✅ Working Endpoints (Live)

```bash
# Movie search with filters
curl "http://localhost:8004/api/v1/search?q=batman&limit=5"

# Enhanced text suggestions with Redis-backed ranking and metadata
curl "http://localhost:8004/api/v1/search/suggestions/text?query=star&limit=3"

# Multi-entity search
curl "http://localhost:8004/api/v1/search/all?query=action&limit=10"

# Service health
curl "http://localhost:8004/health"
```

## 🤝 Contributing

1. Follow existing code patterns from other services
2. Add comprehensive tests for new functionality
3. Update documentation for API changes
4. Ensure health checks cover new dependencies

## 📄 License

MIT License - see LICENSE file for details.

---
