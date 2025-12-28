***REMOVED*** Next Watch

A comprehensive movie discovery and tracking platform built with modern microservices architecture.

***REMOVED******REMOVED*** 🏗️ Architecture

Next Watch is a microservices-based platform with 8 main services:

```text
┌──────────────┐
│   Frontend   │ (Next.js - Port 3000)
│  (Next.js)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   BFF API    │────▶│  Auth API    │     │ Backend API  │     │  Search API  │
│  (Port 8001) │     │ (Port 8003)  │     │ (Port 8000)  │     │ (Port 8005)  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                     │                     │
       │                    │                     │                     │
       ▼                    ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│Recommendation│────▶│    ML API    │     │  PostgreSQL  │     │    Redis     │
│     API      │     │ (Port 8004)  │     │ (Port 5432)  │     │ (Port 6379)  │
│ (Port 8002)  │     └──────────────┘     └──────────────┘     └──────────────┘
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   Qdrant     │     │Data Importer │
│ (Port 6333)  │     │ (On-demand)  │
└──────────────┘     └──────────────┘
```

***REMOVED******REMOVED******REMOVED*** Core Services

- **Frontend** (`apps/web-nextjs`): Next.js 15 web application with modern UI/UX
- **BFF API** (`apps/bff-api`): Backend for Frontend - aggregation and orchestration layer
- **Auth API** (`apps/auth-api`): Dedicated JWT-based authentication and authorization service
- **Backend API** (`apps/backend-api`): Core business logic, movie data access, and database operations
- **Recommendation API** (`apps/recommendation-api`): Movie recommendations using vector similarity and collaborative filtering
- **ML API** (`apps/ml-api`): Machine learning service for generating movie and user embeddings
- **Search API** (`apps/search-api`): Dedicated search service with Redis-powered autocomplete and suggestions
- **Data Importer** (`apps/data-importer`): Movie data synchronization from TMDB and OMDB

***REMOVED******REMOVED******REMOVED*** Infrastructure & Storage

- **PostgreSQL**: Primary database for movie metadata, users, and relational data
- **Redis**: Caching layer and search suggestion storage
- **Qdrant**: Vector database for similarity-based movie recommendations

***REMOVED******REMOVED******REMOVED*** Shared Libraries

- **Fast-Core** (`libs/fast-core`): Standardized FastAPI middleware, configuration, and monitoring framework
  - Consistent middleware stack (CORS, security headers, rate limiting, logging, metrics)
  - OpenTelemetry integration for distributed tracing
  - Health check framework with liveness/readiness/deep probes
  - JWT utilities and authentication helpers
  - Error handling and service error contexts
- **Cache** (`libs/cache`): Redis caching utilities with warming and invalidation patterns
  - Cache warming strategies
  - TTL management
  - Key versioning and invalidation
  - Metrics and monitoring
- **Config** (`libs/config`): Centralized configuration management with environment profiles
  - Environment-based configuration
  - Logging setup with themes
  - Security configuration
  - Service discovery settings
- **CLI** (`libs/cli`): Shared command-line interface utilities for service management
  - Service registry pattern
  - Output handling and formatting
  - Common command patterns

***REMOVED******REMOVED*** 🛠️ Technology Stack

***REMOVED******REMOVED******REMOVED*** Backend Services (Python)

- **Framework**: FastAPI with fast-core standardization
- **Language**: Python 3.12+
- **Package Management**: Hatch
- **ORM**: SQLAlchemy with asyncpg
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Code Quality**: mypy, ruff, black, isort

***REMOVED******REMOVED******REMOVED*** Frontend (TypeScript)

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Package Management**: pnpm
- **UI Library**: Material-UI (MUI)
- **State Management**: React Context + Zustand
- **Styling**: Emotion CSS-in-JS

***REMOVED******REMOVED******REMOVED*** Machine Learning

- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Search**: Qdrant vector database
- **Dimensions**: 384-dimensional embeddings
- **Distance Metric**: Cosine similarity

***REMOVED******REMOVED******REMOVED*** Infrastructure

- **Database**: PostgreSQL 14+
- **Cache**: Redis 7+
- **Vector DB**: Qdrant
- **Reverse Proxy**: Nginx
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Docker Compose (production), Hatch (development)

***REMOVED******REMOVED******REMOVED*** Observability

- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Tracing**: OpenTelemetry + Grafana Alloy
- **Logging**: Structured JSON logs with coloredlogs (development)
- **Alerts**: AlertManager

***REMOVED******REMOVED*** 🚀 Quick Start

New to the repo? Start here:

- `docs/getting-started/ONBOARDING.md` (recommended local development path)

***REMOVED******REMOVED******REMOVED*** Production-like stack (Docker Compose)

Note: `infra/compose/prod.yml` expects PostgreSQL and Redis to be reachable on the host (`host.docker.internal`).

```bash
***REMOVED*** Clone the repository
git clone https://github.com/your-username/next_watch.git
cd next_watch

***REMOVED*** Copy environment template
cp infra/env/prod.example .env.prod

***REMOVED*** Edit environment variables
nano .env.prod

***REMOVED*** Build all services
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest .
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest .
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest .
docker build -f apps/recommendation-api/Dockerfile -t next-watch-recommendation:latest .
docker build -f apps/ml-api/Dockerfile -t next-watch-ml:latest .
docker build -f apps/search-api/Dockerfile -t next-watch-search:latest .
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest .
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest .

***REMOVED*** Start services
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d

***REMOVED*** Check status
docker ps
```

***REMOVED******REMOVED******REMOVED*** Using the Deployment Script

```bash
***REMOVED*** Make executable
chmod +x scripts/deploy-prod.sh

***REMOVED*** Deploy all services
./scripts/deploy-prod.sh

***REMOVED*** Deploy with data import
./scripts/deploy-prod.sh --import

***REMOVED*** Build only (no deployment)
./scripts/deploy-prod.sh --build-only
```

***REMOVED******REMOVED*** 🔧 Configuration

***REMOVED******REMOVED******REMOVED*** Required Environment Variables

```bash
***REMOVED*** Docker Images
DOCKER_BACKEND_IMAGE=next-watch-backend:latest
DOCKER_AUTH_IMAGE=next-watch-auth:latest
DOCKER_BFF_IMAGE=next-watch-bff:latest
DOCKER_RECOMMENDATION_IMAGE=next-watch-recommendation:latest
DOCKER_ML_IMAGE=next-watch-ml:latest
DOCKER_SEARCH_IMAGE=next-watch-search:latest
DOCKER_FRONTEND_IMAGE=next-watch-frontend:latest
DOCKER_IMPORTER_IMAGE=next-watch-importer:latest

***REMOVED*** Database
POSTGRES_USER=next_watch_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=next_watch

***REMOVED*** Security
JWT_SECRET=your-super-secure-jwt-secret
INTERNAL_API_KEY=your-internal-api-key

***REMOVED*** External APIs
TMDB_ACCESS_TOKEN=your-tmdb-token
OMDB_API_KEY=your-omdb-key

***REMOVED*** Service URLs (for inter-service communication)
BACKEND_API_URL=http://backend-api:8000
ML_API_URL=http://ml-api:8000
RECOMMENDATION_API_URL=http://recommendation-api:8000
SEARCH_API_URL=http://search-api:8000
```

See `infra/env/prod.example` for complete configuration options.

***REMOVED******REMOVED*** 🔄 CI/CD Workflows

***REMOVED******REMOVED******REMOVED*** GitHub Actions

The project includes comprehensive GitHub Actions workflows:

***REMOVED******REMOVED******REMOVED******REMOVED*** **Build Workflow** (`.github/workflows/build.yml`)

- Builds all 8 services when their code changes
- Supports building shared libraries (`libs/fast-core`, `libs/cache`, `libs/config`, `libs/cli`)
- Pushes images to GitHub Container Registry
- Supports manual builds with `build_all` option

***REMOVED******REMOVED******REMOVED******REMOVED*** **Deploy Workflow** (`.github/workflows/deploy.yml`)

- Deploys services to production server
- Uses Docker Compose with proper environment configuration
- Supports selective deployment of individual services
- Includes health checks and cleanup

***REMOVED******REMOVED******REMOVED******REMOVED*** **Release Workflow** (`.github/workflows/release.yml`)

- Automatically builds and deploys on `main` branch pushes
- Detects changes in each service
- Orchestrates build → deploy pipeline
- Supports manual releases with custom service selection

***REMOVED******REMOVED******REMOVED*** Workflow Triggers

**Automatic (on push to main):**

- Detects changes in each service directory
- Builds only changed services
- Deploys changed services automatically

**Manual (workflow_dispatch):**

- Build all services regardless of changes
- Deploy specific services
- Full stack deployment

***REMOVED******REMOVED******REMOVED*** Required Secrets

Configure these in your GitHub repository settings:

```bash
***REMOVED*** Deployment
DEPLOY_KEY          ***REMOVED*** SSH private key for server access
DEPLOY_HOST         ***REMOVED*** Server hostname/IP
DEPLOY_USER         ***REMOVED*** SSH username
GH_PAT             ***REMOVED*** GitHub Personal Access Token

***REMOVED*** Database
POSTGRES_USER       ***REMOVED*** Database username
POSTGRES_PASSWORD   ***REMOVED*** Database password
POSTGRES_DB         ***REMOVED*** Database name

***REMOVED*** Security
JWT_SECRET          ***REMOVED*** JWT signing secret
INTERNAL_API_KEY    ***REMOVED*** Service-to-service API key

***REMOVED*** External APIs (optional)
TMDB_ACCESS_TOKEN   ***REMOVED*** The Movie Database API token
OMDB_API_KEY        ***REMOVED*** Open Movie Database API key
```

***REMOVED******REMOVED*** 📊 Monitoring & Health Checks

***REMOVED******REMOVED******REMOVED*** Production Monitoring Stack

Deploy comprehensive monitoring to your AWS infrastructure:

```bash
***REMOVED*** One-click monitoring deployment to existing AWS instance
cd infra/aws
./deploy-monitoring-one-click.sh
```

This deploys:

- **Prometheus**: Metrics collection from all NextWatch services
- **Grafana**: Dashboards and visualization
- **Grafana Alloy**: OpenTelemetry collector for distributed tracing
- **AlertManager**: Alert routing and notifications
- **Node Exporter**: System resource monitoring

***REMOVED******REMOVED******REMOVED*** 📊 Observability Features

All services include built-in observability:

- **Metrics**: Prometheus metrics at `/metrics` endpoint
  - Request rates, latencies, error rates
  - Resource utilization (CPU, memory)
  - Service-specific metrics (cache hit rates, embedding generation times, etc.)
- **Distributed Tracing**: OpenTelemetry integration
  - Request tracing across microservices
  - Configurable sampling rates
  - Integration with Grafana Alloy
- **Structured Logging**: JSON-formatted logs with correlation IDs
  - Request/response logging
  - Error tracking with stack traces
  - Performance monitoring
- **Health Checks**: Multi-level health endpoints
  - `/health` - Aggregated health status
  - `/health/live` - Liveness probe
  - `/health/ready` - Readiness probe (dependencies)
  - `/health/deep` - Detailed diagnostics

***REMOVED******REMOVED******REMOVED*** 🔒 Security Features

- **Localhost Binding**: All services bind to `127.0.0.1` only
- **Nginx Reverse Proxy**: Controlled external access
- **BFF-Only API Access**: Direct service access blocked from internet
- **SSL/TLS**: HTTPS with strong cipher suites
- **Rate Limiting**: Per-endpoint rate limits via fast-core
- **Security Headers**: HSTS, CSP, frame protection, XSS protection
- **Internal API Keys**: Service-to-service authentication

Access your monitoring:

- **Grafana**: <https://your-domain.com/grafana/> (admin/NextWatch2024Admin)
- **Prometheus**: <https://your-domain.com/prometheus/>
- **AlertManager**: <https://your-domain.com/alertmanager/>

***REMOVED******REMOVED******REMOVED*** Service Health Checks

All services include comprehensive health checks:

- **Backend API**: `GET /health` - Database, Redis, and service status
- **Auth API**: `GET /health` - Database, cache, and JWT service status
- **BFF API**: `GET /health` - Aggregates downstream service health
- **Recommendation API**: `GET /health` - Qdrant, Redis, ML API, and Backend API status
- **ML API**: `GET /health` - Model loading status and embedding service health
- **Search API**: `GET /health` - Redis connection and suggestion engine status
- **Frontend**: Process-based health check
- **Data Importer**: On-demand service

Health checks include:

- Service availability (liveness probes)
- Database connectivity (readiness probes)
- Dependency verification (upstream services)
- Resource monitoring (memory, CPU)
- Deep diagnostics (detailed component status)

***REMOVED******REMOVED*** 🛠️ Development

***REMOVED******REMOVED******REMOVED*** Individual Service Development

Each service can be developed independently using Hatch (Python services) or pnpm (Frontend):

```bash
***REMOVED*** Backend API
cd apps/backend-api
hatch env create
hatch run dev

***REMOVED*** Auth API
cd apps/auth-api
hatch env create
hatch run dev

***REMOVED*** BFF API
cd apps/bff-api
hatch env create
hatch run dev

***REMOVED*** Recommendation API
cd apps/recommendation-api
hatch env create
hatch run dev

***REMOVED*** ML API
cd apps/ml-api
hatch env create
hatch run dev

***REMOVED*** Search API
cd apps/search-api
hatch env create
hatch run dev

***REMOVED*** Frontend
cd apps/web-nextjs
pnpm install
pnpm dev

***REMOVED*** Data Importer
cd apps/data-importer
hatch env create
hatch run cli sync --verbose
```

***REMOVED******REMOVED******REMOVED*** Python Project Configuration

All Python services follow modern packaging standards:

- **Single Configuration File**: All project configuration is in `pyproject.toml` (no separate `hatch.toml` files)
- **Hatch Build System**: Uses Hatch for environment management and builds
- **Local Dependencies**: Development environments include local library dependencies
- **Docker Compatibility**: Production builds comment out local dependencies for Docker

***REMOVED******REMOVED******REMOVED*** CLI Tools

Each Python service includes comprehensive CLI tools accessible via Hatch:

```bash
***REMOVED*** Backend API
cd apps/backend-api
hatch run cli --help
hatch run cli serve start --reload
hatch run cli health check

***REMOVED*** Auth API
cd apps/auth-api
hatch run cli --help
hatch run cli serve start --reload
hatch run cli health check

***REMOVED*** BFF API
cd apps/bff-api
hatch run cli --help
hatch run cli serve start --reload
hatch run cli cache info

***REMOVED*** Recommendation API
cd apps/recommendation-api
hatch run cli --help
hatch run cli embeddings generate --batch-size 100
hatch run cli cache precompute --limit 1000

***REMOVED*** ML API
cd apps/ml-api
hatch run cli --help
hatch run cli model info
hatch run cli health check

***REMOVED*** Search API
cd apps/search-api
hatch run cli --help
hatch run cli redis populate --force
hatch run cli health check

***REMOVED*** Data Importer
cd apps/data-importer
hatch run cli --help
hatch run cli sync --verbose
```

***REMOVED******REMOVED******REMOVED*** Available Hatch Scripts

Each service provides these common scripts:

- `serve` - Start the service
- `dev` - Start with auto-reload
- `cli` - Access CLI commands
- `health` - Health checks
- `config` - Show configuration
- `test` - Run tests
- `lint` - Code linting
- `format` - Code formatting

***REMOVED******REMOVED*** 📚 Documentation

***REMOVED******REMOVED******REMOVED*** Service Documentation

Each service has comprehensive documentation:

- **Backend API**: `apps/backend-api/README.md`
  - Fast-core integration guide
  - Bulk operations optimization
  - Materialized view architecture
  - Metrics integration
- **Recommendation API**: `apps/recommendation-api/README.md`
  - Vector search setup
  - Embedding generation CLI
  - Cache warming strategies
- **ML API**: `apps/ml-api/README.md`
  - Model configuration
  - Embedding endpoints
  - Docker deployment
- **Search API**: `apps/search-api/README.md`
  - Redis index management
  - Performance optimization
- **Auth API**: `apps/auth-api/README.md`
  - JWT configuration
  - API refinement guide
- **BFF API**: `apps/bff-api/README.md`
  - Cache patterns
  - Service orchestration
- **Data Importer**: `apps/data-importer/README.md`
  - TMDB/OMDB sync
  - CLI commands

***REMOVED******REMOVED******REMOVED*** API Documentation

Interactive API documentation available at `/docs` on each service:

- **Backend API**: <http://localhost:8000/docs>
- **Auth API**: <http://localhost:8003/docs>
- **BFF API**: <http://localhost:8001/docs>
- **Recommendation API**: <http://localhost:8002/docs>
- **ML API**: <http://localhost:8004/docs>
- **Search API**: <http://localhost:8005/docs>

***REMOVED******REMOVED******REMOVED*** Infrastructure Documentation

- **Docs index**: `docs/README.md`
- **Onboarding (New Devs)**: `docs/getting-started/ONBOARDING.md`
- **Service Map**: `docs/getting-started/SERVICE_MAP.md`
- **Docs Conventions**: `docs/meta/DOCS_GUIDE.md`
- **Deployment Guide**: `infra/DEPLOYMENT.md`
- **Production Deployment**: `infra/production-deployment-guide.md`
- **Monitoring Setup**: `infra/compose/monitoring.yml`
- **AWS Infrastructure**: `infra/aws/`

***REMOVED******REMOVED*** 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes to relevant services
4. Test locally with Docker Compose
5. Submit a pull request

The CI/CD pipeline will automatically:

- Build changed services
- Run tests
- Deploy to staging (if configured)

***REMOVED******REMOVED*** 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

***REMOVED******REMOVED*** Type Checking Standards

This project uses strict type checking with mypy across all Python services. We follow these principles:

***REMOVED******REMOVED******REMOVED*** Configuration

- All type checking configuration is stored in each service's `pyproject.toml` file
- We use Python 3.12 for type checking
- We enforce the same consistent type checking rules across all API services (BFF API, Backend API, and Recommendation API):
  - `disallow_untyped_defs = true` - All functions must have type annotations
  - `disallow_incomplete_defs = true` - No partial type annotations
  - `check_untyped_defs = true` - Check the body of functions without type annotations
  - `no_implicit_optional = true` - Don't treat None as implicit Optional
  - `disallow_untyped_calls = true` - Can't call functions without type hints
  - `disallow_any_generics = true` - Can't use Any in generic types (like List[Any])
  - `disallow_subclassing_any = true` - Can't subclass Any
  - `disallow_untyped_globals = true` - All module-level variables must have type annotations
  - Full warnings for redundant casts, unused ignores, unreachable code, etc.

***REMOVED******REMOVED******REMOVED*** Type Annotations Style

```python
***REMOVED*** Use explicit imports from typing
from typing import Dict, List, Optional, Union, Any, Callable, TypeVar, Generic

***REMOVED*** All module-level variables must have explicit type annotations
app: Typer = typer.Typer(name="app")
user_data: Dict[str, Any] = get_user()
items: List[int] = [1, 2, 3]
DEFAULT_TIMEOUT: int = 30
RETRY_COUNT: int = 3

***REMOVED*** Function annotations with return type
def process_data(input_value: str, count: int = 0) -> List[Dict[str, Any]]:
    ...

***REMOVED*** Generic types with constraints
T = TypeVar('T', bound=BaseModel)
def get_item(item_id: str) -> Optional[T]:
    ...
```

***REMOVED******REMOVED******REMOVED*** Enforcement

Type checking is enforced through:

1. Pre-commit hooks (see `.pre-commit-config.yaml`)
2. CI pipeline checks
3. Code reviews

***REMOVED******REMOVED******REMOVED*** Running Type Checks

To run type checks manually:

```bash
***REMOVED*** Check a specific service
cd apps/bff-api && python -m mypy src/

***REMOVED*** Or for recommendation-api
cd apps/recommendation-api && python -m mypy src/
```

To fix common type issues:

```bash
***REMOVED*** Install type stubs for libraries
pip install types-redis types-requests

***REMOVED*** Add explicit type annotations to functions
def my_function(param: str) -> None:
    ...
```

***REMOVED******REMOVED*** Next Watch Development Progress

***REMOVED******REMOVED******REMOVED*** 🎯 Service Features

***REMOVED******REMOVED******REMOVED******REMOVED*** Backend API

- Movie metadata retrieval with precomputed materialized views
- Bulk movie operations with Redis caching
- User watchlist and favorites management
- PostgreSQL with optimized queries using `ANY()` operator
- Netflix-style "cache forever" pattern for static content

***REMOVED******REMOVED******REMOVED******REMOVED*** Recommendation API

- Vector similarity search using Qdrant
- Collaborative filtering recommendations
- Trending and popular movie endpoints
- ML API integration for embedding generation
- Redis caching with background cache warming
- CLI tools for embedding generation and cache management

***REMOVED******REMOVED******REMOVED******REMOVED*** ML API

- Movie embedding generation using sentence-transformers
- User preference vector calculation
- Model: all-MiniLM-L6-v2 (384 dimensions)
- Batch processing support
- Model caching and health monitoring

***REMOVED******REMOVED******REMOVED******REMOVED*** Search API

- Redis-powered autocomplete suggestions
- Prefix and substring search
- Entity-based search (movies, actors, directors)
- Optimized lexicographical range queries
- CLI for populating and managing search indices

***REMOVED******REMOVED******REMOVED******REMOVED*** Auth API

- JWT-based authentication
- Access and refresh token management
- User registration and login
- Password reset functionality
- Rate limiting for security

***REMOVED******REMOVED******REMOVED******REMOVED*** BFF API

- Frontend aggregation layer
- Response caching with TTL management
- Downstream service orchestration
- User-specific data enrichment
- Cache warming with cron jobs

***REMOVED******REMOVED******REMOVED*** Current Status 🚀

All core services are integrated with fast-core framework for standardized patterns.

***REMOVED******REMOVED******REMOVED******REMOVED*** **✅ Fast-Core Integration Status**

1. **BFF API** - ✅ Complete - Middleware builder integration with cache warming
2. **Backend API** - ✅ Complete - Independent service architecture with materialized views
3. **Recommendation API** - ✅ Complete - ML service communication with vector search
4. **Auth API** - ✅ Complete - Security-first integration with JWT middleware
5. **ML API** - ✅ Complete - Embedding service with model management
6. **Search API** - ✅ Complete - Redis-powered search with suggestion engine

***REMOVED******REMOVED******REMOVED******REMOVED*** **✅ Completed: Auth API Fast-Core Integration**

Successfully integrated auth-api with fast-core following established patterns with authentication-specific security enhancements.

***REMOVED******REMOVED******REMOVED******REMOVED*** **Integration Achievements**

The Auth API integration delivers a security-first approach with:

- **🔒 Security-Hardened Architecture**: Production-grade security headers and authentication-specific middleware
- **⚡ Performance-Optimized Stack**: Efficient middleware chain with auth-specific rate limiting
- **🔧 Standardized Configuration**: Consistent FastAPI patterns with auth-specific optimizations
- **📊 Enhanced Monitoring**: Request tracing and authentication flow monitoring
- **🛡️ Authentication Security**: Aggressive rate limiting and restrictive CORS for auth endpoints

***REMOVED******REMOVED******REMOVED******REMOVED*** **📁 Planned Integration Structure**

```text
auth-api/
├── src/auth_api/
│   ├── config/
│   │   ├── app.py                    ***REMOVED*** Original configuration (preserved)
│   │   └── fast_core_config.py       ***REMOVED*** Fast-core adapter (NEW)
│   ├── core/
│   │   ├── app.py                    ***REMOVED*** Original app factory (preserved)
│   │   └── app_fast_core.py          ***REMOVED*** Fast-core app factory (NEW)
│   └── main.py                       ***REMOVED*** Updated to use fast-core
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **🎯 Key Integration Components**

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **1. Configuration Adapter (`config/fast_core_config.py`)**

Convert Auth API configuration to fast-core compatible format:

```python
def create_fast_core_config(auth_config: Config) -> FastAPIConfig:
    """Convert Auth API configuration to fast-core configuration."""
    ***REMOVED*** Maps JWT settings, security configs, service URLs, etc.
```

**Features:**

- JWT configuration mapping (secret, algorithm, expiration)
- Security settings (CORS, allowed hosts, rate limiting)
- Database and cache configuration
- Feature flags for auth service capabilities
- Development vs production security profiles

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **2. Fast-Core App Factory (`core/app_fast_core.py`)**

Create FastAPI application using fast-core patterns:

```python
def create_auth_app(config: Optional[Config] = None) -> FastAPI:
    """Create Auth API application using fast-core."""
    ***REMOVED*** Uses MiddlewareConfig, JWT integration, security features
```

**Features:**

- **Lifespan Management**: Database, cache, and health service initialization
- **Security Middleware**: Enhanced security headers, JWT validation, rate limiting
- **Router Integration**: Auth, health, and meta routes with fast-core patterns
- **Error Handling**: Consistent auth-specific error responses

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **3. Auth-Specific Middleware Configuration**

Authentication service middleware with security-first approach:

```python
***REMOVED*** CORS Configuration (restrictive for auth service)
middleware.cors(
    origins=config.cors_origins,  ***REMOVED*** Specific allowed origins only
    credentials=True,             ***REMOVED*** Required for auth cookies/tokens
    methods=["POST", "GET", "OPTIONS"],  ***REMOVED*** Limited to auth operations
    headers=["Content-Type", "Authorization"],
    max_age=300,  ***REMOVED*** Short cache for auth endpoints
)

***REMOVED*** Enhanced Security Headers
security_headers = {
    "hsts": True,                 ***REMOVED*** Force HTTPS in production
    "csp": "default-src 'self'",  ***REMOVED*** Strict content policy
    "frame_protection": True,     ***REMOVED*** Prevent iframe attacks
    "xss_protection": True,       ***REMOVED*** XSS prevention
}

***REMOVED*** Auth-Specific Rate Limiting
rate_limit_config = {
    "/auth/login": "10/minute",           ***REMOVED*** Login attempts
    "/auth/register": "5/minute",         ***REMOVED*** Registration attempts
    "/auth/refresh": "30/minute",         ***REMOVED*** Token refresh
    "/auth/logout": "20/minute",          ***REMOVED*** Logout requests
    "/auth/password/reset": "3/minute",   ***REMOVED*** Password reset
    "/auth/verify": "100/minute",         ***REMOVED*** Token verification
}
```

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **4. JWT Integration with Fast-Core**

Leverage fast-core's JWT utilities:

```python
from fast_core.security.jwt import create_jwt_manager, JWTConfig

***REMOVED*** Configure JWT with auth-api settings
jwt_config = JWTConfig(
    secret_key=config.jwt_secret,
    algorithm=config.jwt_algorithm,
    access_token_expire_minutes=config.access_token_expire_minutes,
    refresh_token_expire_days=config.refresh_token_expire_days
)

jwt_manager = create_jwt_manager(jwt_config)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **🔄 Migration Strategy**

Following backend-api's successful approach:

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **Phase 1: Dependencies & Configuration** (Target: 2 days)

- [ ] Add fast-core dependency to pyproject.toml
- [ ] Install fast-core library
- [ ] Create configuration adapter (`config/fast_core_config.py`)
- [ ] Test configuration conversion and validation

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **Phase 2: Core App Integration** (Target: 3 days)

- [ ] Create fast-core app factory (`core/app_fast_core.py`)
- [ ] Update main.py to use fast-core integration
- [ ] Implement auth-specific middleware configuration
- [ ] Test basic application functionality

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **Phase 3: Security Enhancement** (Target: 2 days)

- [ ] Integrate fast-core JWT utilities
- [ ] Implement enhanced rate limiting for auth endpoints
- [ ] Add comprehensive security headers
- [ ] Test authentication flows with new middleware

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **Phase 4: Testing & Validation** (Target: 2 days)

- [ ] Comprehensive testing of all auth endpoints
- [ ] Performance validation with middleware stack
- [ ] Security testing and validation
- [ ] Integration testing with other services

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **Phase 5: Documentation & Cleanup** (Target: 1 day)

- [ ] Create FAST_CORE_INTEGRATION.md documentation
- [ ] Update README and configuration docs
- [ ] Clean up any legacy code if needed
- [ ] Final integration validation

***REMOVED******REMOVED******REMOVED******REMOVED*** **🔧 Auth-Specific Benefits**

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **1. Enhanced Security**

- **Built-in rate limiting** protecting against brute force attacks
- **Comprehensive security headers** for production-ready auth service
- **JWT token validation** with fast-core utilities
- **CORS configuration** tailored for authentication workflows

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **2. Consistent Error Handling**

- **Standardized auth error responses** across all endpoints
- **Detailed logging** for security events and authentication attempts
- **Request tracking** with correlation IDs for debugging

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **3. Performance Optimization**

- **Singleton database connections** for improved performance
- **Efficient middleware stack** with minimal overhead
- **Response compression** and optimized headers

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** **4. Observability**

- **Health checks** for database, cache, and JWT services
- **Performance metrics** for authentication operations
- **Structured logging** with security-focused log levels

***REMOVED******REMOVED******REMOVED******REMOVED*** **📊 Feature Flags**

Auth API specific feature toggles:

```python
feature_flags = {
    "jwt_validation": True,
    "refresh_tokens": True,
    "password_reset": True,
    "user_registration": True,
    "session_management": True,
    "two_factor_auth": False,  ***REMOVED*** Future feature
    "social_login": False,     ***REMOVED*** Future feature
    "health_checks": True,
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **🔄 Backward Compatibility**

Maintain full backward compatibility during integration:

- **Original app factory** (`core/app.py`) preserved
- **Configuration system** remains unchanged
- **All existing routes** continue to work
- **Database and auth services** maintain same initialization
- **Gradual migration** path with rollback capability

***REMOVED******REMOVED******REMOVED******REMOVED*** **🧪 Testing Strategy**

Comprehensive testing approach:

```python
***REMOVED*** Test fast-core integration
from auth_api.core.app_fast_core import create_auth_app

def test_auth_app_creation():
    app = create_auth_app()
    assert app.title == "Next Watch Authentication API"
    assert "fast-core" in str(app.middleware_stack)

def test_jwt_integration():
    ***REMOVED*** Test JWT validation with fast-core
    pass

def test_rate_limiting():
    ***REMOVED*** Test auth endpoint rate limits
    pass
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **📚 Reference Implementation**

Following the successful patterns from:

- [Backend API Fast-Core Integration](apps/backend-api/FAST_CORE_INTEGRATION.md)
- [BFF API Integration Guide](apps/bff-api/FAST_CORE_INTEGRATION.md)
- [Fast-Core Library Documentation](libs/fast-core/README.md)

This integration will establish Auth API as a fully fast-core compatible service while maintaining security-first principles and providing enhanced authentication capabilities for the Next Watch platform.

***REMOVED******REMOVED*** 🔧 Troubleshooting

***REMOVED******REMOVED******REMOVED*** BFF API OpenTelemetry Dependencies Issue

**Problem**: BFF API Docker builds were not including OpenTelemetry dependencies required by fast-core, causing deployment failures with missing modules.

**Root Cause**: The BFF API's Dockerfile was installing `fast-core` as a local dependency (`pip install ./libs/fast-core/`), but this doesn't automatically install the transitive dependencies defined in fast-core's `pyproject.toml`.

**Solution**: Modified the Dockerfile to install local dependencies with the `-e` (editable) flag to ensure all transitive dependencies are properly resolved:

```dockerfile
***REMOVED*** Install local dependencies with dependencies to ensure all transitive dependencies are resolved
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -e ./libs/config/ && \
    pip install --user -e ./libs/cache/ && \
    pip install --user -e ./libs/cli/ && \
    pip install --user -e ./libs/fast-core/
```

**Verification**: After this fix, all OpenTelemetry packages are properly installed:

```bash
***REMOVED*** Check installed packages
docker run --rm bff-api:latest pip list | grep -i opentelemetry
```

**Files Modified**:

- `apps/bff-api/Dockerfile`: Updated local dependency installation to use `-e` flag
