# BFF API Command Line Interface

This module provides a comprehensive command-line interface (CLI) for the BFF API service, built using Typer and integrated with the **NextWatch CLI Framework** for consistent UX and enterprise-grade patterns.

## 🎯 CLI Framework Integration

The BFF API CLI now leverages the **NextWatch CLI Framework** to provide:

- **Consistent UX** across all NextWatch services
- **Production-ready patterns** with structured logging and monitoring
- **Auto-generated commands** for common operations (health, cache, config)
- **Enterprise-grade features** like secret masking, retry logic, and async operations

## Structure

The CLI is organized as follows:

```
bff_api/cli/
│
├── main.py           # Main CLI application with framework integration
├── __main__.py       # Entry point for direct module execution
├── __init__.py       # Package initialization
├── utils.py          # Utility functions for CLI commands
└── commands/         # Remaining command modules
    ├── serve.py      # Server commands (enhanced with framework output)
    └── __init__.py   # Command module initialization
```

**Note**: Health and cache commands are now **auto-generated** by the CLI framework, providing consistent functionality across all NextWatch services.

## Command Groups

### Auto-Generated Commands (via CLI Framework)

- **health**: Health check commands using existing `health_service.py`
  - `health check`: Check health of all services (Backend API, Auth API, Recommendation API)
  - `health backend`: Check Backend API health only
  - `health auth`: Check Auth API health only
  - `health reco`: Check Recommendation API health only
- **cache**: Redis cache management commands
  - `cache info`: Display Redis cache information and statistics
  - `cache keys`: List cache keys with pattern matching
  - `cache get`: Get value for a specific key
  - `cache delete`: Delete a specific key
  - `cache clear`: Clear cache keys matching a pattern
- **config**: Configuration display with smart secret masking
  - `config`: Display current configuration
  - `config --verbose`: Show detailed configuration
  - `config --show-secrets`: Show sensitive configuration values (use with caution)

### Custom Commands

- **serve**: Server management commands (enhanced with framework output)
  - `serve` or `serve start`: Start the BFF API server
- **version**: Show BFF API version information

## Installation

The CLI is installed as part of the BFF API package:

```bash
# Install in development mode
cd /path/to/bff-api
pip install -e .
```

After installation, the CLI is available via:

```bash
# As a console script
bff-api [COMMAND] [OPTIONS]

# As a Python module
python -m bff_api.cli [COMMAND] [OPTIONS]
```

## Usage Examples

### Server Management

Start the server with default settings:

```bash
bff-api serve
```

Start with custom host and port:

```bash
bff-api serve start --host 127.0.0.1 --port 8080
```

Start in development mode with auto-reload:

```bash
bff-api serve --reload
```

### Health Checks (Framework-Generated)

Check health of all services:

```bash
bff-api health check
```

Check with detailed output:

```bash
bff-api health check --verbose
```

Check specific services:

```bash
bff-api health backend    # Backend API only
bff-api health auth       # Auth API only
bff-api health reco       # Recommendation API only
```

### Cache Management (Framework-Generated)

Display cache information:

```bash
bff-api cache info --verbose
```

List cache keys with patterns:

```bash
bff-api cache keys --pattern "user:*" --limit 50
bff-api cache keys --pattern "movie:*"
```

Get and manipulate cache values:

```bash
bff-api cache get user:123
bff-api cache delete session:abc123
bff-api cache clear --pattern "temp:*" --confirm
```

### Configuration (Framework-Generated)

Display current configuration:

```bash
bff-api config
```

Show detailed configuration:

```bash
bff-api config --verbose
```

Show sensitive values (development only):

```bash
bff-api config --show-secrets
```

## Environment Variables

The CLI respects the following environment variables:

| Variable          | Description                 | Default                  |
| ----------------- | --------------------------- | ------------------------ |
| `HOST`            | Server host address         | 0.0.0.0                  |
| `PORT`            | Server port number          | 8001                     |
| `LOG_LEVEL`       | Logging level               | INFO                     |
| `ENVIRONMENT`     | Environment (dev/prod)      | development              |
| `DEBUG`           | Enable debug mode           | false                    |
| `BACKEND_API_URL` | URL for backend API service | http://localhost:8000    |
| `AUTH_API_URL`    | URL for auth API service    | http://localhost:8003    |
| `RECO_API_URL`    | URL for recommendation API  | http://localhost:8002    |
| `REDIS_URL`       | URL for Redis connection    | redis://localhost:6379/0 |

## 🚀 CLI Framework Benefits

### 1. **Unified Output Management**

- Clean separation between user output (Rich console) and operational logging (structured logs)
- Consistent styling and color schemes across all commands
- Verbose mode with detailed operational information

### 2. **Enterprise-Grade Features**

- **Secret Masking**: Automatic masking of sensitive configuration values
- **Structured Logging**: JSON-formatted logs for monitoring and debugging
- **Retry Logic**: Built-in retry mechanisms for unreliable operations
- **Async Support**: Full async/await support for concurrent operations

### 3. **Production-Ready Patterns**

- **Health Service Integration**: Uses existing `health_service.py` for complex health checks
- **Connection Management**: Proper Redis client lifecycle management
- **Error Handling**: Comprehensive error handling with appropriate exit codes
- **Progress Indicators**: Rich progress bars for long-running operations

### 4. **Developer Experience**

- **Type Safety**: Full type annotations throughout
- **Auto-Completion**: Shell completion support
- **Consistent Help**: Standardized help text and command structure
- **Easy Extension**: Simple patterns for adding new commands

## Design Principles

1. **Framework Integration**: Leverage CLI framework for consistent UX and enterprise patterns
2. **Service Separation**: Complex logic stays in service layers (e.g., `health_service.py`)
3. **Clean Output**: Separation between user-facing output and operational logging
4. **Production Ready**: Secret masking, structured logging, and monitoring integration
5. **Type Safety**: Full type annotations for reliability and maintainability
6. **Async First**: Built for concurrent operations and scalable patterns

## Extending the CLI

### Using Framework Generators

For common patterns, use the CLI framework generators:

```python
from cli_framework import create_health_commands, create_cache_commands

# Auto-generate health commands
health_app = create_health_commands(
    health_service_getter=get_health_service,
    service_checks={
        "backend": ("check_backend_api", "Backend API"),
        "auth": ("check_auth_api", "Auth API"),
    }
)
```

### Custom Commands

For custom functionality, follow the framework patterns:

```python
from cli_framework import get_cli_output

@app.command()
def my_command(verbose: bool = False, quiet: bool = False):
    out = get_cli_output("my-command", verbose=verbose, quiet=quiet)

    out.info("User-facing message")
    out.log_operation("Operational log", key="value")
```

## Shell Completion

The BFF API CLI supports shell completion for Bash, Zsh, and Fish shells through the CLI framework integration.
