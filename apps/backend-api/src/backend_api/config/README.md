# Backend API Configuration

This package provides centralized configuration management for the Backend API service, handling database connections, API settings, Redis configuration, and JWT authentication.

> **📦 Migration Notice**: Logging configuration has been moved to the shared NextWatch config library (`config.logging`). This ensures consistent logging setup across all services while eliminating code duplication.

## Overview

The configuration system follows a hierarchical approach where environment variables take precedence over defaults, and supports both development and production environments with appropriate security measures.

## Package Structure

```
config/
├── __init__.py          # Package exports and imports
├── app.py              # Main configuration class and settings
└── README.md           # This documentation
```

**Note**: Logging configuration is now provided by the shared NextWatch config library (`config.logging`) rather than a local module.

## Core Components

### Configuration Class (`app.py`)

The main `Config` class provides a singleton instance with comprehensive settings for:

- **Database**: PostgreSQL connection, pooling, and monitoring
- **API**: Port, CORS, debugging, and performance metrics
- **Redis**: Connection pooling and timeout settings
- **JWT**: Authentication token configuration
- **Security**: Allowed hosts and environment-specific settings
- **Logging**: File and console output configuration

#### Key Features

- **Singleton Pattern**: Ensures consistent configuration across the application
- **Environment-Aware**: Automatically adjusts settings based on `ENVIRONMENT` variable
- **Secure Defaults**: Masks sensitive information in logs and string representations
- **Type Safety**: Comprehensive type hints and validation

### Shared Logging Configuration

Logging is now handled by the shared NextWatch config library (`config.logging`) which provides:

- **Multiple Outputs**: Console (colored) and file (JSON) logging
- **HTTP Noise Suppression**: Configurable verbosity for web framework logs
- **Component-Level Control**: Per-module log level configuration
- **Color Themes**: Multiple visual themes for console output
- **Production Ready**: Automatic fallbacks and error handling
- **Consistent**: Same logging setup across all NextWatch services

## Quick Start

### Basic Usage

```python
from backend_api.config import Config
from config.logging import configure_logging, get_logger

# Get configuration instance
config = Config.get_instance()

# Set up logging (using shared library)
configure_logging(
    log_level=config.log_level,
    log_dir=Path(config.logs_dir) if config.logs_dir else None,
    verbose=config.debug,
    logger_name="backend_api"
)

# Get a logger
logger = get_logger(__name__)

# Use configuration
logger.info("API starting", port=config.api_port)
print(f"Database: {config.database_url}")
```

### Custom Configuration

```python
# Override defaults during initialization
config = Config(
    api_port=8080,
    database_url="postgresql://user:pass@localhost/mydb",
    log_level="DEBUG",
    debug=True
)
```

### Environment-Specific Setup

```python
from backend_api.config import Config
from config.logging import get_logger

# Get configuration instance (automatically loads .env files)
config = Config.get_instance()
logger = get_logger(__name__)

# Check environment
if config.is_production:
    logger.info("Running in production mode", environment=config.environment)
else:
    logger.info("Running in development mode", environment=config.environment)
```

## Environment Variables

### Database Configuration

| Variable                | Default                                                    | Description                       |
| ----------------------- | ---------------------------------------------------------- | --------------------------------- |
| `DATABASE_URL`          | `postgresql://postgres:postgres@localhost:5432/next_watch` | PostgreSQL connection string      |
| `DATABASE_ECHO`         | `false`                                                    | Enable SQL query logging          |
| `DATABASE_POOL_SIZE`    | `5`                                                        | Connection pool size              |
| `DATABASE_MAX_OVERFLOW` | `10`                                                       | Maximum pool overflow             |
| `DATABASE_POOL_TIMEOUT` | `30`                                                       | Pool connection timeout (seconds) |

### API Configuration

| Variable           | Default       | Description                            |
| ------------------ | ------------- | -------------------------------------- |
| `BACKEND_API_PORT` | `8001`        | API server port                        |
| `CORS_ORIGINS`     | `*`           | Allowed CORS origins (comma-separated) |
| `DEBUG`            | `false`       | Enable debug mode                      |
| `ENVIRONMENT`      | `development` | Environment name                       |
| `LOGS_DIR`         | `logs`        | Log directory (disabled in production) |

### Redis Configuration

| Variable                       | Default                    | Description                  |
| ------------------------------ | -------------------------- | ---------------------------- |
| `REDIS_URL`                    | `redis://localhost:6379/0` | Redis connection string      |
| `REDIS_MAX_CONNECTIONS`        | `10`                       | Maximum Redis connections    |
| `REDIS_SOCKET_TIMEOUT`         | `30`                       | Socket timeout (seconds)     |
| `REDIS_SOCKET_CONNECT_TIMEOUT` | `10`                       | Connection timeout (seconds) |
| `REDIS_RETRY_ON_TIMEOUT`       | `true`                     | Retry on timeout             |

### Authentication Configuration

| Variable                      | Default                                    | Description            |
| ----------------------------- | ------------------------------------------ | ---------------------- |
| `JWT_SECRET`                  | `change_this_in_production_very_important` | JWT signing secret     |
| `JWT_ALGORITHM`               | `HS256`                                    | JWT algorithm          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                       | Access token lifetime  |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`                                        | Refresh token lifetime |

### Monitoring & Performance

| Variable                      | Default | Description                          |
| ----------------------------- | ------- | ------------------------------------ |
| `ENABLE_PERFORMANCE_METRICS`  | `false` | Enable performance monitoring        |
| `DATABASE_MONITORING_ENABLED` | `true`  | Enable database monitoring           |
| `SLOW_QUERY_THRESHOLD_MS`     | `100`   | Slow query threshold (ms)            |
| `ENABLE_DB_PROFILING`         | `false` | Enable database profiling (dev only) |

### Logging Configuration

| Variable        | Default   | Description             |
| --------------- | --------- | ----------------------- |
| `LOG_LEVEL`     | `INFO`    | Base logging level      |
| `SQL_LOG_LEVEL` | `WARNING` | SQL query logging level |

## Logging Features

### Advanced Configuration

```python
from pathlib import Path
from config.logging import configure_logging, get_logger

# Comprehensive logging setup (using shared library)
config = configure_logging(
    log_level="DEBUG",
    log_dir=Path("./logs"),
    verbose=True,
    logger_name="backend_api",
    http_verbose=False,  # Suppress HTTP noise
    component_levels={
        "health": "INFO",
        "db": "DEBUG",
        "auth": "WARNING"
    },
    color_theme="solarized"
)

# Get structured logger (using __name__ for hierarchical logging)
logger = get_logger(__name__)
logger.info("Request processed", user_id=123, status_code=200, duration_ms=45)
```

### Color Themes

Available themes for console output:

- **modern**: Bold colors with cyan info, magenta debug
- **classic**: Traditional red/yellow/green scheme
- **minimal**: Subtle styling with bold/dim variations
- **solarized**: Solarized color palette

### Component-Level Logging

Control logging verbosity for different components:

```python
component_levels = {
    "health": "INFO",      # Health checks
    "db": "DEBUG",         # Database operations
    "auth": "WARNING",     # Authentication
    "cache": "ERROR"       # Redis cache operations
}
```

## Production Considerations

### Security

- JWT secrets are masked in logs and string representations
- Database passwords are automatically masked in URLs
- Sensitive configuration is not exposed in error messages

### Performance

- File logging is disabled in production by default
- HTTP access logs are suppressed unless explicitly enabled
- Connection pooling is optimized for production workloads

### Environment Files

Create these files in your project root:

```bash
# .env - Default values (committed to git)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/next_watch
LOG_LEVEL=INFO
DEBUG=false

# .env.local - Local overrides (git-ignored)
DATABASE_URL=postgresql://myuser:mypass@localhost:5432/mydb
DEBUG=true
JWT_SECRET=my-local-secret
```

## Integration Examples

### FastAPI Application

```python
from fastapi import FastAPI
from backend_api.config import Config
from config.logging import configure_logging, get_logger

# Initialize configuration and logging
config = Config.get_instance()
configure_logging(
    log_level=config.log_level,
    log_dir=Path(config.logs_dir) if config.logs_dir else None,
    logger_name="backend_api"
)

app = FastAPI(debug=config.debug)
logger = get_logger(__name__)

@app.on_event("startup")
async def startup():
    logger.info("Application starting", environment=config.environment, port=config.api_port)
```

### Database Connection

```python
from sqlalchemy import create_engine
from backend_api.config import Config

config = Config.get_instance()
engine = create_engine(
    config.database_url,
    echo=config.database_echo,
    pool_size=config.database_pool_size,
    max_overflow=config.database_max_overflow,
    pool_timeout=config.database_pool_timeout
)
```

### Redis Connection

```python
import redis
from backend_api.config import Config

config = Config.get_instance()
redis_client = redis.from_url(
    config.redis_url,
    max_connections=config.redis_max_connections,
    socket_timeout=config.redis_socket_timeout,
    socket_connect_timeout=config.redis_socket_connect_timeout,
    retry_on_timeout=config.redis_retry_on_timeout
)
```

## Error Handling

The configuration system includes comprehensive error handling:

- **Missing Required Variables**: Clear error messages with setup instructions
- **Invalid Values**: Type conversion errors with helpful suggestions
- **File Permissions**: Graceful fallback for log file creation issues
- **Missing Dependencies**: Optional dependency handling (e.g., python-dotenv)

## Testing

For testing, you can override configuration:

```python
import pytest
from backend_api.config import Config

@pytest.fixture
def test_config():
    return Config(
        database_url="sqlite:///:memory:",
        redis_url="redis://localhost:6379/1",  # Test database
        log_level="DEBUG",
        debug=True
    )
```

## Best Practices

1. **Always use environment variables** for sensitive configuration
2. **Set up logging early** in your application lifecycle
3. **Use structured logging** with meaningful context
4. **Monitor slow queries** in production with appropriate thresholds
5. **Keep .env.local** out of version control
6. **Use different Redis databases** for different environments
7. **Enable metrics** for production monitoring
