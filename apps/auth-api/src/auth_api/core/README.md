# Auth API Core Module

This directory contains the core components for the Authentication API application, following a modular architecture pattern similar to the recommendation-api.

## Structure

```
auth_api/core/
├── __init__.py          # Module exports
├── app.py              # FastAPI application factory
├── logging.py          # Logging configuration
├── middleware.py       # Middleware setup
└── README.md           # This file
```

## Components

### `app.py` - Application Factory

- **`create_app()`**: Main factory function that creates and configures the FastAPI application
- **`lifespan()`**: Application lifespan manager for startup/shutdown logic
- **`global_exception_handler()`**: Global exception handling for unhandled errors

### `middleware.py` - Middleware Configuration

- **`setup_middleware()`**: Configures all middleware including CORS and TrustedHost
- Handles production-specific middleware configuration
- Centralizes middleware logic for better maintainability

### `logging.py` - Logging Setup

- **`setup_logging()`**: Initializes application logging using the config module
- Uses the comprehensive logging configuration from `auth_api.config.logging`
- Ensures consistent logging across the application

## Usage

The core module is designed to be imported and used in `main.py`:

```python
from auth_api.core import create_app
from auth_api.core.logging import setup_logging

# Setup logging first
setup_logging()

# Create the application
app = create_app()
```

## Benefits

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easy to modify individual components without affecting others
3. **Testability**: Components can be tested in isolation
4. **Consistency**: Follows the same pattern as other services in the platform
5. **Clean Architecture**: Clear boundaries between configuration, middleware, and application logic

## Dependencies

- `fastapi`: Web framework
- `auth_api.config`: Configuration management
- `auth_api.routes`: Route definitions
- `auth_api.db`: Database operations
