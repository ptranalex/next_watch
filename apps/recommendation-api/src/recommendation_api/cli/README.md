# Recommendation API CLI

Command-line interface for managing the Recommendation API service.

## Overview

The CLI provides a set of commands for managing the Recommendation API service, including server management, configuration, health checks, embeddings management, and debugging tools. It uses Typer for command-line argument parsing and Rich for enhanced console output.

## Installation

The CLI is installed as part of the Recommendation API package:

```bash
pip install recommendation-api
```

## Usage

The CLI is accessible through the `rec-api` command:

```bash
rec-api [COMMAND] [OPTIONS]
```

### Available Commands

#### Server Management

```bash
# Start the server
rec-api serve start [--host HOST] [--port PORT] [--workers N] [--reload] [--log-level LEVEL] [--verbose] [--quiet]

# Stop the server
rec-api serve stop [--verbose] [--quiet]

# Restart the server
rec-api serve restart [--host HOST] [--port PORT] [--workers N] [--reload] [--log-level LEVEL] [--verbose] [--quiet]
```

Options for `serve` commands:

- `--host`: Host address to bind to (default from config)
- `--port`: Port number to bind to (default from config)
- `--workers`: Number of worker processes (not used with --reload)
- `--reload`: Enable auto-reload for development
- `--log-level`: Set log level (DEBUG, INFO, WARNING, ERROR)
- `--verbose`: Enable verbose logging and detailed output
- `--quiet`: Suppress most console output

#### Configuration Management

```bash
# Show current configuration
rec-api config show [--show-secrets] [--verbose] [--quiet]

# Validate configuration
rec-api config validate [--verbose] [--quiet]

# Show environment-specific settings
rec-api config env [--verbose] [--quiet]
```

Options for `config` commands:

- `--show-secrets`: Display sensitive configuration values
- `--verbose`: Show detailed configuration information
- `--quiet`: Suppress most console output

#### Health Checks

```bash
# Check health of all services
rec-api health check [--verbose] [--quiet]

# Ping specific service
rec-api health ping SERVICE [--verbose] [--quiet]
```

Available services for `health ping`:

- `api`: Recommendation API service
- `db`: Database service
- `qdrant`: Vector database service

Options for `health` commands:

- `--verbose`: Show detailed health information and troubleshooting tips
- `--quiet`: Suppress most console output

#### Embeddings Management

```bash
# Generate embeddings for movies
rec-api embeddings generate [--batch-size SIZE] [--force] [--limit LIMIT] [--movie-id ID] [--verbose] [--quiet]

# Show embedding generation status
rec-api embeddings status [--verbose] [--quiet]

# Clean up orphaned embeddings
rec-api embeddings cleanup [--dry-run/--execute] [--verbose] [--quiet]

# Show embedding configuration
rec-api embeddings info [--verbose] [--quiet]

# Repair embeddings with missing vectors
rec-api embeddings repair_embeddings [--batch-size SIZE] [--movie-id ID] [--dry-run] [--verbose] [--quiet]
```

Options for `embeddings generate`:

- `--batch-size`: Number of movies to process in each batch
- `--force`: Force regeneration of existing embeddings
- `--limit`: Limit number of movies to process
- `--movie-id`: Process specific movie by ID
- `--verbose`: Show detailed progress
- `--quiet`: Suppress most console output

Options for `embeddings repair_embeddings`:

- `--batch-size`: Number of movies to process in each batch
- `--movie-id`: Specific movie ID to repair
- `--dry-run`: Show which embeddings would be repaired without making changes
- `--verbose`: Show detailed progress
- `--quiet`: Suppress most console output

#### Debug Tools

```bash
# Check if a movie has an embedding
rec-api debug check_embedding MOVIE_ID [--verbose] [--quiet]

# Find similar movies to a specific movie
rec-api debug similar_movies MOVIE_ID [--limit N] [--min-score SCORE] [--direct] [--ids-only] [--verbose] [--quiet]

# Compare two movies by calculating similarity
rec-api debug compare_movies MOVIE_ID1 MOVIE_ID2 [--verbose] [--quiet]

# Show vector database status
rec-api debug vector_status [--verbose] [--quiet]

# Recreate embedding for a specific movie
rec-api debug recreate_embedding MOVIE_ID [--force] [--verbose] [--quiet]
```

Options for `debug` commands:

- `--verbose`: Show detailed debug information including vectors
- `--quiet`: Suppress most console output
- Command-specific options (see `--help` for each command)

#### Version Information

```bash
# Show version information
rec-api version
```

## Module Structure

```
cli/
├── __init__.py          # Package initialization
├── main.py             # Main CLI application
├── utils.py            # Utility functions
└── commands/           # Command modules
    ├── __init__.py     # Commands package
    ├── serve.py        # Server management commands
    ├── config.py       # Configuration commands
    ├── health.py       # Health check commands
    ├── embeddings.py   # Embedding management commands
    ├── debug.py        # Debug and diagnostic tools
    └── version.py      # Version information
```

## Common Command Features

All commands support the following common options:

- `--verbose, -v`: Show detailed information and extra debug output
- `--quiet, -q`: Suppress most log output except errors
- `--help, -h`: Show help message for the command

Most commands provide:

- Color-coded output for status (green for success, yellow for warnings, red for errors)
- Detailed error messages with troubleshooting tips in verbose mode
- Formatted tables for structured data
- Progress indicators for long-running operations

## Development

### Adding New Commands

1. Create a new command module in `commands/`
2. Define a Typer app instance
3. Add command functions with proper type hints and docstrings
4. Import and add the command module in `main.py`

Example:

```python
# commands/new_command.py
import typer
from rich.console import Console
import logging
from recommendation_api.config.logging import configure_logging

app = typer.Typer(name="new-command")
console = Console()
logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False, quiet: bool = False):
    """Configure logging for commands."""
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "WARNING"
    configure_logging(log_level=log_level, verbose=verbose)

@app.command()
def do_something(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most log output"),
) -> None:
    """Do something.

    Args:
        verbose: Show detailed output
        quiet: Suppress most log output
    """
    # Configure logging
    setup_logging(verbose=verbose, quiet=quiet)

    # Command implementation
    console.print("[green]Operation successful[/green]")

# main.py
from recommendation_api.cli.commands import new_command
app.add_typer(new_command.app, name="new-command")
```

### Utility Functions

Common utility functions are available in `utils.py`:

- `format_config_table()`: Format configuration as Rich table
- `print_config()`: Display configuration settings
- `check_service_health()`: Check service health status
- `display_service_status()`: Show service status table
- `configure_logging()`: Set up logging
- `print_error()`: Display error messages
- `print_success()`: Display success messages

## Error Handling

The CLI uses consistent error handling:

1. All commands catch exceptions and display user-friendly error messages
2. Rich console output for better readability
3. Proper logging of errors for debugging
4. Exit codes for script integration

## Contributing

1. Follow the Google Python Style Guide
2. Add type hints to all functions
3. Include docstrings for all public functions
4. Add tests for new functionality
5. Update this README for new features
