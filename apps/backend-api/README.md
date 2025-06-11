***REMOVED*** Next Watch Backend API

A FastAPI-based Backend for Frontend (BFF) service for the Next Watch application, featuring a clean architecture with comprehensive health monitoring and modular design.

***REMOVED******REMOVED*** Architecture Overview

The Backend API follows modern FastAPI best practices with a modular, testable architecture:

```
backend-api/
├── src/backend_api/
│   ├── core/               ***REMOVED*** Application factory and core components
│   │   ├── app.py         ***REMOVED*** FastAPI app factory with lifespan management
│   │   ├── middleware.py  ***REMOVED*** CORS, error handling, performance monitoring
│   │   └── logging.py     ***REMOVED*** Logging configuration wrapper
│   ├── routes/            ***REMOVED*** HTTP endpoints organized by function
│   │   ├── api_v1/        ***REMOVED*** Versioned API routes (main business logic)
│   │   ├── health.py      ***REMOVED*** Comprehensive health check endpoints
│   │   └── meta.py        ***REMOVED*** Root and debug endpoints
│   ├── services/          ***REMOVED*** Business logic and service classes
│   │   ├── health_service.py  ***REMOVED*** Multi-service health monitoring
│   │   ├── movie_service.py   ***REMOVED*** Movie-related operations
│   │   ├── user_interaction.py ***REMOVED*** User interactions and social features
│   │   ├── suggestion_engine.py ***REMOVED*** Redis-based recommendations
│   │   └── auth.py        ***REMOVED*** Authentication and authorization
│   ├── config/            ***REMOVED*** Configuration management
│   │   ├── app.py         ***REMOVED*** Application settings and environment variables
│   │   └── logging.py     ***REMOVED*** Centralized logging configuration
│   ├── db/                ***REMOVED*** Database models and connections
│   ├── queries/           ***REMOVED*** Database query operations
│   ├── schemas/           ***REMOVED*** Pydantic schemas for API contracts
│   ├── cli/               ***REMOVED*** Command-line interface
│   │   ├── commands/      ***REMOVED*** CLI command implementations
│   │   │   ├── database.py ***REMOVED*** Database management commands (consolidated)
│   │   │   ├── cache.py   ***REMOVED*** Cache management commands
│   │   │   ├── health.py  ***REMOVED*** Health check commands
│   │   │   ├── config.py  ***REMOVED*** Configuration commands
│   │   │   ├── serve.py   ***REMOVED*** Server management commands
│   │   │   └── version.py ***REMOVED*** Version information commands
│   │   └── __init__.py    ***REMOVED*** CLI application setup
│   └── main.py            ***REMOVED*** Clean application entry point
└── README.md              ***REMOVED*** This file
```

***REMOVED******REMOVED******REMOVED*** Key Architectural Benefits

- **Application Factory Pattern**: Clean app creation with dependency injection
- **Health Service Integration**: Comprehensive dependency monitoring
- **Modular Design**: Well-organized, testable components
- **Graceful Degradation**: Robust error handling and fallback mechanisms
- **Clean Separation**: Clear distinction between routes, services, and configuration
- **Comprehensive CLI**: Full-featured command-line interface with flat, intuitive structure

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** Core Functionality

- Movie data API endpoints with advanced search
- User authentication with JWT and role-based access
- User profiles, preferences, and social interactions
- Comprehensive genre and cast information
- Watchlist and recommendation management

***REMOVED******REMOVED******REMOVED*** Health Monitoring

- **Multi-Service Health Checks**: PostgreSQL and Redis monitoring
- **Three Health Endpoints**: Comprehensive, liveness, and readiness checks
- **Load Balancer Integration**: Kubernetes and Docker health probe support
- **Detailed Metrics**: Response times, connection status, and error reporting
- **Fallback Mechanisms**: Continues operation even if some services fail

***REMOVED******REMOVED******REMOVED*** Production Ready

- Comprehensive logging with structured output
- Performance monitoring with request timing
- CORS configuration for microservice architecture
- Global exception handling with detailed error reporting
- Environment-aware configuration with security considerations

***REMOVED******REMOVED*** Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Python 3.10+
- Hatch for dependency management
- PostgreSQL database
- Redis server (optional, for suggestions)

***REMOVED******REMOVED******REMOVED*** Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/next_watch.git
   cd next_watch/apps/backend-api
   ```

2. Install dependencies:

   ```bash
   ***REMOVED*** Using Hatch (recommended)
   hatch env create
   ```

3. Configure environment variables by creating a `.env` file based on `.env.example`.

4. Initialize the database:

   ```bash
   ***REMOVED*** Run database migrations
   hatch run migrate
   ```

5. Run the development server:

   ```bash
   ***REMOVED*** Using Hatch (recommended)
   hatch run dev

   ***REMOVED*** Or using the CLI directly
   python -m backend_api.cli serve

   ***REMOVED*** Or directly with Python
   python -m backend_api.main
   ```

***REMOVED******REMOVED*** Health Monitoring

The Backend API provides comprehensive health monitoring with three specialized endpoints:

***REMOVED******REMOVED******REMOVED*** Health Check Endpoints

***REMOVED******REMOVED******REMOVED******REMOVED*** Comprehensive Health Check (`/health`)

- **Purpose**: Full system health diagnostics
- **Checks**: PostgreSQL database, Redis cache
- **Response**: Detailed metrics with response times and service details
- **Usage**: System monitoring, debugging, detailed diagnostics

```bash
curl http://localhost:8000/health | jq .
```

```json
{
  "status": "healthy",
  "service": "backend-api",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "checks": {
    "postgres": {
      "status": "healthy",
      "healthy": true,
      "response_time_ms": 15.42,
      "details": {
        "version": "PostgreSQL 14.13",
        "database_size": "172 MB",
        "connection_successful": true
      }
    },
    "redis": {
      "status": "healthy",
      "healthy": true,
      "response_time_ms": 8.33,
      "details": {
        "version": "7.2.5",
        "connected_clients": 2,
        "used_memory_human": "4.65M"
      }
    }
  }
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Liveness Check (`/health/live`)

- **Purpose**: Container/process liveness verification
- **Response**: Always returns 200 if service is running
- **Usage**: Kubernetes liveness probes, Docker healthchecks

```bash
curl http://localhost:8000/health/live
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Readiness Check (`/health/ready`)

- **Purpose**: Traffic readiness verification
- **Checks**: Critical services only (PostgreSQL)
- **Usage**: Load balancer readiness probes, Kubernetes readiness probes

```bash
curl http://localhost:8000/health/ready
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Legacy Database Health (`/db-health`)

- **Purpose**: Backward compatibility
- **Note**: Use `/health` for comprehensive monitoring

***REMOVED******REMOVED******REMOVED*** Load Balancer Integration

***REMOVED******REMOVED******REMOVED******REMOVED*** Kubernetes Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 30
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Docker Compose Configuration

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

***REMOVED******REMOVED*** CLI Reference

The backend API comes with a comprehensive CLI tool with a clean, flat command structure:

***REMOVED******REMOVED******REMOVED*** Command Structure

The CLI is organized with minimal nesting for intuitive usage:

- **Top-level commands**: `config`, `serve`, `version`
- **Command groups**: `db`, `health`, `cache`

***REMOVED******REMOVED******REMOVED*** Server Management

```bash
***REMOVED*** Start development server with auto-reload
hatch run dev

***REMOVED*** Start production server
python -m backend_api.cli serve

***REMOVED*** Start with custom options
python -m backend_api.cli serve --host 0.0.0.0 --port 8080 --reload
```

***REMOVED******REMOVED******REMOVED*** Database Management

```bash
***REMOVED*** Initialize database
python -m backend_api.cli db init

***REMOVED*** Initialize with table creation
python -m backend_api.cli db init --create-tables

***REMOVED*** Run database migrations
python -m backend_api.cli db migrate
hatch run migrate  ***REMOVED*** Shortcut

***REMOVED*** Downgrade migrations
python -m backend_api.cli db downgrade
python -m backend_api.cli db downgrade --steps 3
python -m backend_api.cli db downgrade --target 005_add_ratings_and_awards

***REMOVED*** Teardown database (development only)
python -m backend_api.cli db teardown --confirm
```

***REMOVED******REMOVED******REMOVED*** Health Checks

```bash
***REMOVED*** Check overall system health
python -m backend_api.cli health

***REMOVED*** Check specific services
python -m backend_api.cli health redis
python -m backend_api.cli health db
```

***REMOVED******REMOVED******REMOVED*** Cache Management

```bash
***REMOVED*** Display cache information
python -m backend_api.cli cache info

***REMOVED*** Manage cache keys
python -m backend_api.cli cache keys --pattern "user:*"
python -m backend_api.cli cache get "movie:123"
python -m backend_api.cli cache delete "session:456" --confirm
python -m backend_api.cli cache clear --pattern "temp:*" --confirm
```

***REMOVED******REMOVED******REMOVED*** Configuration and System

```bash
***REMOVED*** Display current configuration
python -m backend_api.cli config

***REMOVED*** Show detailed configuration
python -m backend_api.cli config --verbose

***REMOVED*** Display version information
python -m backend_api.cli version
```

***REMOVED******REMOVED******REMOVED*** Hatch Shortcuts

For convenience, common commands are available as Hatch shortcuts:

```bash
***REMOVED*** Database operations
hatch run migrate
hatch run db-init
hatch run db-init-tables

***REMOVED*** Health checks
hatch run health
hatch run health-redis
hatch run health-db

***REMOVED*** Cache management
hatch run cache-info
hatch run cache-keys
hatch run cache-clear

***REMOVED*** System commands
hatch run config
hatch run version
```

***REMOVED******REMOVED*** Configuration

The backend API uses a structured configuration system with environment-aware settings:

***REMOVED******REMOVED******REMOVED*** Environment Variables

| Variable                      | Description                                 | Default                                                    |
| ----------------------------- | ------------------------------------------- | ---------------------------------------------------------- |
| `DATABASE_URL`                | PostgreSQL connection string                | `postgresql://postgres:postgres@localhost:5432/next_watch` |
| `REDIS_URL`                   | Redis connection URL                        | `redis://localhost:6379/0`                                 |
| `API_PORT`                    | Port for the API server                     | `8000`                                                     |
| `LOG_LEVEL`                   | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO`                                                     |
| `DEBUG`                       | Enable debug mode                           | `false`                                                    |
| `CORS_ORIGINS`                | Comma-separated list of allowed origins     | `*`                                                        |
| `ENABLE_PERFORMANCE_METRICS`  | Enable performance metrics middleware       | `false`                                                    |
| `LOGS_DIR`                    | Directory to store log files                | `logs`                                                     |
| `JWT_SECRET`                  | Secret key for JWT token generation         | `change_this_in_production_very_important`                 |
| `JWT_ALGORITHM`               | Algorithm for JWT token generation          | `HS256`                                                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutes until access token expires          | `30`                                                       |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Days until refresh token expires            | `7`                                                        |

***REMOVED******REMOVED******REMOVED*** Redis Configuration (for Suggestion Engine)

| Variable                       | Description                        | Default |
| ------------------------------ | ---------------------------------- | ------- |
| `REDIS_MAX_CONNECTIONS`        | Maximum Redis connection pool size | `10`    |
| `REDIS_SOCKET_TIMEOUT`         | Redis socket timeout (seconds)     | `30`    |
| `REDIS_SOCKET_CONNECT_TIMEOUT` | Redis connection timeout (seconds) | `30`    |
| `REDIS_RETRY_ON_TIMEOUT`       | Retry on timeout errors            | `true`  |

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** Core Information

- `GET /` - API information and available endpoints
- `GET /debug` - Development debugging information (limited in production)

***REMOVED******REMOVED******REMOVED*** Health Monitoring

- `GET /health` - Comprehensive health check with all dependencies
- `GET /health/live` - Simple liveness check for container orchestrators
- `GET /health/ready` - Readiness check for critical dependencies
- `GET /db-health` - Legacy database-only health check

***REMOVED******REMOVED******REMOVED*** Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Authenticate and get access/refresh tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current authenticated user details
- `POST /api/v1/auth/logout` - Logout and invalidate tokens

***REMOVED******REMOVED******REMOVED*** Users

- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/me/preferences` - Get user preferences
- `PATCH /api/v1/users/me/preferences` - Update user preferences

***REMOVED******REMOVED******REMOVED*** Movies

- `GET /api/v1/movies/` - List movies with pagination and filters
- `GET /api/v1/movies/{movie_id}` - Get details for a specific movie
- `GET /api/v1/movies/search` - Search movies by title, actor, or genre
- `POST /api/v1/movies/{movie_id}/like` - Like a movie
- `POST /api/v1/movies/{movie_id}/watch` - Mark movie as watched
- `POST /api/v1/movies/{movie_id}/watchlist` - Add movie to watchlist

***REMOVED******REMOVED******REMOVED*** Genres & Cast

- `GET /api/v1/genres/` - List all genres
- `GET /api/v1/cast/movie/{movie_id}` - Get cast and crew information

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
***REMOVED*** Run all tests
hatch run test

***REMOVED*** Run tests with coverage
hatch run test-cov

***REMOVED*** Run specific test file
hatch run test tests/test_health_service.py -v
```

***REMOVED******REMOVED******REMOVED*** Code Quality

```bash
***REMOVED*** Run linting and formatting
hatch run lint

***REMOVED*** Format code only
hatch run format
```

***REMOVED******REMOVED******REMOVED*** Development Server

```bash
***REMOVED*** Start with auto-reload
hatch run dev

***REMOVED*** Start with specific port
hatch run dev --port 8080

***REMOVED*** Start with debug logging
LOG_LEVEL=DEBUG hatch run dev
```

***REMOVED******REMOVED*** Architecture Documentation

For detailed information about specific modules:

- **[CLI Module](src/backend_api/cli/README.md)**: Command-line interface documentation
- **[Core Module](src/backend_api/core/README.md)**: Application factory, middleware, and logging
- **[Services Module](src/backend_api/services/README.md)**: Business logic and health monitoring
- **[Routes Module](src/backend_api/routes/README.md)**: HTTP endpoints and API documentation

***REMOVED******REMOVED*** Deployment

***REMOVED******REMOVED******REMOVED*** Production Checklist

1. **Environment Variables**: Set proper production values

   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `JWT_SECRET=<secure-random-string>`
   - `DATABASE_URL=<production-database>`

2. **Database Setup**: Initialize production database

   ```bash
   python -m backend_api.cli db init --create-tables
   python -m backend_api.cli db migrate
   ```

3. **Health Checks**: Configure load balancer health checks

   - Liveness: `/health/live`
   - Readiness: `/health/ready`

4. **Monitoring**: Set up monitoring for health endpoints

   - Monitor `/health` for detailed metrics
   - Alert on service unavailability

5. **Security**: Review security settings
   - CORS origins configured properly
   - JWT secrets are secure
   - Database credentials are secure

***REMOVED******REMOVED******REMOVED*** Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

***REMOVED*** Install dependencies
COPY pyproject.toml ./
RUN pip install hatch
RUN hatch env create

***REMOVED*** Copy application
COPY . .

***REMOVED*** Initialize database
RUN python -m backend_api.cli db init --create-tables

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

***REMOVED*** Run application
CMD ["hatch", "run", "serve"]
```

***REMOVED******REMOVED*** Contributing

1. Follow the modular architecture patterns
2. Add comprehensive tests for new features
3. Update health checks for new dependencies
4. Document new endpoints in route READMEs
5. Ensure backward compatibility for health endpoints
6. Update CLI documentation for new commands
7. Follow CLI best practices with flat, intuitive command structure

***REMOVED******REMOVED*** License

MIT License - see LICENSE file for details.

---

The Next Watch Backend API provides a robust, well-monitored foundation for the movie recommendation platform with comprehensive health monitoring, clean architectural patterns, and a intuitive CLI for operations.
