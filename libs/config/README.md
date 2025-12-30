# NextWatch Configuration Library

A simplified, straightforward configuration library for NextWatch microservices.

## Overview

This library provides a standardized way to manage configuration across NextWatch services with a focus on simplicity and ease of use. It includes:

- Base configuration classes for different service types
- Environment variable loading and validation
- Configuration profiles for different deployment scenarios
- Utilities for secure handling of sensitive configuration

## Key Features

- **Simple inheritance model**: Clear base classes with minimal inheritance depth
- **Environment-based configuration**: Easy loading from environment variables
- **Configuration profiles**: Predefined settings for different service types and environments
- **Validation**: Built-in validation for configuration values
- **Security**: Automatic masking of sensitive information and production safeguards

## Usage

### Basic Service Configuration

```python
from config.base.config import ServiceConfig

class MyServiceConfig(ServiceConfig):
    # Service-specific configuration
    api_key: str
    feature_flag_enabled: bool = False

    class Config:
        env_prefix = "MY_SERVICE_"  # Environment variables will be prefixed with MY_SERVICE_
```

### Adding Cache Support

```python
from config.base.config import ServiceConfig
from config.services.cache import CacheConfigMixin

class MyCachedServiceConfig(ServiceConfig, CacheConfigMixin):
    # Service-specific configuration
    cache_enabled: bool = True
```

### Using Configuration Profiles

```python
from config.base.config import ServiceConfig
from config.profiles.service_profiles import apply_profiles, GatewayProfile, DevelopmentProfile

# Create config instance
config = MyServiceConfig()

# Apply profiles
apply_profiles(config, GatewayProfile, DevelopmentProfile)
```

## Configuration Mixins

The library provides several mixins for common functionality:

- **CacheConfigMixin**: Redis cache configuration
- **DatabaseConfigMixin**: Database connection configuration
- **AuthConfigMixin**: JWT authentication configuration
- **MonitoringConfigMixin**: Monitoring and observability configuration

## Configuration Profiles

Predefined profiles for different service types and environments:

- **Development/Test/Production**: Environment-specific settings
- **ApiService/Gateway/Backend/Worker**: Service type-specific settings
- **LowResource/HighPerformance**: Resource allocation profiles

## Best Practices

1. **Keep it simple**: Avoid deep inheritance hierarchies
2. **Validate early**: Use validators to catch configuration errors at startup
3. **Secure by default**: Always mask sensitive information in logs
4. **Use profiles**: Apply appropriate profiles for your service type
5. **Log configuration**: Always log configuration summary at startup
6. **Validate production**: Use `validate_production_settings()` before deploying

## Implementation Notes

The library has been simplified from its previous version to:

- Remove unnecessary caching mechanisms
- Simplify the inheritance model
- Make configuration more straightforward
- Reduce complexity in profiles and mixins
- Improve error messages and validation

## Installation

```bash
# Install as a local dependency in your service
pip install -e ../../libs/config
```

## Quick Start

```python
from config.base.config import ServiceConfig
from config.services.database import DatabaseConfigMixin
from config.services.cache import CacheConfigMixin

class MyServiceConfig(ServiceConfig, DatabaseConfigMixin, CacheConfigMixin):
    """Custom service configuration."""

    # Service-specific settings
    api_port: int = 8000
    feature_flag: bool = True

# Create and use configuration
config = MyServiceConfig()
print(f"Database URL: {config.get_masked_database_url()}")
print(f"Cache URL: {config.get_masked_cache_url()}")
```

## Architecture

### Base Configuration Classes

- **`BaseConfig`**: Abstract base with core configuration functionality
- **`ServiceConfig`**: For HTTP services (FastAPI, Flask, etc.)
- **`WorkerConfig`**: For background workers and batch jobs

### Service Mixins

- **`DatabaseConfigMixin`**: PostgreSQL configuration with connection pooling
- **`CacheConfigMixin`**: Redis configuration with TTL management
- **`AuthConfigMixin`**: JWT authentication configuration
- **`MonitoringConfigMixin`**: Observability (logging, metrics, tracing)
- **`VectorDBConfigMixin`**: Qdrant vector database configuration

### Environment Management

- **Hierarchical Loading**: `.env` → `.env.local` → `.env.{environment}` → system environment
- **Type-Safe Parsing**: Automatic type conversion with validation
- **Project Root Detection**: Automatic discovery of project configuration files

## Usage Examples

### Basic Service Configuration

```python
from config.base.config import ServiceConfig
from config.services.database import DatabaseConfigMixin
from config.services.auth import AuthConfigMixin

class APIConfig(ServiceConfig, DatabaseConfigMixin, AuthConfigMixin):
    """API service configuration."""

    # Service-specific settings
    api_port: int = 8001
    cors_origins: List[str] = ["*"]

    def validate_production_config(self) -> List[str]:
        """Custom production validation."""
        errors = super().validate_production_config()

        if self.environment == "production" and "*" in self.cors_origins:
            errors.append("CORS origins should not include '*' in production")

        return errors

# Usage
config = APIConfig()

# Validate for production
if config.environment == "production":
    errors = config.validate_production_config()
    if errors:
        raise ValueError(f"Production config errors: {errors}")
```

### Environment Variables

The library supports environment variables with service-specific prefixes:

```bash
# Core settings
ENVIRONMENT=production
SERVICE_NAME=my-api
SERVICE_VERSION=1.0.0

# Database settings
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Cache settings
CACHE_URL=redis://host:6379/0
CACHE_DEFAULT_TTL=3600
CACHE_MAX_CONNECTIONS=10

# Auth settings
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monitoring settings
LOG_LEVEL=INFO
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=30
```

## Development Status

### Phase 1: Core Infrastructure ✅ COMPLETE

- [x] Base configuration classes (`BaseConfig`, `ServiceConfig`, `WorkerConfig`)
- [x] Environment variable loading with hierarchical `.env` support
- [x] Security utilities (masking, validation)
- [x] Package structure and build configuration

### Phase 2: Service Mixins ✅ COMPLETE

- [x] **DatabaseConfigMixin**: PostgreSQL with connection pooling
- [x] **CacheConfigMixin**: Redis with TTL management
- [x] **AuthConfigMixin**: JWT authentication
- [x] **MonitoringConfigMixin**: Logging, metrics, tracing
- [x] **VectorDBConfigMixin**: Qdrant vector database

### Phase 3: Service Migration 🚧 IN PROGRESS

#### Backend API Integration ✅ TEST DRIVE COMPLETE

**Status**: Ready for integration - test drive successful!

**Test Results**:

- ✅ Configuration comparison working
- ✅ Enhanced validation features working
- ✅ Environment variable handling working
- ✅ Migration plan documented
- ✅ Example files created

**Next Steps**:

1. Add config dependency to `backend-api/pyproject.toml`
2. Create `backend_api/config/shared.py` with `BackendAPIConfig`
3. Create `backend_api/config/migration.py` with gradual migration adapter
4. Test with existing functionality
5. Gradually migrate modules

**Key Files Ready**:

- `config/examples/backend_api_integration_test.py` - Live integration test
- `config/examples/backend_api_migration.py` - Migration demonstration
- Example `BackendAPIConfig` class with all required mixins
- Migration adapter pattern for gradual transition

#### Other Services

| Service                | Status     | Priority | Complexity |
| ---------------------- | ---------- | -------- | ---------- |
| **bff-api**            | 📋 Planned | High     | Medium     |
| **auth-api**           | 📋 Planned | High     | Low        |
| **recommendation-api** | 📋 Planned | Medium   | High       |
| **ml-api**             | 📋 Planned | Low      | Low        |
| **data-importer**      | 📋 Planned | Low      | Medium     |

## Integration Guide

### Step 1: Add Dependency

Add to your service's `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies ...
    "config @ file:../../libs/config",
]
```

### Step 2: Create Service Configuration

```python
# your_service/config/shared.py
from typing import List
from config.base.config import ServiceConfig
from config.services.database import DatabaseConfigMixin
from config.services.cache import CacheConfigMixin

class YourServiceConfig(ServiceConfig, DatabaseConfigMixin, CacheConfigMixin):
    """Your service configuration using shared library."""

    # Service-specific settings
    api_port: int = 8000

    def validate_production_config(self) -> List[str]:
        """Custom production validation."""
        errors = super().validate_production_config()
        # Add service-specific validations
        return errors
```

### Step 3: Migration Adapter (Optional)

For gradual migration from existing configuration:

```python
# your_service/config/migration.py
from typing import Any
from your_service.config.legacy import LegacyConfig
from your_service.config.shared import YourServiceConfig

class ConfigAdapter:
    """Adapter for gradual migration."""

    def __init__(self, use_shared: bool = False):
        if use_shared:
            self._config = YourServiceConfig()
        else:
            self._config = LegacyConfig.get_instance()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._config, name)

# Global instance
config = ConfigAdapter(use_shared=False)  # Start with legacy
```

### Step 4: Update Imports

Gradually update your service modules:

```python
# Before
from your_service.config.legacy import Config

# After
from your_service.config.migration import config
# or directly:
from your_service.config.shared import YourServiceConfig
```

## Configuration Reference

### Core Settings

| Setting           | Environment Variable | Default         | Description             |
| ----------------- | -------------------- | --------------- | ----------------------- |
| `environment`     | `ENVIRONMENT`        | `"development"` | Application environment |
| `service_name`    | `SERVICE_NAME`       | `"unknown"`     | Service identifier      |
| `service_version` | `SERVICE_VERSION`    | `"0.1.0"`       | Service version         |
| `debug`           | `DEBUG`              | `False`         | Debug mode flag         |

### Database Settings (DatabaseConfigMixin)

| Setting                 | Environment Variable    | Default              | Description              |
| ----------------------- | ----------------------- | -------------------- | ------------------------ |
| `database_url`          | `DATABASE_URL`          | `"postgresql://..."` | Database connection URL  |
| `database_pool_size`    | `DATABASE_POOL_SIZE`    | `5`                  | Connection pool size     |
| `database_max_overflow` | `DATABASE_MAX_OVERFLOW` | `10`                 | Max overflow connections |
| `database_pool_timeout` | `DATABASE_POOL_TIMEOUT` | `30`                 | Pool timeout (seconds)   |
| `database_echo`         | `DATABASE_ECHO`         | `False`              | Echo SQL queries         |

### Cache Settings (CacheConfigMixin)

| Setting                 | Environment Variable    | Default                      | Description           |
| ----------------------- | ----------------------- | ---------------------------- | --------------------- |
| `cache_url`             | `CACHE_URL`             | `"redis://localhost:6379/0"` | Redis connection URL  |
| `cache_max_connections` | `CACHE_MAX_CONNECTIONS` | `10`                         | Max Redis connections |
| `cache_default_ttl`     | `CACHE_DEFAULT_TTL`     | `3600`                       | Default TTL (seconds) |
| `cache_key_prefix`      | `CACHE_KEY_PREFIX`      | `""`                         | Key prefix for cache  |

### Authentication Settings (AuthConfigMixin)

| Setting                       | Environment Variable          | Default       | Description        |
| ----------------------------- | ----------------------------- | ------------- | ------------------ |
| `jwt_secret`                  | `JWT_SECRET`                  | `"change-me"` | JWT signing secret |
| `jwt_algorithm`               | `JWT_ALGORITHM`               | `"HS256"`     | JWT algorithm      |
| `access_token_expire_minutes` | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`          | Access token TTL   |
| `refresh_token_expire_days`   | `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`           | Refresh token TTL  |

### Monitoring Settings (MonitoringConfigMixin)

| Setting                 | Environment Variable    | Default  | Description               |
| ----------------------- | ----------------------- | -------- | ------------------------- |
| `log_level`             | `LOG_LEVEL`             | `"INFO"` | Logging level             |
| `enable_metrics`        | `ENABLE_METRICS`        | `False`  | Enable metrics collection |
| `health_check_interval` | `HEALTH_CHECK_INTERVAL` | `30`     | Health check interval     |
| `structured_logging`    | `STRUCTURED_LOGGING`    | `True`   | Use structured logging    |

### Vector Database Settings (VectorDBConfigMixin)

| Setting                | Environment Variable   | Default                   | Description       |
| ---------------------- | ---------------------- | ------------------------- | ----------------- |
| `vector_db_url`        | `VECTOR_DB_URL`        | `"http://localhost:6333"` | Qdrant URL        |
| `vector_db_collection` | `VECTOR_DB_COLLECTION` | `"default"`               | Collection name   |
| `vector_db_size`       | `VECTOR_DB_SIZE`       | `384`                     | Vector dimensions |
| `vector_db_distance`   | `VECTOR_DB_DISTANCE`   | `"cosine"`                | Distance metric   |

## Security Features

### Production Validation

All configuration classes include production validation:

```python
config = MyServiceConfig()
if config.environment == "production":
    errors = config.validate_production_config()
    if errors:
        raise ValueError(f"Production config errors: {errors}")
```

### Secret Masking

Sensitive values are automatically masked in logs:

```python
config = MyServiceConfig()
print(config.get_masked_database_url())  # postgresql://***:***@host:5432/db
print(config.get_masked_jwt_secret())    # ***
```

### Environment Validation

- JWT secrets must be sufficiently strong in production
- Database URLs must use secure connections in production
- Debug mode is automatically disabled in production
- CORS origins are validated for production use

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test modules
pytest tests/test_base_config.py
pytest tests/test_service_mixins.py
```

### Integration Testing

Test your service configuration:

```bash
# From your service directory
python ../../libs/config/examples/your_service_integration_test.py
```

## Contributing

1. **Adding New Mixins**: Create new mixin classes in `src/config/services/`
2. **Environment Variables**: Update the reference tables above
3. **Documentation**: Update this README and add examples
4. **Testing**: Add comprehensive tests for new functionality

## Examples

See the `examples/` directory for complete integration examples:

- `backend_api_example.py` - Backend API service configuration
- `backend_api_migration.py` - Migration demonstration
- `backend_api_integration_test.py` - Live integration test
- `recommendation_api_example.py` - ML service with vector database

## License

MIT License - see LICENSE file for details.
