***REMOVED*** CLI Commands

This directory contains the implementation of all CLI commands for the data-importer application. The commands are built using [Typer](https://typer.tiangolo.com/) and follow consistent patterns for configuration, logging, and error handling.

***REMOVED******REMOVED*** Command Structure

```
commands/
├── __init__.py          ***REMOVED*** Command module exports
├── sync.py              ***REMOVED*** Movie synchronization commands
├── interactive.py       ***REMOVED*** Interactive interface command
├── shell/               ***REMOVED*** Interactive shell command
│   ├── __init__.py      ***REMOVED*** Shell module exports
│   ├── command.py       ***REMOVED*** Main shell command implementation
│   ├── helpers.py       ***REMOVED*** Shell helper functions and utilities
│   ├── help.py          ***REMOVED*** Shell help and banner functions
│   └── repl.py          ***REMOVED*** REPL configuration and setup
└── README.md           ***REMOVED*** This file
```

***REMOVED******REMOVED*** Available Commands

***REMOVED******REMOVED******REMOVED*** 1. Sync Commands (`sync.py`)

The sync command group provides functionality for importing movie data from external sources.

***REMOVED******REMOVED******REMOVED******REMOVED*** `sync movies`

Synchronizes movie data from TMDB and OMDB for a specified year range.

**Key Features:**

- Configurable year ranges and limits
- Optional cast/crew information
- Database persistence control
- Progress tracking with Rich console output
- Comprehensive error handling and logging

**Implementation Pattern:**

```python
@app.command(name="movies")sync
@with_logging(log_level="INFO")
def sync_movies(...):
    """Command implementation with type hints and comprehensive options."""
```

**Configuration:**

- Uses Config.get_instance() for default values
- Supports environment variables and CLI overrides
- Validates API keys using shared utilities

***REMOVED******REMOVED******REMOVED*** 2. Interactive Command (`interactive.py`)

Provides a conversational interface for data import operations.

**Status:** Experimental - Not fully implemented

**Key Features:**

- Configuration validation
- API client initialization
- Logging setup
- Future: Interactive prompts and guided operations

***REMOVED******REMOVED******REMOVED*** 3. Shell Command (`shell/`)

Launches an interactive Python shell with pre-configured data import tools.

**Key Features:**

- Pre-loaded API clients (TMDB, OMDB, IMDb)
- Helper functions for common operations
- Syntax highlighting and code completion
- Multiple themes and customization options
- Auto-imported utilities and async helpers

**Shell Environment:**

- `tmdb_client`: Pre-configured TMDB API client
- `omdb_client`: Pre-configured OMDB API client
- `imdb_client`: Pre-configured IMDb API client
- `run_async()`: Helper for running async functions
- `print_json()`, `print_plain()`: Output formatters
- Helper functions for data loading and manipulation

***REMOVED******REMOVED*** Implementation Patterns

***REMOVED******REMOVED******REMOVED*** 1. Command Definition

All commands follow this pattern:

```python
import typer
from data_importer.config.logging import with_logging

app = typer.Typer(name="command_group", help="Command group description")

@app.command(name="command_name")
@with_logging(log_level="INFO")
def command_function(
    ***REMOVED*** Required arguments
    required_arg: str = typer.Argument(..., help="Description"),

    ***REMOVED*** Optional arguments with defaults
    optional_arg: Optional[str] = typer.Option(
        None, "--option", "-o", help="Description"
    ),

    ***REMOVED*** Boolean flags
    flag: bool = typer.Option(False, "--flag", help="Description"),

    ***REMOVED*** Configuration-based defaults
    config_option: Optional[int] = typer.Option(
        None, "--config-opt", help="Uses config default if not provided"
    ),
):
    """
    Command docstring with comprehensive description.

    Examples:
        command_name arg --option value --flag
    """
```

***REMOVED******REMOVED******REMOVED*** 2. Configuration Integration

Commands integrate with the centralized configuration system:

```python
def command_function(...):
    ***REMOVED*** Get configuration instance
    config = Config.get_instance()

    ***REMOVED*** Use config defaults when CLI options not provided
    actual_value = cli_option if cli_option is not None else config.default_value

    ***REMOVED*** Display configuration in verbose mode
    if verbose:
        console.print("[bold cyan]Configuration:[/bold cyan]")
        console.print(f"Option: {actual_value}")
```

***REMOVED******REMOVED******REMOVED*** 3. API Key Management

All commands use the standardized API key utility:

```python
from data_importer.cli.utils import get_api_key

***REMOVED*** In command function
api_key = get_api_key(
    provided_key,           ***REMOVED*** CLI argument value
    "ENV_VAR_NAME",        ***REMOVED*** Environment variable name
    "Human readable name",  ***REMOVED*** Display name for errors
    console,               ***REMOVED*** Rich console instance
    required=True          ***REMOVED*** Whether key is required
)
```

***REMOVED******REMOVED******REMOVED*** 4. Error Handling

Commands implement comprehensive error handling:

```python
def command_function(...):
    try:
        ***REMOVED*** Command logic
        result = perform_operation()

        ***REMOVED*** Display results
        console.print(f"[green]Success: {result}[/green]")

    except SomeSpecificError as e:
        console.print(f"[red]Specific error: {e}[/red]")
        logger.error(f"Specific error details: {e}")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        logger.exception("Full exception details")
        raise typer.Exit(code=1)

    finally:
        ***REMOVED*** Cleanup resources
        cleanup_resources()
```

***REMOVED******REMOVED******REMOVED*** 5. Logging Integration

Commands use the `@with_logging` decorator:

```python
from data_importer.config.logging import with_logging

@with_logging(log_level="INFO")
def command_function(...):
    logger = logging.getLogger(__name__)
    logger.info("Command started")

    ***REMOVED*** Command implementation
```

***REMOVED******REMOVED******REMOVED*** 6. Progress Indication

Commands use Rich for progress indication:

```python
from rich.console import Console
from rich.progress import Progress

console = Console()

def command_function(...):
    with Progress() as progress:
        task = progress.add_task("Processing...", total=total_items)

        for item in items:
            ***REMOVED*** Process item
            progress.advance(task)
```

***REMOVED******REMOVED*** Adding New Commands

***REMOVED******REMOVED******REMOVED*** 1. Create Command Module

Create a new Python file in the `commands/` directory:

```python
***REMOVED*** commands/new_command.py
"""New command implementation."""

import logging
import typer
from rich.console import Console

from data_importer.config.logging import with_logging

console = Console()
logger = logging.getLogger(__name__)

app = typer.Typer(name="new-command", help="New command description")

@app.command()
@with_logging(log_level="INFO")
def new_subcommand():
    """New subcommand implementation."""
    console.print("[green]New command executed[/green]")
```

***REMOVED******REMOVED******REMOVED*** 2. Register in `__init__.py`

Add the new command to the module exports:

```python
***REMOVED*** commands/__init__.py
from data_importer.cli.commands import new_command

__all__ = ["shell", "interactive", "sync", "new_command"]
```

***REMOVED******REMOVED******REMOVED*** 3. Register in Main CLI

Add the command to the main CLI app:

```python
***REMOVED*** cli/__init__.py
from data_importer.cli.commands import new_command

app.add_typer(new_command.app, name="new-command")
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** 1. Type Hints

Always use comprehensive type hints:

```python
from typing import Optional, List
import typer

def command(
    items: List[str] = typer.Argument(..., help="List of items"),
    count: Optional[int] = typer.Option(None, help="Item count"),
    enabled: bool = typer.Option(False, help="Enable feature"),
) -> None:
```

***REMOVED******REMOVED******REMOVED*** 2. Help Documentation

Provide comprehensive help text:

```python
def command():
    """
    Single line summary of the command.

    Detailed description of what the command does,
    including important notes and limitations.

    Examples:
        command --option value
        command item1 item2 --flag
    """
```

***REMOVED******REMOVED******REMOVED*** 3. Configuration Defaults

Use configuration system for defaults:

```python
def command(
    limit: Optional[int] = typer.Option(
        None, "--limit", help="Limit (defaults to config value)"
    ),
):
    config = Config.get_instance()
    actual_limit = limit if limit is not None else config.default_limit
```

***REMOVED******REMOVED******REMOVED*** 4. Validation

Validate inputs early:

```python
def command(year: int):
    if year < 1900 or year > 2030:
        console.print("[red]Year must be between 1900 and 2030[/red]")
        raise typer.Exit(code=1)
```

***REMOVED******REMOVED******REMOVED*** 5. Resource Cleanup

Always clean up resources:

```python
def command():
    clients = []
    try:
        client = create_client()
        clients.append(client)
        ***REMOVED*** Use client
    finally:
        for client in clients:
            asyncio.run(client.close())
```

***REMOVED******REMOVED*** Testing Commands

***REMOVED******REMOVED******REMOVED*** Unit Tests

Test command logic separately from CLI interface:

```python
***REMOVED*** tests/test_commands.py
def test_sync_movies_logic():
    ***REMOVED*** Test the core logic without CLI
    pass

def test_sync_movies_cli():
    ***REMOVED*** Test CLI interface using typer.testing.CliRunner
    pass
```

***REMOVED******REMOVED******REMOVED*** CLI Tests

Use Typer's testing utilities:

```python
from typer.testing import CliRunner
from data_importer.cli import app

runner = CliRunner()

def test_command():
    result = runner.invoke(app, ["sync", "movies", "--help"])
    assert result.exit_code == 0
    assert "Sync movies" in result.stdout
```

***REMOVED******REMOVED*** Dependencies

Commands rely on these key dependencies:

- **Typer**: CLI framework and argument parsing
- **Rich**: Console output, progress bars, and formatting
- **Logging**: Centralized logging configuration
- **Config**: Application configuration management
- **Services**: API clients for external data sources

***REMOVED******REMOVED*** Shell Command Special Features

The shell command provides an enhanced interactive environment:

***REMOVED******REMOVED******REMOVED*** Pre-loaded Functions

- `run_async(coro)`: Execute async functions in the shell
- `load_movies_from_file()`: Bulk data loading utilities
- `save_movie()`: Database persistence helpers
- `print_json()`, `print_plain()`: Output formatters

***REMOVED******REMOVED******REMOVED*** Available Clients

- `tmdb_client`: TMDB API client with authentication
- `omdb_client`: OMDB API client for additional movie data
- `imdb_client`: IMDb scraping client for ratings

***REMOVED******REMOVED******REMOVED*** Configuration

- Multiple color themes
- Syntax highlighting toggle
- Verbose/quiet modes
- Custom data and log directories

This architecture ensures consistent, maintainable, and user-friendly CLI commands that integrate seamlessly with the application's configuration and logging systems.
