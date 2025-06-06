***REMOVED*** BFF API Service

Backend for Frontend (BFF) service for the Next Watch movie platform. This service acts as an aggregation layer between the Next.js frontend and various backend services, providing optimized data structures and caching for the UI.

***REMOVED******REMOVED*** 🎯 Purpose

The BFF aggregates data from multiple backend services and provides optimized endpoints for specific UI screens, reducing the complexity and number of API calls required by the frontend.

***REMOVED******REMOVED*** 🧱 Core Responsibilities

- ✅ **Data Aggregation**: Combine data from backend-api, databases, and other services
- ✅ **Screen-Oriented Endpoints**: Provide UI-specific endpoints like `/bff/home`, `/bff/movies/:id`
- ✅ **User-Aware Logic**: Embed user-specific data (watchlist status, favorites, ratings)
- ✅ **Service Abstraction**: Hide backend service boundaries from the frontend
- ✅ **Caching & Performance**: Optimize data delivery with intelligent caching

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

***REMOVED*** Run database migrations
hatch run migrate
hatch run upgrade

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

Redis cache management and monitoring:

```bash
***REMOVED*** Display cache information
hatch run cache info [OPTIONS]

Options:
  --redis-url TEXT      Redis URL (overrides config)
  --verbose, -v         Show detailed Redis information

***REMOVED*** List cache keys
hatch run cache keys [OPTIONS]

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
GET /api/v1/movies/trending     ***REMOVED*** Trending movies with caching
GET /api/v1/movies/{id}         ***REMOVED*** Movie details with cast/crew
GET /api/v1/search              ***REMOVED*** Search with suggestions
GET /api/v1/user/watchlist      ***REMOVED*** User's watchlist (aggregated)
```

***REMOVED******REMOVED******REMOVED*** Health Endpoints

```http
GET /health/          ***REMOVED*** Basic health check
GET /health/ready     ***REMOVED*** Readiness check (K8s)
GET /health/live      ***REMOVED*** Liveness check (K8s)
```

***REMOVED******REMOVED*** 🧩 Integration Points

***REMOVED******REMOVED******REMOVED*** Backend Services

- **backend-api**: Primary source for movie metadata, genres, cast
- **auth-api**: Authentication and user management
- **Redis**: Caching layer for performance optimization

***REMOVED******REMOVED******REMOVED*** Configuration

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

***REMOVED*** Auth Service Integration
AUTH_API_URL=http://localhost:8003

***REMOVED*** Service-to-Service Authentication
INTERNAL_API_KEY=bff-to-backend-secret-key-change-in-production

***REMOVED*** Caching
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

***REMOVED*** Security
JWT_SECRET=your-jwt-secret-here-change-in-production

***REMOVED*** CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8001

***REMOVED*** Performance Monitoring
ENABLE_PERFORMANCE_METRICS=false
```

***REMOVED******REMOVED*** 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   BFF Service   │────│  Backend API    │
│                 │    │                 │    │                 │
│ - Home Screen   │    │ - Data Agg.     │    │ - Movie Data    │
│ - Movie Detail  │    │ - User Context  │    │ - User Data     │
│ - Search        │    │ - Caching       │    │ - Business Logic│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │   Auth API      │
                       │   (Caching)     │    │ (Authentication)│
                       └─────────────────┘    └─────────────────┘
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

***REMOVED******REMOVED******REMOVED*** Adding New CLI Commands

1. **Create command module** in `src/bff_api/cli/commands/`
2. **Import in commands/**init**.py**
3. **Add to main CLI app** in `src/bff_api/cli/main.py`
4. **Write tests** for the new commands
5. **Update documentation**

Example command structure:

```python
***REMOVED*** src/bff_api/cli/commands/example.py
import typer
from rich.console import Console

app = typer.Typer(name="example", help="Example commands.")
console = Console()

@app.command()
def hello(name: str = typer.Option(..., help="Name to greet")):
    """Say hello to someone."""
    console.print(f"[green]Hello {name}![/green]")
```

***REMOVED******REMOVED******REMOVED*** Project Structure

```
apps/bff-api/
├── src/bff_api/
│   ├── config/          ***REMOVED*** Configuration management
│   ├── routes/          ***REMOVED*** FastAPI route handlers
│   ├── services/        ***REMOVED*** External service clients
│   ├── middlewares/     ***REMOVED*** Custom middleware
│   ├── cli/            ***REMOVED*** Command-line interface
│   │   ├── commands/   ***REMOVED*** Modular CLI commands
│   │   ├── utils.py    ***REMOVED*** CLI utilities
│   │   └── main.py     ***REMOVED*** Main CLI app
│   └── main.py         ***REMOVED*** FastAPI application
├── tests/              ***REMOVED*** Test suite
├── pyproject.toml      ***REMOVED*** Dependencies and config
└── README.md          ***REMOVED*** This file
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

***REMOVED******REMOVED*** 📊 Monitoring

The BFF service provides several monitoring endpoints:

- Health checks for load balancer integration
- Structured logging for observability
- Request/response timing middleware
- Error tracking and reporting
- CLI tools for operational monitoring

***REMOVED******REMOVED*** 🤝 Contributing

1. Follow TDD practices - write tests first
2. Use type hints for all functions
3. Add docstrings following Google style
4. Update README for any API changes
5. Ensure all tests pass before submitting
6. Test CLI commands thoroughly

***REMOVED******REMOVED*** 📝 License

This project is part of the Next Watch movie platform.
