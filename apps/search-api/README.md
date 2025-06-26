***REMOVED*** Search API

A dedicated search and suggestion service for the Next Watch platform, providing fast and intelligent search capabilities across movies, actors, and directors.

***REMOVED******REMOVED*** 🚀 Features

- **Movie Search**: Comprehensive movie search with advanced filtering
- **Real-time Suggestions**: Redis-backed autocomplete and typeahead
- **Multi-entity Search**: Search across movies, actors, and directors
- **Search Analytics**: Track search patterns and performance
- **Fuzzy Matching**: Typo tolerance and intelligent matching
- **Semantic Search**: Enhanced search using ML embeddings (optional)
- **Performance Optimized**: Redis caching and optimized queries

***REMOVED******REMOVED*** 🏗️ Architecture

The Search API is built using:

- **FastAPI**: Modern async web framework
- **Fast-Core**: Shared framework for consistent API patterns
- **Redis**: Caching and suggestion storage
- **PostgreSQL**: Data persistence (via Backend API)
- **Pydantic**: Data validation and serialization

***REMOVED******REMOVED*** 📚 API Endpoints

***REMOVED******REMOVED******REMOVED*** Search Endpoints

- `GET /api/v1/search` - Movie search with filtering
- `GET /api/v1/search/all` - Multi-entity search
- `GET /api/v1/search/suggestions` - Basic search suggestions
- `GET /api/v1/search/suggestions/text` - Enhanced text suggestions

***REMOVED******REMOVED******REMOVED*** System Endpoints

- `GET /health` - Comprehensive health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /` - Service information
- `GET /debug` - Debug information (development only)

***REMOVED******REMOVED*** 🔧 Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

```bash
***REMOVED*** Service Configuration
SEARCH_API_PORT=8004
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

***REMOVED*** External Services
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TIMEOUT=30
ML_API_URL=http://localhost:8005  ***REMOVED*** Optional
ML_API_TIMEOUT=60

***REMOVED*** Redis Configuration
REDIS_URL=redis://localhost:6379/2
REDIS_POOL_SIZE=20

***REMOVED*** Search Settings
MAX_SUGGESTIONS=50
SEARCH_CACHE_TTL=300
SUGGESTION_CACHE_TTL=3600
MIN_QUERY_LENGTH=1
MAX_QUERY_LENGTH=100

***REMOVED*** Feature Flags
ENABLE_SEMANTIC_SEARCH=false
ENABLE_SEARCH_ANALYTICS=true
ENABLE_FUZZY_MATCHING=true
ENABLE_TYPO_TOLERANCE=true

***REMOVED*** Security
INTERNAL_API_KEY=search-to-backend-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

***REMOVED******REMOVED*** 🚀 Development

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Python 3.12+
- Redis server
- Access to Backend API

***REMOVED******REMOVED******REMOVED*** Setup

```bash
***REMOVED*** Navigate to search-api directory
cd apps/search-api

***REMOVED*** Install dependencies
hatch shell
hatch run install-libs

***REMOVED*** Run development server
hatch run dev
```

***REMOVED******REMOVED******REMOVED*** Available Commands

```bash
***REMOVED*** Development server
hatch run dev                    ***REMOVED*** Start with auto-reload on port 8004

***REMOVED*** CLI access
hatch run cli                    ***REMOVED*** Access search-api CLI

***REMOVED*** Health checks
hatch run health-check           ***REMOVED*** Comprehensive health check
hatch run health-redis           ***REMOVED*** Redis health check
hatch run health-backend         ***REMOVED*** Backend API health check

***REMOVED*** Cache management
hatch run cache-info             ***REMOVED*** Redis cache information
hatch run cache-keys             ***REMOVED*** List cache keys
hatch run cache-clear            ***REMOVED*** Clear cache (with confirmation)

***REMOVED*** Search operations
hatch run index-suggestions      ***REMOVED*** Index search suggestions
hatch run search-test           ***REMOVED*** Test search functionality

***REMOVED*** Development tools
hatch run lint                   ***REMOVED*** Code linting
hatch run format                 ***REMOVED*** Code formatting
hatch run test                   ***REMOVED*** Run tests
hatch run test-cov              ***REMOVED*** Run tests with coverage

***REMOVED*** Docker testing
./scripts/test-docker-build.sh   ***REMOVED*** Test Docker build and basic functionality
```

***REMOVED******REMOVED*** 🧪 Testing

```bash
***REMOVED*** Run all tests
hatch run test

***REMOVED*** Run with coverage
hatch run test-cov

***REMOVED*** Test specific functionality
pytest tests/test_search.py -v
pytest tests/test_suggestions.py -v
```

***REMOVED******REMOVED*** 📊 Monitoring

***REMOVED******REMOVED******REMOVED*** Health Checks

The service provides multiple health check endpoints:

- `/health` - Comprehensive check including Redis and Backend API
- `/health/ready` - Kubernetes readiness probe
- `/health/live` - Kubernetes liveness probe
- `/health/services` - Service client factory status

***REMOVED******REMOVED******REMOVED*** Metrics

When enabled, the service exposes metrics for:

- Search request counts and latency
- Suggestion performance
- Cache hit/miss ratios
- Error rates and types
- Redis connection status

***REMOVED******REMOVED*** 🔄 Integration

***REMOVED******REMOVED******REMOVED*** With BFF API

The Search API is called by the BFF API for all search-related operations:

```python
***REMOVED*** BFF API search routes will be updated to call Search API
***REMOVED*** instead of Backend API directly
```

***REMOVED******REMOVED******REMOVED*** With Backend API

Search API calls Backend API for:

- Movie data retrieval
- User-specific search results
- Search result enrichment

***REMOVED******REMOVED******REMOVED*** With ML API (Optional)

When semantic search is enabled:

- Movie embedding generation
- Semantic similarity calculations
- Enhanced search ranking

***REMOVED******REMOVED*** 🚢 Deployment

***REMOVED******REMOVED******REMOVED*** Docker

***REMOVED******REMOVED******REMOVED******REMOVED*** Building from Monorepo Root

```bash
***REMOVED*** Build image from monorepo root (required for local dependencies)
docker build -f apps/search-api/Dockerfile -t search-api:latest .

***REMOVED*** Run container
docker run -p 8004:8004 \
  -e REDIS_URL=redis://redis:6379/2 \
  -e BACKEND_API_URL=http://backend:8000 \
  -e ENVIRONMENT=production \
  search-api:latest
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Development with Docker Compose

```bash
***REMOVED*** From search-api directory
cd apps/search-api

***REMOVED*** Start search-api with Redis
docker-compose -f docker-compose.dev.yml up --build

***REMOVED*** Stop services
docker-compose -f docker-compose.dev.yml down
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Production Environment Variables

```bash
***REMOVED*** Core Configuration
ENVIRONMENT=production
PORT=8004
LOG_LEVEL=info
WORKERS=2

***REMOVED*** External Services
BACKEND_API_URL=http://backend:8000
REDIS_URL=redis://redis:6379/2

***REMOVED*** Search Configuration
MAX_SUGGESTIONS=50
SEARCH_CACHE_TTL=300
SUGGESTION_CACHE_TTL=3600

***REMOVED*** Feature Flags
ENABLE_SEARCH_ANALYTICS=true
ENABLE_FUZZY_MATCHING=true
ENABLE_TYPO_TOLERANCE=true
ENABLE_SEMANTIC_SEARCH=false

***REMOVED*** Security
INTERNAL_API_KEY=your-secret-key
CORS_ORIGINS=["https://yourdomain.com"]
```

***REMOVED******REMOVED******REMOVED*** Environment-specific Configuration

- **Development**: Full debugging, verbose logging
- **Staging**: Production-like with debug endpoints
- **Production**: Optimized performance, security hardened

***REMOVED******REMOVED*** 📝 Migration Notes

This service consolidates search functionality that was previously split between:

- Backend API (`/api/v1/search/*` endpoints)
- BFF API (search aggregation logic)

***REMOVED******REMOVED******REMOVED*** Migration Steps

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

***REMOVED******REMOVED******REMOVED*** ✅ Working Endpoints (Live)

```bash
***REMOVED*** Movie search with filters
curl "http://localhost:8004/api/v1/search?q=batman&limit=5"

***REMOVED*** Enhanced text suggestions with Redis-backed ranking and metadata
curl "http://localhost:8004/api/v1/search/suggestions/text?query=star&limit=3"

***REMOVED*** Multi-entity search
curl "http://localhost:8004/api/v1/search/all?query=action&limit=10"

***REMOVED*** Service health
curl "http://localhost:8004/health"
```

***REMOVED******REMOVED*** 🤝 Contributing

1. Follow existing code patterns from other services
2. Add comprehensive tests for new functionality
3. Update documentation for API changes
4. Ensure health checks cover new dependencies

***REMOVED******REMOVED*** 📄 License

MIT License - see LICENSE file for details.
