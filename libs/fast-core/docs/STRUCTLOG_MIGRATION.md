# Structlog Migration Guide

This document describes the migration from `config.logging` to `structlog` in the Fast Core library.

## Overview

Fast Core has been updated to use `structlog` for all logging operations, eliminating the dependency on `config.logging.get_logger`. This change provides:

- **Structured logging**: All log entries include contextual data as structured fields
- **Better performance**: More efficient logging with lazy evaluation
- **Improved debugging**: Request-scoped loggers with automatic context binding
- **JSON output**: Configurable output formats including JSON for better log aggregation
- **Reduced dependencies**: No longer depends on the `config` package for logging

## Changes Made

### Dependencies

Added `structlog>=23.1.0` to the project dependencies in `pyproject.toml`.

### Updated Files

The following files were updated to use `structlog` instead of `config.logging`:

1. **`src/fast_core/app.py`**

   - Replaced `from config.logging import get_logger` with `import structlog`
   - Updated logger initialization to `logger = structlog.get_logger(__name__)`

2. **`src/fast_core/middleware/logging.py`**

   - Replaced `from config.logging import get_logger` with `import structlog`
   - Updated logger initialization and `get_request_logger` function
   - The middleware now uses structured logging with proper context binding

3. **`src/fast_core/middleware/cors.py`**

   - Replaced `from config.logging import get_logger` with `import structlog`
   - Updated logger initialization

4. **`src/fast_core/middleware/security.py`**

   - Replaced `from config.logging import get_logger` with `import structlog`
   - Updated logger initialization

5. **`src/fast_core/middleware/setup.py`**

   - Replaced `import logging` with `import structlog`
   - Updated logging calls to use structured logging methods
   - Fixed log level handling for structlog API

6. **`src/fast_core/monitoring/health.py`**
   - Replaced `from config.logging import get_logger` with `import structlog`
   - Updated logger initialization

## Migration for Applications Using Fast Core

### Before (using config.logging)

```python
from config.logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("User logged in")

# With context (manual string formatting)
logger.info(f"User {user_id} logged in from {ip_address}")
```

### After (using structlog)

```python
import structlog

logger = structlog.get_logger(__name__)

# Basic logging
logger.info("User logged in")

# With structured context
logger.info("User logged in", user_id=user_id, ip_address=ip_address)
```

### Configuration

Applications should configure structlog at startup. Here's a recommended configuration:

```python
import structlog

# Configure structlog for your application
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # Use JSONRenderer for production, ConsoleRenderer for development
        structlog.processors.JSONRenderer()  # or structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Request-Scoped Logging

Fast Core provides a `get_request_logger` function that returns a logger bound with request context:

```python
from fastapi import Request
from fast_core.middleware.logging import get_request_logger

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, request: Request):
    # Get logger with request context (request_id, method, path, client)
    logger = get_request_logger(request)

    logger.info("Processing user request", user_id=user_id)

    # ... process request ...

    logger.info("User request completed", user_id=user_id, status="success")
```

## Benefits

### Structured Data

Instead of string interpolation:

```python
logger.info(f"User {user_id} performed action {action} at {timestamp}")
```

Use structured fields:

```python
logger.info("User action performed",
           user_id=user_id,
           action=action,
           timestamp=timestamp)
```

### Automatic Context

Request-scoped loggers automatically include:

- `request_id`: Unique identifier for the request
- `method`: HTTP method (GET, POST, etc.)
- `path`: Request path
- `client`: Client IP address

### JSON Output

With JSON formatting, logs are easily parsed by log aggregation systems:

```json
{
  "event": "User action performed",
  "user_id": 123,
  "action": "login",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req-abc123",
  "method": "POST",
  "path": "/api/auth/login",
  "client": "192.168.1.100",
  "logger": "myapp.auth",
  "level": "info"
}
```

## Best Practices

### Log Output Quality

The improved middleware now produces cleaner, more actionable logs:

**Before:**

```
2025-06-22T06:08:35.606719Z [debug] Response [fast_core.middleware.setup]
method=GET path=/bff/v1/movies/3566 process_time=0.0238s request_body=
request_headers={'host': 'localhost:8001', 'connection': 'keep-alive',
'sec-ch-ua-platform': '"macOS"', 'user-agent': 'Mozilla/5.0...',
'accept': 'application/json, text/plain, */*', 'sec-ch-ua': '"Not.A/Brand"...',
'dnt': '1', 'sec-ch-ua-mobile': '?0', 'origin': 'http://localhost:3000',
'sec-fetch-site': 'same-site', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty',
'referer': 'http://localhost:3000/', 'accept-encoding': 'gzip, deflate, br, zstd',
'accept-language': 'en-US,en;q=0.9,vi;q=0.8'} status_code=200
url=http://localhost:8001/bff/v1/movies/3566 user_agent='Mozilla/5.0...'
```

**After:**

```
2025-06-22T06:08:35.606719Z [info] Request completed [fast_core.middleware.setup]
request_id=abc123-def456 method=GET path=/bff/v1/movies/3566 status_code=200
process_time_ms=23.8 client_ip=192.168.1.100 user_agent='Mozilla/5.0...'
headers={'host': 'localhost:8001', 'accept': 'application/json', 'origin': 'http://localhost:3000'}
```

### Key Improvements

1. **Request Correlation**: Every request has a unique `request_id` for tracing
2. **Reduced Noise**: Filters out browser fingerprinting headers and redundant data
3. **Better Metrics**: Process time in milliseconds, response size when available
4. **Smart Log Levels**: 5xx = ERROR, 4xx = WARNING, 2xx/3xx = INFO/DEBUG
5. **Essential Headers Only**: Keeps business-relevant headers, removes noise
6. **No Duplication**: User-agent logged once, not in headers and separately

### Recommended Configuration

```python
# Production configuration
middleware.logging(
    level="INFO",
    include_request_body=False,  # Disable for performance/privacy
    include_response_body=False,
    log_timing=True,
    include_headers=True,  # Now filtered automatically
    exclude_paths=["/health", "/metrics", "/docs"],
    exclude_headers=["authorization", "cookie", "x-api-key"]
)
```

## Example Application

See `examples/structlog_usage.py` for a complete example of using structlog with Fast Core.

## Breaking Changes

1. **No automatic logger configuration**: Applications must configure structlog themselves
2. **Different API**: Use keyword arguments for context instead of string formatting
3. **Import changes**: Import `structlog` instead of `config.logging.get_logger`

## Recommendations

1. **Configure structlog early**: Set up structlog configuration in your application's startup code
2. **Use structured logging**: Pass context as keyword arguments rather than string formatting
3. **Leverage request context**: Use `get_request_logger` for request-scoped logging
4. **Choose appropriate output format**: Use `JSONRenderer` for production, `ConsoleRenderer` for development
5. **Include relevant context**: Add business-relevant fields to your log entries

## Backward Compatibility

This is a breaking change. Applications using Fast Core will need to:

1. Install `structlog` as a dependency
2. Update their logging imports and configuration
3. Optionally update their logging calls to use structured format

The change eliminates the dependency on the `config` package for logging, making Fast Core more self-contained and flexible.
