# Auth API Service

Dedicated authentication microservice for the Next Watch movie platform. This service handles all authentication concerns including user registration, login, JWT token management, and token verification for other services.

## 🎯 Purpose

This service handles all authentication concerns in the microservices architecture:

- User registration and login
- JWT token generation and validation
- Token verification for BFF service
- Centralized authentication logic
- User management and administration

## 🏗️ Architecture Role

```
Frontend → BFF → Auth-API (verify token) → Backend-API (X-User-ID header)
```

- **Frontend** sends tokens to BFF
- **BFF** validates tokens via Auth-API `/auth/v1/tokens/verify`
- **Auth-API** returns user info if token is valid
- **BFF** injects `X-User-ID` header for Backend-API calls

### Core Architecture

The Auth API follows a modular architecture with clear separation of concerns:

- **Core Module**: Application factory, middleware, and logging configuration
- **Routes**: HTTP endpoint handlers organized by domain
- **Services**: Business logic and authentication operations
- **Database**: Data access layer with SQLModel/SQLAlchemy
- **CLI**: Command-line interface for operations and management
- **Configuration**: Environment-based configuration management

## 🚀 Quick Start

### Installation

```bash
# Navigate to Auth API directory
cd apps/auth-api

# Install dependencies
hatch env create

# Copy environment configuration
cp .env.example .env

# Start the service
hatch run serve
```

### Using the CLI

The Auth API includes a comprehensive command-line interface for development and operations:

```bash
# Show all available commands
auth-api --help

# Start the development server
auth-api serve --reload --verbose

# Check configuration
auth-api config --verbose

# Show version information
auth-api version
```

## 🛠️ CLI Commands

### Server Management

```bash
# Start the Auth API server
auth-api serve [OPTIONS]

Options:
  --host TEXT          Host to bind server to [default: 0.0.0.0]
  --port INTEGER       Port to bind server to [default: 8003]
  --reload             Enable auto-reload for development
  --log-level TEXT     Set log level (DEBUG, INFO, WARNING, ERROR)
  --verbose, -v        Enable verbose logging and output
  --quiet, -q          Suppress console output except errors
```

### Configuration Management

```bash
# Display current configuration
auth-api config [OPTIONS]

Options:
  --show-secrets       Show sensitive configuration values (use with caution)
  --verbose, -v        Show detailed configuration information

# Examples
auth-api config                    # Show masked configuration
auth-api config --verbose         # Show detailed configuration
auth-api config --show-secrets    # Show unmasked secrets (development only)
```

### Health Checks

Comprehensive health checking for the Auth API service and dependencies:

```bash
# Check all services and dependencies
auth-api health check [OPTIONS]

Options:
  --auth-api-url TEXT       Auth API URL to check (overrides config)
  --backend-api-url TEXT    Backend API URL to check (optional)
  --timeout INTEGER         Request timeout in seconds [default: 5]
  --verbose, -v             Show detailed output

# Check specific components
auth-api health self [OPTIONS]      # Check Auth API only
auth-api health database [OPTIONS]  # Check database connection only

# Examples
auth-api health check                # Check all services
auth-api health check --verbose     # Detailed health check with response times
auth-api health self --timeout 10   # Check self with custom timeout
auth-api health database            # Check database connection
```

### User Management

Comprehensive user administration commands:

```bash
# List users
auth-api users list [OPTIONS]

Options:
  --limit INTEGER       Maximum number of users to display [default: 50]
  --active-only         Show only active users
  --search TEXT         Search users by email or username
  --verbose, -v         Show detailed output

# Create new user
auth-api users create [OPTIONS]

Options:
  --email TEXT          User email address (required)
  --username TEXT       Username (optional)
  --password TEXT       User password (will prompt if not provided)
  --active/--inactive   User active status [default: active]
  --admin               Grant admin privileges
  --verbose, -v         Show detailed output

# User status management
auth-api users activate USER_EMAIL_OR_ID     # Activate user account
auth-api users deactivate USER_EMAIL_OR_ID   # Deactivate user account
auth-api users delete USER_EMAIL_OR_ID       # Delete user permanently

# User statistics
auth-api users stats [OPTIONS]

Options:
  --verbose, -v         Show detailed statistics

# Examples
auth-api users list --active-only --limit 20        # List 20 active users
auth-api users create --email user@example.com      # Create user (will prompt for password)
auth-api users create --email admin@example.com --admin  # Create admin user
auth-api users activate user@example.com            # Activate user by email
auth-api users stats --verbose                      # Show detailed user statistics
```

### Database Management

```bash
# Initialize database with required tables
auth-api init-db [OPTIONS]

Options:
  --confirm/--no-confirm    Confirm before initializing [default: True]
  --verbose, -v             Show detailed output

# Examples
auth-api init-db                    # Initialize with confirmation
auth-api init-db --no-confirm      # Initialize without confirmation
auth-api init-db --verbose         # Show detailed initialization process
```

### Version Information

```bash
# Show version and environment information
auth-api version
```

## 🔧 CLI Features

### Rich Output

The CLI uses Rich for beautiful, informative output:

- **Color-coded status messages** (green for success, red for errors, yellow for warnings)
- **Progress indicators** for long-running operations
- **Formatted tables** for configuration, user lists, and statistics
- **Interactive prompts** for sensitive operations

### Environment Integration

Commands automatically use environment variables and can be overridden:

```bash
# Use environment variables
export AUTH_API_URL=http://production-auth:8003
auth-api health check

# Override with command-line options
auth-api health check --auth-api-url http://staging-auth:8003
```

### Error Handling

Comprehensive error handling with:

- **Detailed error messages** with actionable information
- **Proper exit codes** for scripting and CI/CD integration
- **Logging integration** for debugging and monitoring
- **Graceful handling** of database errors and connection issues

### Development Workflow

```bash
# Development server with auto-reload and verbose logging
auth-api serve --reload --verbose --log-level DEBUG

# Initialize database for development
auth-api init-db --verbose

# Create admin user for testing
auth-api users create --email admin@localhost --admin --verbose

# Check all services are healthy
auth-api health check --verbose

# Monitor user activity
auth-api users stats --verbose
```

## 📡 API Endpoints

### Health & Info

```http
GET /               # Service information
GET /health         # Comprehensive health check with database status
GET /health/live    # Liveness check for load balancers
GET /health/ready   # Readiness check for orchestrators
GET /health/deep    # Deep diagnostics (optional)
```

### Authentication (v1)

```http
POST /auth/v1/users           # Register new user
POST /auth/v1/tokens          # Login (OAuth2 form: username=email, password)
PUT  /auth/v1/tokens          # Refresh access token
GET  /auth/v1/users/me        # Get current user info
```

### Token Verification (for BFF)

```http
POST /auth/v1/tokens/verify   # Verify JWT token and return user info
```

## 🧩 Integration Points

### Database

- **PostgreSQL**: Primary data store for user accounts and authentication data
- **Shared with other services**: Uses the same database as Backend API
- **Health Monitoring**: Comprehensive database health checks with response time tracking

### Health Service

The service includes a comprehensive health monitoring system:

- **Database Health**: PostgreSQL connection and performance monitoring
- **Response Time Tracking**: Monitors database query performance
- **Multiple Endpoints**: Separate endpoints for different health check types
- **Load Balancer Integration**: Optimized health checks for orchestration systems

### Configuration

Environment variables:

```bash
# Server Configuration
AUTH_API_PORT=8003
HOST=0.0.0.0
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
LOGS_DIR=logs

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/next_watch

# JWT Configuration
JWT_SECRET=your-jwt-secret-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Configuration
PASSWORD_HASH_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION_MINUTES=15
SESSION_TIMEOUT_MINUTES=60

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8001

# Performance Monitoring
ENABLE_PERFORMANCE_METRICS=false

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

## 🔐 Security Features

- **JWT Tokens**: Industry-standard JWT for authentication
- **Password Hashing**: Bcrypt with configurable rounds
- **Token Expiration**: Configurable access and refresh token lifetimes
- **Rate Limiting**: Configurable request rate limiting
- **Login Lockout**: Protection against brute force attacks
- **Environment Isolation**: Separate configuration for dev/prod

## 🧪 Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8003/auth/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### Login (OAuth2 form)

```bash
curl -X POST http://localhost:8003/auth/v1/tokens \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=user@example.com&password=securepassword123'
```

### Refresh Token

```bash
curl -X PUT http://localhost:8003/auth/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<your-refresh-token>"
  }'
```

### Verify Token (BFF Usage)

```bash
curl -X POST http://localhost:8003/auth/v1/tokens/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

## 🧪 Testing

```bash
# Run all tests
hatch run test

# Run with coverage
hatch run test-cov

# Run specific test file
hatch run test tests/test_auth.py

# Run with verbose output
hatch run test -v
```

## 🔧 Development

### Code Style

The project follows Google Python Style Guide:

```bash
# Format code
hatch run format

# Lint code (includes black, isort, ruff, and mypy)
hatch run lint
```

### Adding New CLI Commands

1. **Create command module** in `src/auth_api/cli/commands/`
2. **Import in commands/**init**.py**
3. **Add to main CLI app** in `src/auth_api/cli/main.py`
4. **Write tests** for the new commands
5. **Update documentation**

Example command structure:

```python
# src/auth_api/cli/commands/example.py
import typer
from rich.console import Console

app = typer.Typer(name="example", help="Example commands.")
console = Console()

@app.command()
def hello(name: str = typer.Option(..., help="Name to greet")):
    """Say hello to someone."""
    console.print(f"[green]Hello {name}![/green]")
```

### Project Structure

```
apps/auth-api/
├── src/auth_api/
│   ├── core/           # Core application components
│   │   ├── app.py      # FastAPI application factory
│   │   ├── middleware.py # Middleware configuration
│   │   ├── logging.py  # Logging setup
│   │   └── README.md   # Core module documentation
│   ├── config/         # Configuration management
│   ├── routes/         # FastAPI route handlers
│   ├── services/       # Business logic and authentication services
│   ├── db/            # Database models and connections
│   ├── schemas/       # Pydantic models for request/response
│   ├── dependencies/ # FastAPI dependency injection
│   ├── cli/           # Command-line interface
│   │   ├── commands/  # Modular CLI commands
│   │   ├── utils.py   # CLI utilities
│   │   └── main.py    # Main CLI app
│   └── main.py        # Application entry point
├── tests/             # Test suite
├── logs/              # Application logs
├── .env               # Environment configuration
├── .env.local         # Local development overrides
├── pyproject.toml     # Dependencies and Hatch configuration
├── hatch.toml         # Hatch project configuration
├── Dockerfile         # Optimized multi-stage Docker build
└── README.md          # This file
```

## 🚀 Deployment

### Docker

The service can be built and run using Docker with an optimized Alpine-based build:

```bash
# Build the optimized Docker image
docker build -f apps/auth-api/Dockerfile -t next-watch-auth .

# Run the container
docker run -p 8003:8003 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/next_watch \
  -e JWT_SECRET=your-secret-key \
  next-watch-auth

# Or run in background
docker run -d -p 8003:8003 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/next_watch \
  -e JWT_SECRET=your-secret-key \
  --name auth-api \
  next-watch-auth
```

The Docker build uses:

- **Alpine Linux** for minimal image size (~80-120MB)
- **Multi-stage build** to exclude build dependencies from final image
- **Non-root user** for security
- **Health checks** for container orchestration
- **Proper movie-storage dependency** handling

### Environment Variables

Ensure these are set in production:

- `ENVIRONMENT=production`
- `JWT_SECRET` (secure random string)
- `DATABASE_URL` (production database URL)
- `PASSWORD_HASH_ROUNDS` (12 or higher for production)
- `MAX_LOGIN_ATTEMPTS` (reasonable limit like 5)

## 📊 Monitoring

The Auth API service provides several monitoring endpoints:

- Health checks for load balancer integration
- Structured logging for observability
- Request/response timing middleware
- User activity tracking
- CLI tools for operational monitoring

## 🤝 Contributing

1. Follow TDD practices - write tests first
2. Use type hints for all functions
3. Add docstrings following Google style
4. Update README for any API changes
5. Ensure all tests pass before submitting
6. Test CLI commands thoroughly

## 📝 License

This project is part of the Next Watch movie platform.

---
