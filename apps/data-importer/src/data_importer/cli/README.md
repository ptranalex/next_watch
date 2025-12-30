# CLI Module

This directory contains the command-line interface (CLI) implementation for the data-importer application. The CLI is built using [Typer](https://typer.tiangolo.com/) and provides a modern, user-friendly interface for importing movie and TV show data from various external sources.

## 📁 Directory Structure

```
cli/
├── __init__.py          # Main CLI app initialization and command registration
├── __main__.py          # Entry point for python -m data_importer.cli
├── utils.py             # Shared CLI utilities and helper functions
├── commands/            # Individual command implementations
│   ├── __init__.py      # Command module exports
│   ├── sync.py          # Movie synchronization commands
│   ├── interactive.py   # Interactive interface command
│   ├── shell/           # Interactive shell command
│   └── README.md        # Detailed command documentation
└── README.md           # This file
```

## 🚀 Quick Start

### Installation

The CLI is automatically available after installing the data-importer package:

```bash
# Install the package
pip install -e .

# Use the CLI
data-importer --help
```

### Basic Usage

```bash
# Show all available commands
data-importer --help

# Sync movies for a specific year range
data-importer sync movies --start-year 2022 --end-year 2023 --save

# Launch interactive shell
data-importer shell

# Launch interactive interface (experimental)
data-importer interactive
```

## 📋 Available Commands

### 1. **Sync Commands** (`sync`)

Import movie data from external sources (TMDB, OMDB).

```bash
# Sync movies with default settings
data-importer sync movies

# Sync with custom parameters
data-importer sync movies \
  --start-year 2020 \
  --end-year 2023 \
  --limit 50 \
  --credits \
  --save \
  --verbose

# Sync without saving to database
data-importer sync movies --start-year 2023 --no-save
```

**Key Features:**

- Configurable year ranges and movie limits
- Optional cast/crew information import
- Database persistence control
- Progress tracking with visual indicators
- Comprehensive error handling

### 2. **Interactive Shell** (`shell`)

Launch an enhanced Python shell with pre-configured data import tools.

```bash
# Launch shell with default configuration
data-importer shell

# Launch with custom theme and verbose logging
data-importer shell --theme monokai --verbose
```

**Pre-loaded Environment:**

- `tmdb_client`: TMDB API client
- `omdb_client`: OMDB API client
- `imdb_client`: IMDb API client
- `async_run()`: Helper for async operations
- `sync_movies()`: Bulk movie synchronization
- `sync_movie_by_id()`: Single movie import
- Rich formatting and syntax highlighting

### 3. **Interactive Interface** (`interactive`)

Experimental conversational interface for guided data operations.

```bash
data-importer interactive
```

**Status:** Under development - provides configuration validation and setup.

## 🛠️ CLI Architecture

### Core Components

#### 1. **Main App (`__init__.py`)**

The central CLI application built with Typer:

```python
app = typer.Typer(
    name="data-importer",
    help="Import movie and TV show data from various sources.",
    add_completion=False,
)
```

**Features:**

- Rich traceback handling for better error display
- Centralized logging configuration
- Command group registration
- Global error handling

#### 2. **Entry Point (`__main__.py`)**

Enables running the CLI as a Python module:

```bash
python -m data_importer.cli
```

#### 3. **Utilities (`utils.py`)**

Shared functions used across commands:

- **`format_config_table()`**: Creates Rich tables for configuration display
- **`print_config()`**: Prints configuration in a user-friendly format
- **`get_api_key()`**: Standardized API key validation and retrieval
- **`print_plain()`**: Plain text output without formatting

### Configuration Integration

The CLI integrates seamlessly with the application's configuration system:

```python
from data_importer.config.app import Config

def command():
    config = Config.get_instance()
    # Use config defaults when CLI options not provided
    actual_value = cli_option if cli_option is not None else config.default_value
```

### Logging Integration

All commands use the centralized logging system:

```python
from data_importer.config.logging import with_logging

@with_logging(log_level="INFO")
def command():
    logger = logging.getLogger(__name__)
    logger.info("Command executed")
```

## 🎨 User Experience Features

### Rich Console Output

The CLI uses [Rich](https://rich.readthedocs.io/) for enhanced terminal output:

- **Colored output** for better readability
- **Progress bars** for long-running operations
- **Tables** for structured data display
- **Syntax highlighting** in the interactive shell
- **Error formatting** with stack traces

### Error Handling

Comprehensive error handling with user-friendly messages:

```python
try:
    # Command logic
    result = perform_operation()
except SpecificError as e:
    console.print(f"[red]Error: {e}[/red]")
    raise typer.Exit(code=1)
except Exception as e:
    console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
    logger.exception("Full exception details")
    raise typer.Exit(code=1)
```

### API Key Management

Standardized API key handling across all commands:

```python
# Supports CLI arguments, environment variables, and validation
api_key = get_api_key(
    provided_key=cli_arg,
    env_var_name="TMDB_ACCESS_TOKEN",
    key_name="TMDB access token",
    console=console,
    required=True
)
```

## 🔧 Development Guide

### Adding New Commands

1. **Create Command Module**

```python
# cli/commands/new_command.py
import typer
from data_importer.config.logging import with_logging

app = typer.Typer(name="new-command", help="Description")

@app.command()
@with_logging(log_level="INFO")
def new_subcommand():
    """New command implementation."""
    pass
```

2. **Register Command**

```python
# cli/__init__.py
from data_importer.cli.commands import new_command

app.add_typer(new_command.app, name="new-command")
```

### Best Practices

#### Type Annotations

Always use comprehensive type hints:

```python
from typing import Optional
import typer

def command(
    required_arg: str = typer.Argument(..., help="Required argument"),
    optional_flag: Optional[str] = typer.Option(None, help="Optional flag"),
    boolean_flag: bool = typer.Option(False, help="Boolean flag"),
) -> None:
```

#### Help Documentation

Provide clear help text and examples:

```python
def command():
    """
    Brief command description.

    Detailed explanation of what the command does,
    including important notes and limitations.

    Examples:
        data-importer command --option value
        data-importer command arg1 arg2 --flag
    """
```

#### Configuration Defaults

Use the configuration system for default values:

```python
def command(limit: Optional[int] = typer.Option(None, help="Limit")):
    config = Config.get_instance()
    actual_limit = limit if limit is not None else config.default_limit
```

## 🧪 Testing

### Unit Tests

Test command logic separately from CLI interface:

```python
def test_command_logic():
    # Test core functionality without CLI
    result = command_function(args)
    assert result.success
```

### CLI Integration Tests

Use Typer's testing utilities:

```python
from typer.testing import CliRunner
from data_importer.cli import app

def test_command_cli():
    runner = CliRunner()
    result = runner.invoke(app, ["sync", "movies", "--help"])
    assert result.exit_code == 0
    assert "Sync movies" in result.stdout
```

## 📦 Dependencies

### Core Dependencies

- **[Typer](https://typer.tiangolo.com/)**: Modern CLI framework with automatic help generation
- **[Rich](https://rich.readthedocs.io/)**: Rich text and beautiful formatting in the terminal
- **[Click](https://click.palletsprojects.com/)**: Underlying CLI library (via Typer)

### Application Dependencies

- **Config System**: Centralized configuration management
- **Logging System**: Structured logging with file and console output
- **Service Clients**: API clients for external data sources (TMDB, OMDB, IMDb)
- **Database Layer**: SQLModel-based data persistence

## 🔍 Troubleshooting

### Common Issues

#### API Key Errors

```bash
Error: TMDB access token is required.
Provide it via command option or set the TMDB_ACCESS_TOKEN environment variable.
```

**Solution**: Set environment variables or use CLI options:

```bash
export TMDB_ACCESS_TOKEN="your_token_here"
export OMDB_API_KEY="your_key_here"

# Or use CLI options
data-importer sync movies --tmdb-token "your_token" --omdb-key "your_key"
```

#### Database Connection Issues

```bash
Error: Could not connect to database
```

**Solution**: Ensure database is running and connection string is correct in `.env` file.

#### Import Errors

```bash
ModuleNotFoundError: No module named 'data_importer'
```

**Solution**: Install the package in development mode:

```bash
pip install -e .
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
data-importer sync movies --verbose
```

This provides detailed logs including:

- API request/response details
- Database operations
- Configuration values
- Error stack traces

## 🚀 Performance Tips

### Batch Operations

Use appropriate batch sizes for large imports:

```bash
# Process in smaller batches
data-importer sync movies --start-year 2020 --end-year 2020 --limit 100
```

### Database Optimization

- Use `--no-save` for testing without database writes
- Ensure database indexes are properly configured
- Monitor database connection pool usage

### API Rate Limiting

- TMDB: 40 requests per 10 seconds
- OMDB: 1000 requests per day (free tier)
- Use appropriate delays between requests

## 📈 Future Enhancements

### Planned Features

- **Configuration Profiles**: Multiple environment configurations
- **Parallel Processing**: Concurrent API requests and database operations
- **Data Validation**: Enhanced data quality checks
- **Export Commands**: Data export in various formats
- **Monitoring**: Built-in performance and health monitoring

### Contributing

When adding new CLI features:

1. Follow the established patterns in existing commands
2. Add comprehensive type annotations
3. Include proper error handling and logging
4. Update documentation and help text
5. Add unit and integration tests
6. Consider user experience and accessibility

The CLI module provides a robust, user-friendly interface for all data import operations while maintaining clean architecture and excellent developer experience.
