***REMOVED*** Configuration Module

The configuration module provides centralized configuration management for the Auth API service. It handles environment variable loading, validation, type conversion, and provides a clean interface for accessing configuration throughout the application.

***REMOVED******REMOVED*** Overview

The configuration module provides:

- **Environment Configuration**: Load settings from environment variables and `.env` files
- **Type Safety**: Type conversion and validation for all configuration values
- **Hierarchical Loading**: Support for multiple environment files with precedence
- **Configuration Validation**: Comprehensive validation of required settings
- **Logging Configuration**: Structured logging setup and configuration
- **Development Support**: Special handling for development and testing environments

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Module Organization

- **`app.py`** (8.3KB, 231 lines): Main application configuration and settings
- **`env.py`** (5.9KB, 208 lines): Environment variable loading and utilities
- **`logging.py`** (3.9KB, 120 lines): Logging configuration and setup

***REMOVED******REMOVED******REMOVED*** Configuration Hierarchy

```
1. Environment Variables (highest priority)
2. .env.local (local development overrides)
3. .env (base configuration)
4. Default Values (lowest priority)
```

***REMOVED******REMOVED*** Configuration Files

***REMOVED******REMOVED******REMOVED*** `app.py` - Application Configuration

The main configuration class that provides typed access to all application settings.

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features

- **Typed Configuration**: All settings have proper type hints
- **Environment Integration**: Automatically loads from environment variables
- **Validation**: Validates required settings and formats
- **Computed Properties**: Derived settings based on other configuration
- **Development Helpers**: Special handling for development environments

***REMOVED******REMOVED******REMOVED******REMOVED*** Main Configuration Class

```python
from pydantic import BaseSettings, validator
from typing import Optional, List
import os

class Config(BaseSettings):
    """
    Application configuration loaded from environment variables and .env files.

    Configuration is loaded in this order (highest to lowest priority):
    1. Environment variables
    2. .env.local file
    3. .env file
    4. Default values
    """

    ***REMOVED*** Server Configuration
    environment: str = "development"
    debug: bool = False
    auth_api_port: int = 8003
    auth_api_host: str = "0.0.0.0"

    ***REMOVED*** Database Configuration
    database_url: str
    database_echo: bool = False

    ***REMOVED*** JWT Configuration
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    ***REMOVED*** Security Configuration
    password_hash_rounds: int = 12
    max_login_attempts: int = 5
    login_lockout_duration_minutes: int = 15

    ***REMOVED*** CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000"]

    ***REMOVED*** Logging Configuration
    log_level: str = "INFO"
    log_dir: str = "logs"

    class Config:
        env_file = [".env", ".env.local"]
        env_file_encoding = "utf-8"
        case_sensitive = False
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration Categories

**Server Settings:**

```python
***REMOVED*** HTTP server configuration
auth_api_host: str = "0.0.0.0"        ***REMOVED*** Server bind address
auth_api_port: int = 8003              ***REMOVED*** Server port
environment: str = "development"        ***REMOVED*** Environment name
debug: bool = False                    ***REMOVED*** Debug mode
```

**Database Settings:**

```python
***REMOVED*** PostgreSQL database configuration
database_url: str                      ***REMOVED*** Database connection URL
database_echo: bool = False            ***REMOVED*** SQL query logging
database_pool_size: int = 5            ***REMOVED*** Connection pool size
database_max_overflow: int = 10        ***REMOVED*** Max overflow connections
```

**Authentication Settings:**

```python
***REMOVED*** JWT token configuration
jwt_secret: str                        ***REMOVED*** JWT signing secret
jwt_algorithm: str = "HS256"           ***REMOVED*** JWT algorithm
access_token_expire_minutes: int = 30  ***REMOVED*** Access token lifetime
refresh_token_expire_days: int = 7     ***REMOVED*** Refresh token lifetime

***REMOVED*** Password security
password_hash_rounds: int = 12         ***REMOVED*** Bcrypt rounds
max_login_attempts: int = 5            ***REMOVED*** Max failed attempts
login_lockout_duration_minutes: int = 15  ***REMOVED*** Lockout duration
```

**CORS Settings:**

```python
***REMOVED*** Cross-Origin Resource Sharing
cors_origins: List[str] = [            ***REMOVED*** Allowed origins
    "http://localhost:3000",
    "http://localhost:8001"
]
cors_credentials: bool = True          ***REMOVED*** Allow credentials
cors_methods: List[str] = ["*"]        ***REMOVED*** Allowed methods
cors_headers: List[str] = ["*"]        ***REMOVED*** Allowed headers
```

**Logging Settings:**

```python
***REMOVED*** Logging configuration
log_level: str = "INFO"                ***REMOVED*** Log level
log_dir: str = "logs"                  ***REMOVED*** Log directory
log_format: str = "structured"         ***REMOVED*** Log format (structured/text)
log_rotation: str = "1 day"            ***REMOVED*** Log rotation interval
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration Validation

```python
@validator('database_url')
def validate_database_url(cls, v):
    """Validate database URL format."""
    if not v:
        raise ValueError('DATABASE_URL is required')
    if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
        raise ValueError('DATABASE_URL must be a PostgreSQL URL')
    return v

@validator('jwt_secret')
def validate_jwt_secret(cls, v):
    """Validate JWT secret strength."""
    if not v:
        raise ValueError('JWT_SECRET is required')
    if len(v) < 32:
        raise ValueError('JWT_SECRET must be at least 32 characters')
    return v

@validator('cors_origins')
def validate_cors_origins(cls, v):
    """Parse CORS origins from string or list."""
    if isinstance(v, str):
        return [origin.strip() for origin in v.split(',')]
    return v

@validator('log_level')
def validate_log_level(cls, v):
    """Validate log level."""
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if v.upper() not in valid_levels:
        raise ValueError(f'Log level must be one of: {valid_levels}')
    return v.upper()
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Computed Properties

```python
@property
def is_development(self) -> bool:
    """Check if running in development environment."""
    return self.environment.lower() == "development"

@property
def is_production(self) -> bool:
    """Check if running in production environment."""
    return self.environment.lower() == "production"

@property
def is_testing(self) -> bool:
    """Check if running in testing environment."""
    return self.environment.lower() == "testing"

@property
def database_url_async(self) -> str:
    """Get async-compatible database URL."""
    if 'postgresql://' in self.database_url:
        return self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
    return self.database_url

@property
def cors_origin_list(self) -> List[str]:
    """Get CORS origins as a list."""
    if isinstance(self.cors_origins, str):
        return [origin.strip() for origin in self.cors_origins.split(',')]
    return self.cors_origins
```

***REMOVED******REMOVED******REMOVED*** `env.py` - Environment Loading

Utilities for loading and managing environment variables.

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features

- **Hierarchical Loading**: Load from multiple `.env` files with precedence
- **Type Conversion**: Convert environment strings to appropriate Python types
- **Validation Helpers**: Validate environment variable formats and values
- **Development Support**: Handle development-specific environment setup

***REMOVED******REMOVED******REMOVED******REMOVED*** Main Functions

```python
def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from a file.

    Args:
        env_file: Path to environment file

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('***REMOVED***'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
    return env_vars

def get_env_var(key: str, default: Any = None, required: bool = False) -> str:
    """
    Get environment variable with validation.

    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required

    Returns:
        Environment variable value

    Raises:
        ValueError: If required variable is missing
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = get_env_var(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable."""
    value = get_env_var(key, str(default))
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} must be an integer")

def get_env_list(key: str, default: List[str] = None, separator: str = ",") -> List[str]:
    """Get list environment variable."""
    if default is None:
        default = []
    value = get_env_var(key, separator.join(default))
    return [item.strip() for item in value.split(separator) if item.strip()]
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Environment File Loading

```python
def load_environment_files() -> None:
    """
    Load environment variables from files in order of precedence:
    1. .env.local (highest priority)
    2. .env (base configuration)
    """
    ***REMOVED*** Load base environment
    base_env = load_env_file(".env")
    for key, value in base_env.items():
        if key not in os.environ:
            os.environ[key] = value

    ***REMOVED*** Load local overrides
    local_env = load_env_file(".env.local")
    for key, value in local_env.items():
        os.environ[key] = value

    print(f"Loaded {len(base_env)} base and {len(local_env)} local environment variables")

def validate_required_env_vars(required_vars: List[str]) -> List[str]:
    """
    Validate that required environment variables are set.

    Args:
        required_vars: List of required environment variable names

    Returns:
        List of missing environment variables
    """
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    return missing
```

***REMOVED******REMOVED******REMOVED*** `logging.py` - Logging Configuration

Comprehensive logging setup for the application.

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features

- **Structured Logging**: JSON-formatted logs for production
- **Development Logging**: Human-readable logs for development
- **Log Rotation**: Automatic log file rotation
- **Multiple Handlers**: Console and file logging
- **Performance Logging**: Request/response timing

***REMOVED******REMOVED******REMOVED******REMOVED*** Logging Setup

```python
import logging
import logging.handlers
import sys
from typing import Dict, Any
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        ***REMOVED*** Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        ***REMOVED*** Add extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno',
                          'pathname', 'filename', 'module', 'lineno',
                          'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process',
                          'getMessage', 'exc_info', 'exc_text', 'stack_info'):
                log_entry[key] = value

        return json.dumps(log_entry)

def setup_logging(config: Config) -> None:
    """
    Setup application logging based on configuration.

    Args:
        config: Application configuration
    """
    ***REMOVED*** Create logs directory
    os.makedirs(config.log_dir, exist_ok=True)

    ***REMOVED*** Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level))

    ***REMOVED*** Clear existing handlers
    root_logger.handlers.clear()

    ***REMOVED*** Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if config.is_production:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    root_logger.addHandler(console_handler)

    ***REMOVED*** File handler with rotation
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(config.log_dir, 'auth-api.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(file_handler)

    ***REMOVED*** Error file handler
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(config.log_dir, 'auth-api-errors.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(error_handler)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Request Logging

```python
async def log_request(request: Request, response_time: float, status_code: int) -> None:
    """
    Log HTTP request details.

    Args:
        request: FastAPI request object
        response_time: Response time in seconds
        status_code: HTTP status code
    """
    logger = logging.getLogger("auth_api.requests")

    log_data = {
        'method': request.method,
        'url': str(request.url),
        'status_code': status_code,
        'response_time_ms': round(response_time * 1000, 2),
        'user_agent': request.headers.get('user-agent'),
        'remote_addr': request.client.host if request.client else None,
    }

    ***REMOVED*** Add user ID if authenticated
    if hasattr(request.state, 'user_id'):
        log_data['user_id'] = request.state.user_id

    if status_code >= 500:
        logger.error("HTTP request failed", extra=log_data)
    elif status_code >= 400:
        logger.warning("HTTP request error", extra=log_data)
    else:
        logger.info("HTTP request", extra=log_data)
```

***REMOVED******REMOVED*** Environment Variables

***REMOVED******REMOVED******REMOVED*** Required Variables

```bash
***REMOVED*** Database Configuration (Required)
DATABASE_URL=postgresql://user:password@localhost:5432/next_watch

***REMOVED*** JWT Configuration (Required)
JWT_SECRET=your-secure-jwt-secret-key-at-least-32-characters-long
```

***REMOVED******REMOVED******REMOVED*** Optional Variables

```bash
***REMOVED*** Server Configuration
AUTH_API_HOST=0.0.0.0
AUTH_API_PORT=8003
ENVIRONMENT=development
DEBUG=false

***REMOVED*** JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

***REMOVED*** Security Configuration
PASSWORD_HASH_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION_MINUTES=15

***REMOVED*** Database Configuration
DATABASE_ECHO=false
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

***REMOVED*** CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8001
CORS_CREDENTIALS=true

***REMOVED*** Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_FORMAT=structured
LOG_ROTATION=1 day

***REMOVED*** Performance Configuration
ENABLE_PERFORMANCE_METRICS=false
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

***REMOVED******REMOVED*** Usage Patterns

***REMOVED******REMOVED******REMOVED*** Loading Configuration

```python
from auth_api.config import Config

***REMOVED*** Load configuration (automatically loads environment)
config = Config()

***REMOVED*** Access configuration values
print(f"Server running on {config.auth_api_host}:{config.auth_api_port}")
print(f"Environment: {config.environment}")

***REMOVED*** Check environment type
if config.is_development:
    print("Running in development mode")
elif config.is_production:
    print("Running in production mode")
```

***REMOVED******REMOVED******REMOVED*** Configuration Validation

```python
def validate_configuration(config: Config) -> List[str]:
    """Validate configuration and return list of issues."""
    issues = []

    if not config.database_url:
        issues.append("DATABASE_URL is required")

    if not config.jwt_secret:
        issues.append("JWT_SECRET is required")
    elif len(config.jwt_secret) < 32:
        issues.append("JWT_SECRET must be at least 32 characters")

    return issues
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Configuration Management

1. **Environment Variables**: Use environment variables for all configuration
2. **Type Safety**: Use type hints and validation for all settings
3. **Default Values**: Provide sensible defaults for optional settings
4. **Validation**: Validate configuration at startup
5. **Documentation**: Document all configuration options

***REMOVED******REMOVED******REMOVED*** Security

1. **Secret Management**: Never commit secrets to version control
2. **Production Validation**: Validate security settings for production
3. **Environment Separation**: Use different configurations for different environments
4. **Access Control**: Limit access to sensitive configuration
5. **Rotation**: Implement secret rotation procedures

***REMOVED******REMOVED*** Dependencies

The configuration module depends on:

- **Pydantic**: Configuration validation and type conversion
- **Python-dotenv**: Environment file loading
- **Typing**: Type hints and validation
- **OS**: Environment variable access
- **Logging**: Python logging framework
