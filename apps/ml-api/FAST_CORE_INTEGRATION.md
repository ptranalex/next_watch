***REMOVED*** Fast Core Integration - ML API

This document outlines the integration of the ML API with the fast-core framework, providing standardized patterns for FastAPI application development.

***REMOVED******REMOVED*** Overview

The ML API has been migrated from a manual FastAPI setup to use the fast-core framework, which provides:

- **Standardized Configuration**: Using the config library with ServiceConfig as base
- **Enhanced Middleware**: CORS, security headers, rate limiting, logging, and metrics
- **Dependency Injection**: Consistent patterns for service dependencies
- **Error Handling**: Standardized error responses and service error contexts
- **Monitoring**: Built-in health checks and Prometheus metrics

***REMOVED******REMOVED*** Key Changes

***REMOVED******REMOVED******REMOVED*** 1. Package Structure

**Before:**

```
ml-api/
├── ml_api/
│   ├── app.py
│   ├── config/app.py
│   └── ...
└── pyproject.toml
```

**After:**

```
ml-api/
├── src/
│   └── ml_api/
│       ├── main.py              ***REMOVED*** New main entry point
│       ├── __main__.py          ***REMOVED*** Module execution support
│       ├── app.py               ***REMOVED*** Legacy support (updated)
│       ├── config/
│       │   ├── app.py           ***REMOVED*** MLAPIConfig (ServiceConfig-based)
│       │   └── fast_core_config.py  ***REMOVED*** Fast-core adapter
│       ├── core/
│       │   ├── __init__.py      ***REMOVED*** Exports create_app
│       │   ├── app_fast_core.py ***REMOVED*** Fast-core application factory
│       │   └── metrics.py       ***REMOVED*** ML-specific metrics
│       ├── cli/
│       │   ├── main.py          ***REMOVED*** CLI entry point
│       │   ├── __main__.py      ***REMOVED*** CLI module execution
│       │   └── commands/        ***REMOVED*** CLI commands
│       └── routes/
│           ├── embeddings.py    ***REMOVED*** Embedding endpoints
│           └── health.py        ***REMOVED*** Health check endpoints
└── pyproject.toml              ***REMOVED*** Updated with proper hatch config
```

***REMOVED******REMOVED******REMOVED*** 2. Configuration System

**Before:**

```python
***REMOVED*** Simple singleton configuration
class Config:
    def __init__(self, host="0.0.0.0", port=8000, ...):
        self.host = host
        self.port = port
```

**After:**

```python
***REMOVED*** ServiceConfig-based configuration with validation
class MLAPIConfig(ServiceConfig):
    service_name: str = Field(default="ml-api")
    port: int = Field(default=8000)
    ***REMOVED*** ML-specific features
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    enable_embeddings: bool = Field(default=True)
    enable_batch_processing: bool = Field(default=True)
    enable_model_caching: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)
```

***REMOVED******REMOVED******REMOVED*** 3. Application Factory

**Before:**

```python
***REMOVED*** Manual FastAPI setup
def create_app():
    app = FastAPI(title="ML API", ...)
    app.add_middleware(CORSMiddleware, ...)
    app.include_router(embeddings_router)
    return app
```

**After:**

```python
***REMOVED*** Fast-core integration
def create_ml_app(config=None):
    fast_core_config = create_fast_core_config(config)
    middleware_config = create_ml_middleware_config(config)
    app = create_app(config=fast_core_config, options=app_options)
    return app
```

***REMOVED******REMOVED******REMOVED*** 4. Hatch Configuration

The ML API now follows the standard NextWatch hatch pattern:

```toml
[tool.hatch.envs.default]
type = "virtual"
path = ".venv"
features = ["dev"]

[tool.hatch.envs.default.env-vars]
PYTHONPATH = "src"

[tool.hatch.envs.default.scripts]
***REMOVED*** Install local libraries
install-libs = [
  "pip install -e ../../libs/config",
  "pip install -e ../../libs/cli",
  "pip install -e ../../libs/fast-core",
]

***REMOVED*** Server management
serve = "python -m ml_api.main"
dev = "PYTHONPATH=src uvicorn ml_api.app:app --reload --port 8000"

***REMOVED*** CLI access
cli = "python -m ml_api.cli"

***REMOVED*** Health checks
health-check = "python -m ml_api.cli health check"
health-model = "python -m ml_api.cli health model"

***REMOVED*** Model management
model-info = "python -m ml_api.cli model info"
model-load = "python -m ml_api.cli model load"
model-test = "python -m ml_api.cli model test"
```

***REMOVED******REMOVED******REMOVED*** 5. Middleware Configuration

The new setup provides comprehensive middleware through fast-core:

- **CORS**: Configured for ML API service patterns (internal service)
- **Security Headers**: Production-ready security policies
- **Rate Limiting**: Endpoint-specific limits for embedding operations
  - `/embeddings`: 100/minute
  - `/embeddings/batch`: 20/minute
  - `/health`: 1000/minute
- **Request Processing**: 5MB request size limits, 120s timeouts
- **Logging**: Structured logging with configurable verbosity
- **Metrics**: Prometheus metrics for ML-specific operations

***REMOVED******REMOVED******REMOVED*** 6. Health Checks

Health endpoints moved to dedicated router:

- `/health` - Basic API health
- `/ping` - Simple connectivity test
- `/health/model` - ML model health and status

***REMOVED******REMOVED******REMOVED*** 7. Metrics Integration

ML-specific metrics for monitoring:

- `ml_embedding_requests_total` - Request counters by model and batch size
- `ml_embedding_duration_seconds` - Processing time histograms
- `ml_embedding_batch_size` - Batch size distribution
- `ml_model_load_duration_seconds` - Model loading performance
- `ml_model_memory_usage_bytes` - Model memory consumption
- `ml_embedding_errors_total` - Error counters by type

***REMOVED******REMOVED*** Installation

1. **Install Dependencies:**

```bash
cd ml-api
hatch run install-libs
```

2. **Run Development Server:**

```bash
hatch run dev
```

3. **Run with CLI:**

```bash
hatch run serve
```

***REMOVED******REMOVED*** Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

The ML API now supports comprehensive environment configuration:

```bash
***REMOVED*** Service configuration
SERVICE_NAME=ml-api
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

***REMOVED*** ML-specific configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
MODEL_CACHE_DIR=/app/model_cache
MAX_BATCH_SIZE=32
EMBEDDINGS_DB_PATH=/app/embeddings.db

***REMOVED*** Feature flags
ENABLE_EMBEDDINGS=true
ENABLE_BATCH_PROCESSING=true
ENABLE_MODEL_CACHING=true
ENABLE_METRICS=true

***REMOVED*** Security (production)
ALLOWED_HOSTS=localhost,127.0.0.1,ml-api.example.com
CORS_ORIGINS=https://backend.example.com,https://recommendation.example.com
```

***REMOVED******REMOVED******REMOVED*** Configuration Validation

The new configuration system provides validation:

- Port ranges and timeout limits
- Batch size constraints (1-1000)
- Model cache directory validation
- Production security checks

***REMOVED******REMOVED*** API Changes

***REMOVED******REMOVED******REMOVED*** No Breaking Changes

The API endpoints remain unchanged:

- `POST /embeddings/movie` - Generate movie embeddings
- `POST /embeddings/user` - Generate user preference vectors
- `GET /embeddings/info` - Get model information
- `GET /health` - Health checks
- `GET /ping` - Connectivity test
- `GET /health/model` - Model health

***REMOVED******REMOVED******REMOVED*** Enhanced Features

1. **Rate Limiting**: Automatic rate limiting on embedding endpoints
2. **Request Tracking**: All requests include X-Request-ID headers
3. **Metrics Exposure**: `/metrics` endpoint for Prometheus scraping
4. **Enhanced Logging**: Structured logging with configurable levels
5. **Security Headers**: Production-ready security policies
6. **CORS Configuration**: Proper CORS for internal service communication

***REMOVED******REMOVED*** Development Workflow

***REMOVED******REMOVED******REMOVED*** Local Development

```bash
***REMOVED*** Install dependencies
hatch run install-libs

***REMOVED*** Run development server with reload
hatch run dev

***REMOVED*** Run tests
hatch run test

***REMOVED*** Check code quality
hatch run lint

***REMOVED*** Format code
hatch run format
```

***REMOVED******REMOVED******REMOVED*** CLI Commands

```bash
***REMOVED*** CLI help
hatch run cli --help

***REMOVED*** Check health
hatch run health-check

***REMOVED*** Model management
hatch run model-info
hatch run model-load
hatch run model-test

***REMOVED*** Configuration
hatch run config
```

***REMOVED******REMOVED******REMOVED*** Production Deployment

The ML API now supports production-ready patterns:

- Environment-based configuration
- Security headers and CORS policies
- Rate limiting and request size controls
- Comprehensive monitoring and metrics
- Graceful shutdown handling

***REMOVED******REMOVED*** Migration Benefits

1. **Consistency**: Standardized patterns across all Next Watch services
2. **Maintainability**: Reduced boilerplate and centralized configurations
3. **Observability**: Built-in metrics and structured logging
4. **Security**: Production-ready security policies by default
5. **Performance**: Optimized middleware and request handling
6. **Developer Experience**: Better error handling and debugging tools
7. **Package Management**: Proper src structure following Python best practices

***REMOVED******REMOVED*** Next Steps

- [ ] Test the integration with dependencies installed
- [ ] Add integration tests for fast-core features
- [ ] Set up Prometheus monitoring in development
- [ ] Configure production environment variables
- [ ] Add custom middleware for ML-specific requirements
- [ ] Implement caching strategies using fast-core cache dependencies
- [ ] Add CLI commands for model management and health checks
