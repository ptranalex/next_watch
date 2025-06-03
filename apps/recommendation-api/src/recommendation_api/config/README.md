***REMOVED*** Configuration Module

This module manages all configuration settings for the Recommendation API service.

***REMOVED******REMOVED*** Overview

The configuration system provides:

- Environment-based configuration loading
- Type-safe configuration classes
- Logging configuration
- Centralized settings management

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** `app.py`

The main configuration module that defines:

- `Config` class with all application settings
- Default values for all settings
- Environment variable mapping
- Type validation

The settings are loaded with this hierarchy:

1. Environment variables (highest priority)
2. `.env` file in project root
3. Default values (lowest priority)

***REMOVED******REMOVED******REMOVED*** `logging.py`

Configures the application's logging system:

- Sets up formatters and handlers
- Configures log levels based on settings
- Provides a `configure_logging()` function for CLI commands
- Handles log file outputs and rotation

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Accessing Configuration

```python
from recommendation_api.config import settings

***REMOVED*** Use settings directly
database_url = settings.database_url
host = settings.host
port = settings.port
```

***REMOVED******REMOVED******REMOVED*** Environment Variables

Key configuration settings can be overridden with environment variables:

| Setting         | Environment Variable | Default                                                            |
| --------------- | -------------------- | ------------------------------------------------------------------ |
| Host            | `HOST`               | `0.0.0.0`                                                          |
| Port            | `PORT`               | `8000`                                                             |
| Log Level       | `LOG_LEVEL`          | `INFO`                                                             |
| Database URL    | `DATABASE_URL`       | `postgresql://postgres:postgres@localhost:5432/recommendation_api` |
| Qdrant URL      | `QDRANT_URL`         | `http://localhost:6333`                                            |
| Embedding Model | `EMBEDDING_MODEL`    | `all-MiniLM-L6-v2`                                                 |

***REMOVED******REMOVED******REMOVED*** Configuring Logging

```python
from recommendation_api.config.logging import configure_logging

***REMOVED*** Basic configuration
configure_logging()

***REMOVED*** Custom configuration
configure_logging(log_level="DEBUG", verbose=True)
```

***REMOVED******REMOVED*** Environment Support

The configuration system supports multiple environments:

- `development` (default): Development settings with detailed logging
- `production`: Production-optimized settings
- `test`: Settings for test environment

Set the environment with the `ENVIRONMENT` environment variable.

***REMOVED******REMOVED*** Extending Configuration

To add new configuration options:

1. Add the property to the `Config` class in `app.py`
2. Set a default value
3. Add appropriate type annotations
4. Add environment variable mapping if needed
