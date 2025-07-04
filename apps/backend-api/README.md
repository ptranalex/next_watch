***REMOVED*** Next Watch Backend API

> A production-ready FastAPI backend service for the Next Watch movie recommendation platform, featuring clean architecture, comprehensive health monitoring, and robust CLI tooling.

***REMOVED******REMOVED*** 🚀 Quick Start

Get up and running in minutes:

```bash
***REMOVED*** 1. Clone and navigate to the project
git clone https://github.com/yourusername/next_watch.git
cd next_watch/apps/backend-api

***REMOVED*** 2. Install dependencies
hatch env create

***REMOVED*** 3. Configure environment (copy .env.example to .env and customize)
cp .env.example .env

***REMOVED*** 4. Initialize database
hatch run migrate

***REMOVED*** 5. Start development server
hatch run dev
```

🎉 **Your API is now running at** `http://localhost:8000`

***REMOVED******REMOVED******REMOVED*** Prerequisites

- **Python 3.10+**
- **Hatch** for dependency management
- **PostgreSQL** database
- **Redis** server (optional, for caching and recommendations)

***REMOVED******REMOVED*** 📋 Table of Contents

- [Features](***REMOVED***-features)
- [Architecture](***REMOVED***-architecture)
- [Health Monitoring](***REMOVED***-health-monitoring)
- [API Reference](***REMOVED***-api-reference)
- [CLI Reference](***REMOVED***-cli-reference)
- [Configuration](***REMOVED***-configuration)
- [Database Setup](***REMOVED***-database-setup)
- [Development](***REMOVED***-development)
- [Docker Deployment](***REMOVED***-docker-deployment)
- [Contributing](***REMOVED***-contributing)

***REMOVED******REMOVED*** ✨ Features

***REMOVED******REMOVED******REMOVED*** 🎬 Core Functionality

- **Movie Database API** - Advanced search, filtering, and metadata
- **User Management** - Authentication, profiles, and preferences
- **Social Features** - Watchlists, ratings, and user interactions
- **Recommendation Engine** - Redis-powered suggestions
- **Content Discovery** - Genre browsing and cast information

***REMOVED******REMOVED******REMOVED*** 🏥 Health & Monitoring

- **Multi-Service Health Checks** - PostgreSQL and Redis monitoring
- **Three-Tier Health Endpoints** - Comprehensive, liveness, and readiness
- **Container Orchestration Ready** - Kubernetes and Docker health probes
- **Performance Metrics** - Response times and connection status
- **Graceful Degradation** - Continues operation with partial service failures

***REMOVED******REMOVED******REMOVED*** 🚀 Production Ready

- **Fast Core Integration** - Standardized FastAPI patterns and middleware
- **Service Client Factory** - Efficient inter-service communication
- **Rate Limiting** - Built-in endpoint protection with configurable limits
- **Security Headers** - Production-ready HSTS, CSP, and XSS protection
- **Structured Logging** - Comprehensive, searchable logs with request tracking
- **Performance Monitoring** - Request timing and metrics
- **Security First** - JWT authentication, CORS, input validation
- **Global Error Handling** - Detailed error reporting with proper status codes
- **Environment Awareness** - Development, staging, and production configurations

***REMOVED******REMOVED*** 🏗 Architecture

Built with modern FastAPI best practices and clean architecture principles:

```
backend-api/
├── src/backend_api/
│   ├── 🏭 core/                ***REMOVED*** Application factory and core components
│   │   ├── app.py             ***REMOVED*** FastAPI app factory with lifespan management
│   │   ├── middleware.py      ***REMOVED*** CORS, error handling, performance monitoring
│   │   └── logging.py         ***REMOVED*** Logging configuration wrapper
│   ├── 🛣 routes/             ***REMOVED*** HTTP endpoints organized by function
│   │   ├── api_v1/            ***REMOVED*** Versioned API routes (main business logic)
│   │   ├── health.py          ***REMOVED*** Comprehensive health check endpoints
│   │   └── meta.py            ***REMOVED*** Root and debug endpoints
│   ├── 🎯 services/           ***REMOVED*** Business logic and service classes
│   │   ├── health_service.py  ***REMOVED*** Multi-service health monitoring
│   │   ├── movie_service.py   ***REMOVED*** Movie-related operations
│   │   ├── user_interaction.py ***REMOVED*** User interactions and social features
│   │   ├── suggestion_engine.py ***REMOVED*** Redis-based recommendations
│   │   └── auth.py            ***REMOVED*** Authentication and authorization
│   ├── ⚙️ config/             ***REMOVED*** Configuration management
│   │   ├── app.py             ***REMOVED*** Application settings and environment variables
│   │   └── logging.py         ***REMOVED*** Centralized logging configuration
│   ├── 🗄 db/                 ***REMOVED*** Database models and connections
│   ├── 📊 queries/            ***REMOVED*** Database query operations
│   ├── 📋 schemas/            ***REMOVED*** Pydantic schemas for API contracts
│   ├── 💻 cli/                ***REMOVED*** Command-line interface
│   │   ├── commands/          ***REMOVED*** CLI command implementations
│   │   └── __init__.py        ***REMOVED*** CLI application setup
│   └── main.py                ***REMOVED*** Clean application entry point
└── 📖 README.md               ***REMOVED*** This file
```

***REMOVED******REMOVED******REMOVED*** 🎯 Key Architectural Benefits

- **🏭 Application Factory Pattern** - Clean app creation with dependency injection
- **🏥 Health Service Integration** - Comprehensive dependency monitoring
- **🧩 Modular Design** - Well-organized, testable components
- **🛡 Graceful Degradation** - Robust error handling and fallback mechanisms
- **🔄 Clean Separation** - Clear distinction between routes, services, and configuration
- **💻 Comprehensive CLI** - Full-featured command-line interface

***REMOVED******REMOVED*** 🏥 Health Monitoring

Comprehensive health monitoring with three specialized endpoints designed for different use cases:

***REMOVED******REMOVED******REMOVED*** 🔍 Health Check Endpoints

***REMOVED******REMOVED******REMOVED******REMOVED*** 📊 Comprehensive Health Check (`/health`)

**Purpose**: Full system diagnostics with detailed metrics

```bash
curl http://localhost:8000/health | jq .
```

<details>
<summary>📋 Example Response</summary>

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

</details>

***REMOVED******REMOVED******REMOVED******REMOVED*** 💓 Liveness Check (`/health/live`)

**Purpose**: Container/process liveness verification

- Always returns 200 if service is running
- For Kubernetes liveness probes and Docker healthchecks

***REMOVED******REMOVED******REMOVED******REMOVED*** ⚡ Readiness Check (`/health/ready`)

**Purpose**: Traffic readiness verification

- Checks critical services only (PostgreSQL)
- For load balancer readiness probes

***REMOVED******REMOVED******REMOVED*** 🐳 Container Integration

<details>
<summary>🚢 Kubernetes Configuration</summary>

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

</details>

<details>
<summary>🐳 Docker Compose Configuration</summary>

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

</details>

***REMOVED******REMOVED*** 🏗 API Reference

***REMOVED******REMOVED******REMOVED*** 🔧 Core Information

- `GET /` - API information and available endpoints
- `GET /debug` - Development debugging information (limited in production)

***REMOVED******REMOVED******REMOVED*** 🏥 Health Monitoring

- `GET /health` - Comprehensive health check with all dependencies
- `GET /health/live` - Simple liveness check for container orchestrators
- `GET /health/ready` - Readiness check for critical dependencies
- `GET /db-health` - Legacy database-only health check

***REMOVED******REMOVED******REMOVED*** 🔐 Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Authenticate and get access/refresh tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current authenticated user details
- `POST /api/v1/auth/logout` - Logout and invalidate tokens

***REMOVED******REMOVED******REMOVED*** 👤 Users

- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/me/preferences` - Get user preferences
- `PATCH /api/v1/users/me/preferences` - Update user preferences

***REMOVED******REMOVED******REMOVED*** 🎬 Movies

- `GET /api/v1/movies/` - List movies with pagination and filters
- `GET /api/v1/movies/{movie_id}` - Get details for a specific movie
- `GET /api/v1/movies/search` - Search movies by title, actor, or genre
- `POST /api/v1/movies/{movie_id}/like` - Like a movie
- `POST /api/v1/movies/{movie_id}/watch` - Mark movie as watched
- `POST /api/v1/movies/{movie_id}/watchlist` - Add movie to watchlist

***REMOVED******REMOVED******REMOVED*** 🎭 Genres & Cast

- `GET /api/v1/genres/` - List all genres
- `GET /api/v1/cast/movie/{movie_id}` - Get cast and crew information

***REMOVED******REMOVED*** 💻 CLI Reference

Comprehensive command-line interface with intuitive, flat command structure:

***REMOVED******REMOVED******REMOVED*** 🚀 Server Management

```bash
***REMOVED*** Development server with auto-reload
hatch run dev

***REMOVED*** Production server
python -m backend_api.cli serve

***REMOVED*** Custom server options
python -m backend_api.cli serve --host 0.0.0.0 --port 8080 --reload
```

***REMOVED******REMOVED******REMOVED*** 🗄 Database Management

```bash
***REMOVED*** Initialize database
python -m backend_api.cli db init
python -m backend_api.cli db init --create-tables

***REMOVED*** Run migrations
python -m backend_api.cli db migrate
hatch run migrate  ***REMOVED*** Shortcut

***REMOVED*** Downgrade migrations
python -m backend_api.cli db downgrade
python -m backend_api.cli db downgrade --steps 3
python -m backend_api.cli db downgrade --target 005_add_ratings_and_awards

***REMOVED*** Development teardown
python -m backend_api.cli db teardown --confirm
```

***REMOVED******REMOVED******REMOVED*** 🏥 Health Checks

```bash
***REMOVED*** System health overview
python -m backend_api.cli health

***REMOVED*** Check specific services
python -m backend_api.cli health redis
python -m backend_api.cli health db
```

***REMOVED******REMOVED******REMOVED*** 🗂 Cache Management

```bash
***REMOVED*** Cache information
python -m backend_api.cli cache info

***REMOVED*** Key management
python -m backend_api.cli cache keys --pattern "user:*"
python -m backend_api.cli cache get "movie:123"
python -m backend_api.cli cache delete "session:456" --confirm
python -m backend_api.cli cache clear --pattern "temp:*" --confirm
```

***REMOVED******REMOVED******REMOVED*** ⚙️ Configuration & System

```bash
***REMOVED*** Display configuration
python -m backend_api.cli config
python -m backend_api.cli config --verbose

***REMOVED*** Version information
python -m backend_api.cli version
```

***REMOVED******REMOVED******REMOVED*** 🎯 Hatch Shortcuts

```bash
***REMOVED*** Database operations
hatch run migrate, hatch run db-init, hatch run db-init-tables

***REMOVED*** Health checks
hatch run health, hatch run health-redis, hatch run health-db

***REMOVED*** Cache operations
hatch run cache-info, hatch run cache-keys, hatch run cache-clear

***REMOVED*** System commands
hatch run config, hatch run version
```

***REMOVED******REMOVED*** ⚙️ Configuration

Environment-aware configuration system with secure defaults:

***REMOVED******REMOVED******REMOVED*** 🔧 Core Settings

| Variable                     | Description                                 | Default                                                    |
| ---------------------------- | ------------------------------------------- | ---------------------------------------------------------- |
| `DATABASE_URL`               | PostgreSQL connection string                | `postgresql://postgres:postgres@localhost:5432/next_watch` |
| `REDIS_URL`                  | Redis connection URL                        | `redis://localhost:6379/0`                                 |
| `API_PORT`                   | Port for the API server                     | `8000`                                                     |
| `LOG_LEVEL`                  | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO`                                                     |
| `DEBUG`                      | Enable debug mode                           | `false`                                                    |
| `CORS_ORIGINS`               | Comma-separated list of allowed origins     | `*`                                                        |
| `ENABLE_PERFORMANCE_METRICS` | Enable performance metrics middleware       | `false`                                                    |
| `LOGS_DIR`                   | Directory to store log files                | `logs`                                                     |

***REMOVED******REMOVED******REMOVED*** 🔐 Security Settings

| Variable                      | Description                         | Default                                    |
| ----------------------------- | ----------------------------------- | ------------------------------------------ |
| `JWT_SECRET`                  | Secret key for JWT token generation | `change_this_in_production_very_important` |
| `JWT_ALGORITHM`               | Algorithm for JWT token generation  | `HS256`                                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutes until access token expires  | `30`                                       |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Days until refresh token expires    | `7`                                        |

***REMOVED******REMOVED******REMOVED*** 🚀 Performance Settings

| Variable                       | Description                        | Default |
| ------------------------------ | ---------------------------------- | ------- |
| `REDIS_MAX_CONNECTIONS`        | Maximum Redis connection pool size | `10`    |
| `REDIS_SOCKET_TIMEOUT`         | Redis socket timeout (seconds)     | `30`    |
| `REDIS_SOCKET_CONNECT_TIMEOUT` | Redis connection timeout (seconds) | `30`    |
| `REDIS_RETRY_ON_TIMEOUT`       | Retry on timeout errors            | `true`  |

***REMOVED******REMOVED******REMOVED*** 🔍 Development Settings

| Variable                               | Description                             | Default |
| -------------------------------------- | --------------------------------------- | ------- |
| `ENABLE_DB_PROFILING`                  | Enable database query profiling         | `false` |
| `DB_PROFILING_SLOW_QUERY_THRESHOLD_MS` | Threshold for slow query detection (ms) | `100`   |

> ⚠️ **Note**: Database profiling is automatically disabled in production environments for security and performance.

***REMOVED******REMOVED*** 🗄 Database Setup

***REMOVED******REMOVED******REMOVED*** ⚡ Quick Setup

```bash
***REMOVED*** Complete database setup with migrations
python -m backend_api.scripts.setup_db setup-storage
```

***REMOVED******REMOVED******REMOVED*** 🔧 Manual Setup

```bash
***REMOVED*** 1. Initialize database connection only
python -m backend_api.scripts.setup_db initialize-db

***REMOVED*** 2. Run migrations to create tables
python -m backend_api.scripts.setup_db run-migrations
```

***REMOVED******REMOVED******REMOVED*** 📊 Migration Commands

```bash
***REMOVED*** Run all pending migrations
python -m backend_api.scripts.setup_db run-migrations

***REMOVED*** Check database schema status
python -m backend_api.scripts.setup_db check-schema

***REMOVED*** Profile database queries (development)
python -m backend_api.scripts.setup_db profile-db --duration 30
```

> ⚠️ **Important**: The application no longer creates database tables automatically at startup. You must run migrations manually to set up the database schema.

***REMOVED******REMOVED*** 🛠 Development

***REMOVED******REMOVED******REMOVED*** 🧪 Testing

```bash
***REMOVED*** Run all tests
hatch run test

***REMOVED*** Run tests with coverage
hatch run test-cov

***REMOVED*** Run specific test file
hatch run test tests/test_health_service.py -v
```

***REMOVED******REMOVED******REMOVED*** 🎨 Code Quality

```bash
***REMOVED*** Run linting and formatting
hatch run lint

***REMOVED*** Format code only
hatch run format
```

***REMOVED******REMOVED******REMOVED*** 🚀 Development Server

```bash
***REMOVED*** Start with auto-reload
hatch run dev

***REMOVED*** Start with specific port
hatch run dev --port 8080

***REMOVED*** Start with debug logging
LOG_LEVEL=DEBUG hatch run dev
```

***REMOVED******REMOVED*** 🐳 Docker Deployment

***REMOVED******REMOVED******REMOVED*** 🚀 Production Deployment

```bash
***REMOVED*** Build from monorepo root
docker build -f apps/backend-api/Dockerfile -t backend-api .

***REMOVED*** Run container
docker run -p 8000:8000 backend-api
```

***REMOVED******REMOVED******REMOVED*** 📋 Production Checklist

1. **🔧 Environment Variables**

   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `JWT_SECRET=<secure-random-string>`
   - `DATABASE_URL=<production-database>`

2. **🗄 Database Setup**

   ```bash
   python -m backend_api.scripts.setup_db run-migrations
   ```

3. **🏥 Health Checks**

   - Configure liveness: `/health/live`
   - Configure readiness: `/health/ready`

4. **📊 Monitoring**

   - Monitor `/health` for detailed metrics
   - Set up alerts for service unavailability

5. **🔒 Security**
   - Configure proper CORS origins
   - Use secure JWT secrets
   - Protect database credentials

***REMOVED******REMOVED*** 📚 Architecture Documentation

For detailed information about specific modules:

- **[CLI Module](src/backend_api/cli/README.md)** - Command-line interface documentation
- **[Core Module](src/backend_api/core/README.md)** - Application factory, middleware, and logging
- **[Services Module](src/backend_api/services/README.md)** - Business logic and health monitoring
- **[Routes Module](src/backend_api/routes/README.md)** - HTTP endpoints and API documentation

***REMOVED******REMOVED*** 🤝 Contributing

1. **🏗 Architecture** - Follow modular architecture patterns
2. **🧪 Testing** - Add comprehensive tests for new features
3. **🏥 Health Checks** - Update health checks for new dependencies
4. **📖 Documentation** - Document new endpoints in route READMEs
5. **🔄 Compatibility** - Ensure backward compatibility for health endpoints
6. **💻 CLI** - Update CLI documentation for new commands
7. **🎯 Best Practices** - Follow CLI best practices with flat, intuitive structure

***REMOVED******REMOVED*** 📄 License

MIT License - see LICENSE file for details.

---

**The Next Watch Backend API** provides a robust, production-ready foundation for the movie recommendation platform with comprehensive health monitoring, clean architectural patterns, and intuitive CLI operations. 🎬✨

---
