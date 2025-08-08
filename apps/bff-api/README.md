***REMOVED*** BFF API Service

Backend for Frontend (BFF) service for the Next Watch movie platform. This service acts as an aggregation layer between the Next.js frontend and various backend services, providing optimized data structures, intelligent caching, and smart warming for the UI.

***REMOVED******REMOVED*** 🎯 Purpose

The BFF aggregates data from multiple backend services and provides optimized endpoints for specific UI screens, reducing the complexity and number of API calls required by the frontend. It includes intelligent cache warming, performance monitoring, and comprehensive CLI tools for operations.

***REMOVED******REMOVED*** 🧱 Core Responsibilities

- ✅ **Data Aggregation**: Combine data from backend-api, auth-api, recommendation-api, search-api, and other services
- ✅ **Screen-Oriented Endpoints**: Provide UI-specific endpoints like `/bff/v1/home`, `/bff/v1/movies/{id}`, `/bff/v1/search`
- ✅ **User-Aware Logic**: Embed user-specific data (watchlist status, favorites, ratings, interactions)
- ✅ **Service Abstraction**: Hide backend service boundaries from the frontend
- ✅ **Intelligent Caching**: Optimize data delivery with domain-specific TTLs and smart warming
- ✅ **Performance Monitoring**: Comprehensive metrics and health checks
- ✅ **Smart Warming**: Event-driven cache warming based on user behavior

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Navigate to BFF directory
cd apps/bff-api

***REMOVED*** Set up Python environment with Hatch
hatch env create

***REMOVED*** Install local dependencies (movie-storage library)
./setup-local-deps.sh

***REMOVED*** Copy environment configuration
cp env.example .env

***REMOVED*** Start the service
hatch run serve
```

***REMOVED******REMOVED******REMOVED*** Using the CLI

The BFF API includes a comprehensive command-line interface for development and operations:

```bash
***REMOVED*** Show all available commands (inside Hatch environment)
hatch run cli --help

***REMOVED*** Start the development server
hatch run dev

***REMOVED*** Run tests
hatch run dev:test
```

***REMOVED******REMOVED*** 🛠️ CLI Commands

***REMOVED******REMOVED******REMOVED*** Server Management

```bash
***REMOVED*** Start the BFF server
hatch run serve [OPTIONS]

Options:
  --host TEXT          Host to bind server to [default: 0.0.0.0]
  --port INTEGER       Port to bind server to [default: 8001]
  --reload             Enable auto-reload for development
  --log-level TEXT     Set log level (DEBUG, INFO, WARNING, ERROR)
  --verbose, -v        Enable verbose logging and output
  --quiet, -q          Suppress console output except errors
```

***REMOVED******REMOVED******REMOVED*** Configuration Management

```bash
***REMOVED*** Display current configuration
hatch run config [OPTIONS]

Options:
  --show-secrets       Show sensitive configuration values (use with caution)
  --verbose, -v        Show detailed configuration information

***REMOVED*** Examples
hatch run config                    ***REMOVED*** Show masked configuration
hatch run config --verbose         ***REMOVED*** Show detailed configuration
hatch run config --show-secrets    ***REMOVED*** Show unmasked secrets (development only)
```

***REMOVED******REMOVED******REMOVED*** Health Checks

Comprehensive health checking for the BFF service and all dependencies:

```bash
***REMOVED*** Check all services
hatch run health check [OPTIONS]

Options:
  --backend-api-url TEXT    Backend API URL to check (overrides config)
  --auth-api-url TEXT       Auth API URL to check (overrides config)
  --timeout INTEGER         Request timeout in seconds [default: 5]
  --verbose, -v             Show detailed output

***REMOVED*** Check specific services
hatch run health backend [OPTIONS]    ***REMOVED*** Check Backend API only
hatch run health auth [OPTIONS]       ***REMOVED*** Check Auth API only

***REMOVED*** Examples
hatch run health check                 ***REMOVED*** Check all services
hatch run health check --verbose      ***REMOVED*** Detailed health check with response times
hatch run health backend --timeout 10 ***REMOVED*** Check backend with custom timeout
```

***REMOVED******REMOVED******REMOVED*** Cache Management

BFF-specific cache management with domain-aware operations:

```bash
***REMOVED*** Display BFF cache statistics
hatch run cache stats [OPTIONS]

Options:
  --verbose, -v         Show detailed cache statistics

***REMOVED*** Check cache health
hatch run cache health

***REMOVED*** Get cached movie data
hatch run cache get-movie MOVIE_ID

***REMOVED*** Get cached trending movies
hatch run cache get-trending [OPTIONS]

Options:
  --page, -p INTEGER    Page number to retrieve [default: 1]

***REMOVED*** Invalidate user cache
hatch run cache invalidate-user USER_ID [OPTIONS]

Options:
  --confirm             Skip confirmation prompt

***REMOVED*** Clear domain-specific cache
hatch run cache clear-domain DOMAIN [OPTIONS]

Arguments:
  DOMAIN                Domain to clear (movie, user, trending, search)

Options:
  --confirm             Skip confirmation prompt

***REMOVED*** Generic Redis cache operations
hatch run redis-cache info [OPTIONS]
hatch run redis-cache keys [OPTIONS]

Options:
  --pattern TEXT        Key pattern to match [default: *]
  --limit INTEGER       Maximum number of keys to display [default: 100]
  --verbose, -v         Show key details including TTL

***REMOVED*** Clear cache keys
hatch run cache clear [OPTIONS]

Options:
  --pattern TEXT        Key pattern to clear [default: *]
  --confirm/--no-confirm  Confirm before clearing cache [default: True]
  --verbose, -v         Show detailed output

***REMOVED*** Examples
hatch run cache info --verbose        ***REMOVED*** Detailed Redis statistics
hatch run cache keys --pattern "user:*" --limit 50  ***REMOVED*** List user-related keys
hatch run cache clear --pattern "temp:*" --no-confirm  ***REMOVED*** Clear temp keys without confirmation
```

***REMOVED******REMOVED******REMOVED*** Cache Warming

Intelligent cache warming based on user behavior and content popularity:

```bash
***REMOVED*** Warm popular content
hatch run cache warm popular [OPTIONS]

Options:
  --max-items INTEGER   Maximum items to warm [default: 100]
  --force               Force warming even if already cached
  --verbose, -v         Show detailed warming progress

***REMOVED*** Warm specific movie
hatch run cache warm movie MOVIE_ID [OPTIONS]

Options:
  --force               Force warming even if already cached
  --include-similar     Also warm similar movies

***REMOVED*** Warm user-specific content
hatch run cache warm user USER_ID [OPTIONS]

Options:
  --max-items INTEGER   Maximum items to warm [default: 50]
  --force               Force warming even if already cached

***REMOVED*** Examples
hatch run cache warm popular --max-items 200 --verbose  ***REMOVED*** Warm popular content with details
hatch run cache warm movie 123 --include-similar        ***REMOVED*** Warm movie and similar content
```

***REMOVED******REMOVED******REMOVED*** Version Information

```bash
***REMOVED*** Show version and environment information
hatch run version
```

***REMOVED******REMOVED*** 🔧 CLI Features

***REMOVED******REMOVED******REMOVED*** Rich Output

The CLI uses Rich for beautiful, informative output:

- **Color-coded status messages** (green for success, red for errors, yellow for warnings)
- **Progress indicators** for long-running operations
- **Formatted tables** for configuration and status information
- **Spinner animations** for async operations

***REMOVED******REMOVED******REMOVED*** Environment Integration

Commands automatically use environment variables and can be overridden:

```bash
***REMOVED*** Use environment variables
export BACKEND_API_URL=http://production-backend:8000
hatch run health check

***REMOVED*** Override with command-line options
hatch run health check --backend-api-url http://staging-backend:8000
```

***REMOVED******REMOVED******REMOVED*** Error Handling

Comprehensive error handling with:

- **Detailed error messages** with actionable information
- **Proper exit codes** for scripting and CI/CD integration
- **Logging integration** for debugging and monitoring
- **Graceful handling** of network timeouts and connection errors

***REMOVED******REMOVED******REMOVED*** Development Workflow

```bash
***REMOVED*** Development server with auto-reload and verbose logging
hatch run dev --reload --verbose --log-level DEBUG

***REMOVED*** Check all services are healthy before deployment
hatch run health check --verbose

***REMOVED*** Monitor cache performance
hatch run cache info --verbose

***REMOVED*** Clear development cache
hatch run cache clear --pattern "dev:*"
```

***REMOVED******REMOVED*** 📡 API Endpoints

***REMOVED******REMOVED******REMOVED*** Core Endpoints

```http
***REMOVED*** Movie Management
GET /bff/v1/movies                    ***REMOVED*** Movie catalog with filtering and pagination
GET /bff/v1/movies/{id}              ***REMOVED*** Movie details with cast/crew and recommendations
GET /bff/v1/movies/{id}/similar      ***REMOVED*** Similar movies suggestions

***REMOVED*** Search and Discovery
GET /bff/v1/search                   ***REMOVED*** Unified search across all services
GET /bff/v1/search/suggestions       ***REMOVED*** Search suggestions for typeahead
GET /bff/v1/search/suggestions/text  ***REMOVED*** Text-based search suggestions

***REMOVED*** User Interactions
GET /bff/v1/watchlist                ***REMOVED*** User's watchlist (aggregated)
GET /bff/v1/watched                  ***REMOVED*** User's watched movies
GET /bff/v1/liked                    ***REMOVED*** User's liked movies
POST /bff/v1/user-interactions       ***REMOVED*** Toggle user interactions (watchlist, like, etc.)

***REMOVED*** Content Discovery
GET /bff/v1/home                     ***REMOVED*** Home screen data aggregation
GET /bff/v1/sidebar                  ***REMOVED*** Sidebar widget data
GET /bff/v1/top                      ***REMOVED*** Top-rated content
GET /bff/v1/genres                   ***REMOVED*** Genre listings and content

***REMOVED*** Authentication
POST /bff/v1/auth/login              ***REMOVED*** User authentication
POST /bff/v1/auth/register           ***REMOVED*** User registration
GET /bff/v1/auth/profile             ***REMOVED*** User profile management

***REMOVED*** Actors and Cast
GET /bff/v1/actors                   ***REMOVED*** Actor listings
GET /bff/v1/actors/{id}              ***REMOVED*** Actor details with filmography
```

***REMOVED******REMOVED******REMOVED*** Health Endpoints

```http
GET /health/          ***REMOVED*** Basic health check
GET /health/ready     ***REMOVED*** Readiness check (K8s)
GET /health/live      ***REMOVED*** Liveness check (K8s)
```

***REMOVED******REMOVED*** 🧩 Integration Points

***REMOVED******REMOVED******REMOVED*** Backend Services

- **backend-api**: Primary source for movie metadata, genres, cast, user data
- **auth-api**: Authentication and user management
- **recommendation-api**: Movie recommendations and similar content
- **search-api**: Search functionality and suggestions
- **ml-api**: Machine learning features (optional)
- **Redis**: Caching layer for performance optimization

***REMOVED******REMOVED******REMOVED*** Fast-Core Integration

The BFF API is built on **fast-core** for standardized FastAPI patterns:

- **Service Client Factory**: Pre-configured HTTP clients for all backend services
- **Middleware Stack**: Automatic logging, CORS, security, and error handling
- **Health Checks**: Comprehensive monitoring of external dependencies
- **Configuration Management**: Environment-aware configuration with validation
- **Error Handling**: Consistent error responses across all endpoints

***REMOVED******REMOVED******REMOVED*** Cache Integration

The BFF API uses the **NextWatch Cache Library** for intelligent caching:

- **Domain-specific TTLs**: Different cache durations for movies (30 days static, 5 min user data), users (30min), popular content (15min)
- **Structured keys**: Organized cache keys like `bff:movie:details:123`, `bff:user:watchlist:456`
- **Smart Warming**: Event-driven cache warming based on user behavior and content popularity
- **Health monitoring**: Cache health checks integrated into service monitoring
- **CLI management**: Rich CLI commands for cache inspection and management
- **Graceful fallback**: Cache failures don't break the API, just reduce performance

***REMOVED******REMOVED******REMOVED*** Smart Warming System

The BFF includes an intelligent cache warming system:

- **Event-driven warming**: Automatically warms content based on user interactions
- **Priority-based warming**: Different warming strategies for popular, new, and trending content
- **Version-aware warming**: Respects content versions to avoid stale data
- **Throttled operations**: Prevents backend overload during warming operations
- **Background processing**: Non-blocking warming operations

***REMOVED******REMOVED*** 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   BFF Service   │────│  Backend API    │
│                 │    │                 │    │                 │
│ - Home Screen   │    │ - Data Agg.     │    │ - Movie Data    │
│ - Movie Detail  │    │ - User Context  │    │ - User Data     │
│ - Search        │    │ - Smart Warming │    │ - Business Logic│
│ - User Profile  │    │ - Caching       │    │ - Auth          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │   Auth API      │
                       │   (Caching)     │    │ (Authentication)│
                       │ + Smart Warming │    └─────────────────┘
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │ Recommendation  │
                       │     API         │
                       └─────────────────┘
```

***REMOVED******REMOVED*** 🔧 Configuration

Environment variables:

```bash
***REMOVED*** Server Configuration
HOST=0.0.0.0
PORT=8001
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
LOGS_DIR=logs

***REMOVED*** Backend Integration
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TIMEOUT=30
AUTH_API_URL=http://localhost:8003
AUTH_API_TIMEOUT=10
RECO_API_URL=http://localhost:8002
RECO_API_TIMEOUT=30
SEARCH_API_URL=http://localhost:8005
SEARCH_API_TIMEOUT=15
ML_API_URL=http://localhost:8006
ML_API_TIMEOUT=60

***REMOVED*** Service-to-Service Authentication
INTERNAL_API_KEY=bff-to-backend-secret-key-change-in-production
ADMIN_API_KEY=admin-secret-key-change-in-production

***REMOVED*** Caching
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

***REMOVED*** Cache Library Settings
CACHE_KEY_PREFIX=bff:
CACHE_REDIS_POOL_SIZE=10
CACHE_REDIS_TIMEOUT=5
CACHE_ENABLE_METRICS=true

***REMOVED*** Domain-specific Cache TTLs
CACHE_MOVIE_TTL=600        ***REMOVED*** 10 minutes for movie data
CACHE_USER_TTL=1800        ***REMOVED*** 30 minutes for user sessions
CACHE_POPULAR_TTL=900      ***REMOVED*** 15 minutes for popular content
CACHE_DEFAULT_TTL=300      ***REMOVED*** 5 minutes default

***REMOVED*** Smart Warming Configuration
WARMING_MAX_CONCURRENT=3
WARMING_REQUESTS_PER_SECOND=2
WARMING_MAX_CONNECTIONS=4
WARMING_OPERATION_TIMEOUT=120
WARMING_REQUEST_TIMEOUT=3
WARMING_BURST_SIZE=5
WARMING_MAX_ITEMS_PER_STRATEGY=10000

***REMOVED*** Security
JWT_SECRET=your-jwt-secret-here-change-in-production

***REMOVED*** CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8001

***REMOVED*** Performance Monitoring
ENABLE_PERFORMANCE_METRICS=true
```

***REMOVED******REMOVED*** 🧪 Testing

```bash
***REMOVED*** Run all tests
hatch run dev:test

***REMOVED*** Run with coverage
hatch run dev:test-cov

***REMOVED*** Run specific test file
hatch run dev:test-file tests/test_routes.py

***REMOVED*** Run with verbose output
hatch run dev:test -v
```

***REMOVED******REMOVED*** 🔧 Development

***REMOVED******REMOVED******REMOVED*** Code Style

The project follows Google Python Style Guide:

```bash
***REMOVED*** Format code
hatch run dev:format

***REMOVED*** Sort imports
hatch run dev:isort

***REMOVED*** Lint code
hatch run dev:lint

***REMOVED*** Type checking
hatch run dev:mypy
```

***REMOVED******REMOVED******REMOVED*** Project Structure

```
apps/bff-api/
├── src/bff_api/
│   ├── config/              ***REMOVED*** Configuration management
│   │   ├── app.py          ***REMOVED*** BFF-specific configuration
│   │   └── fast_core_config.py  ***REMOVED*** Fast-core integration
│   ├── core/               ***REMOVED*** Core application components
│   │   ├── app_fast_core.py  ***REMOVED*** Fast-core application factory
│   │   └── metrics.py      ***REMOVED*** Performance metrics
│   ├── routes/             ***REMOVED*** FastAPI route handlers
│   │   ├── api_v1.py       ***REMOVED*** v1 API router
│   │   ├── health.py       ***REMOVED*** Health check endpoints
│   │   ├── v1/             ***REMOVED*** v1 API endpoints
│   │   │   ├── movies.py   ***REMOVED*** Movie-related endpoints
│   │   │   ├── search.py   ***REMOVED*** Search endpoints
│   │   │   ├── auth.py     ***REMOVED*** Authentication endpoints
│   │   │   ├── home.py     ***REMOVED*** Home screen endpoints
│   │   │   └── ...         ***REMOVED*** Other endpoint modules
│   │   └── admin/          ***REMOVED*** Admin endpoints (secured)
│   ├── services/           ***REMOVED*** External service clients
│   │   ├── clients/        ***REMOVED*** Service clients
│   │   │   ├── base.py     ***REMOVED*** Base client class
│   │   │   ├── movies.py   ***REMOVED*** Movie service client
│   │   │   ├── search.py   ***REMOVED*** Search service client
│   │   │   └── ...         ***REMOVED*** Other service clients
│   │   ├── smart_warming.py  ***REMOVED*** Intelligent cache warming
│   │   └── health_service.py ***REMOVED*** Health check service
│   ├── schemas/            ***REMOVED*** Pydantic schemas
│   │   ├── screen_schemas.py    ***REMOVED*** Screen data schemas
│   │   ├── auth_schemas.py      ***REMOVED*** Authentication schemas
│   │   └── user_interaction_schemas.py  ***REMOVED*** User interaction schemas
│   ├── dependencies/       ***REMOVED*** FastAPI dependencies
│   ├── utils/              ***REMOVED*** Utility functions
│   ├── cli/                ***REMOVED*** Command-line interface
│   │   ├── commands/       ***REMOVED*** Modular CLI commands
│   │   ├── utils.py        ***REMOVED*** CLI utilities
│   │   └── main.py         ***REMOVED*** Main CLI app
│   └── main.py             ***REMOVED*** FastAPI application
├── tests/                  ***REMOVED*** Test suite
├── pyproject.toml          ***REMOVED*** Dependencies and config
└── README.md              ***REMOVED*** This file
```

***REMOVED******REMOVED*** 🚀 Deployment

***REMOVED******REMOVED******REMOVED*** Docker

The service can be built and run using Docker with a pure pip-based approach:

```bash
***REMOVED*** Build the optimized Docker image
docker build -f apps/bff-api/Dockerfile -t next-watch-bff .

***REMOVED*** Run the container
docker run -p 8001:8001 \
  -e BACKEND_API_URL=http://localhost:8000 \
  -e REDIS_URL=redis://localhost:6379 \
  -e JWT_SECRET=your-secret-key \
  next-watch-bff

***REMOVED*** Or run in background
docker run -d -p 8001:8001 \
  -e BACKEND_API_URL=http://localhost:8000 \
  -e REDIS_URL=redis://localhost:6379 \
  -e JWT_SECRET=your-secret-key \
  --name bff-api \
  next-watch-bff
```

The Docker build uses:

- **Alpine Linux** for minimal image size (~80-120MB)
- **Multi-stage build** to exclude build dependencies from final image
- **requirements.txt** instead of Poetry for faster, simpler builds
- **Non-root user** for security
- **Health checks** for container orchestration

***REMOVED******REMOVED******REMOVED******REMOVED*** Updating Dependencies

When you add new dependencies to `pyproject.toml`, regenerate `requirements.txt`:

```bash
***REMOVED*** Navigate to BFF directory
cd apps/bff-api

***REMOVED*** Install poetry export plugin if not already installed
poetry self add poetry-plugin-export

***REMOVED*** Export dependencies to requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes

***REMOVED*** Rebuild Docker image
docker build -f Dockerfile -t next-watch-bff .
```

***REMOVED******REMOVED******REMOVED*** Environment Variables

Ensure these are set in production:

- `ENVIRONMENT=production`
- `JWT_SECRET` (secure random string)
- `BACKEND_API_URL` (production backend URL)
- `AUTH_API_URL` (production auth service URL)
- `REDIS_URL` (production Redis instance)
- `INTERNAL_API_KEY` (secure service-to-service key)
- `ADMIN_API_KEY` (secure admin endpoint key)

***REMOVED******REMOVED*** 📊 Monitoring

The BFF service provides several monitoring endpoints:

- Health checks for load balancer integration
- Structured logging for observability
- Request/response timing middleware
- Error tracking and reporting
- CLI tools for operational monitoring
- Performance metrics collection
- Cache warming statistics

***REMOVED******REMOVED*** 🤝 Contributing

1. Follow TDD practices - write tests first
2. Use type hints for all functions
3. Add docstrings following Google style
4. Update README for any API changes
5. Ensure all tests pass before submitting
6. Test CLI commands thoroughly
7. Follow fast-core patterns for new endpoints
8. Implement proper error handling with fast-core exceptions

***REMOVED******REMOVED*** 📝 License

This project is part of the Next Watch movie platform.

---
