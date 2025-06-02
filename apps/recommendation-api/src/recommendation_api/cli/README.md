***REMOVED*** Recommendation API CLI

Command-line interface for managing the Recommendation API service.

***REMOVED******REMOVED*** Overview

The CLI provides a set of commands for managing the Recommendation API service, including server management, configuration, and health checks. It uses Typer for command-line argument parsing and Rich for enhanced console output.

***REMOVED******REMOVED*** Installation

The CLI is installed as part of the Recommendation API package:

```bash
pip install recommendation-api
```

***REMOVED******REMOVED*** Usage

The CLI is accessible through the `rec-api` command:

```bash
rec-api [COMMAND] [OPTIONS]
```

***REMOVED******REMOVED******REMOVED*** Available Commands

***REMOVED******REMOVED******REMOVED******REMOVED*** Server Management

```bash
***REMOVED*** Start the server
rec-api serve start [--host HOST] [--port PORT] [--reload] [--log-level LEVEL] [--verbose] [--quiet]

***REMOVED*** Stop the server
rec-api serve stop

***REMOVED*** Restart the server
rec-api serve restart
```

Options for `serve start`:

- `--host`: Host address to bind to (default from config)
- `--port`: Port number to bind to (default from config)
- `--reload`: Enable auto-reload for development
- `--log-level`: Set log level (DEBUG, INFO, WARNING, ERROR)
- `--verbose`: Enable verbose logging
- `--quiet`: Suppress console output except errors

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration Management

```bash
***REMOVED*** Show current configuration
rec-api config show [--show-secrets] [--verbose]

***REMOVED*** Validate configuration
rec-api config validate

***REMOVED*** Show environment-specific settings
rec-api config env
```

Options for `config show`:

- `--show-secrets`: Display sensitive configuration values
- `--verbose`: Show detailed configuration information

***REMOVED******REMOVED******REMOVED******REMOVED*** Health Checks

```bash
***REMOVED*** Check health of all services
rec-api health check

***REMOVED*** Ping specific service
rec-api health ping SERVICE
```

Available services for `health ping`:

- `api`: Recommendation API service
- `db`: Database service
- `qdrant`: Vector database service

***REMOVED******REMOVED******REMOVED******REMOVED*** Version Information

```bash
***REMOVED*** Show version information
rec-api version
```

***REMOVED******REMOVED*** Module Structure

```
cli/
├── __init__.py          ***REMOVED*** Package initialization
├── main.py             ***REMOVED*** Main CLI application
├── utils.py            ***REMOVED*** Utility functions
└── commands/           ***REMOVED*** Command modules
    ├── __init__.py     ***REMOVED*** Commands package
    ├── serve.py        ***REMOVED*** Server management commands
    ├── config.py       ***REMOVED*** Configuration commands
    └── health.py       ***REMOVED*** Health check commands
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Adding New Commands

1. Create a new command module in `commands/`
2. Define a Typer app instance
3. Add command functions with proper type hints and docstrings
4. Import and add the command module in `main.py`

Example:

```python
***REMOVED*** commands/new_command.py
import typer

app = typer.Typer(name="new-command")

@app.command()
def do_something() -> None:
    """Do something."""
    pass

***REMOVED*** main.py
from recommendation_api.cli.commands import new_command
app.add_typer(new_command.app, name="new-command")
```

***REMOVED******REMOVED******REMOVED*** Utility Functions

Common utility functions are available in `utils.py`:

- `format_config_table()`: Format configuration as Rich table
- `print_config()`: Display configuration settings
- `check_service_health()`: Check service health status
- `display_service_status()`: Show service status table
- `configure_logging()`: Set up logging
- `print_error()`: Display error messages
- `print_success()`: Display success messages

***REMOVED******REMOVED*** Error Handling

The CLI uses consistent error handling:

1. All commands catch exceptions and display user-friendly error messages
2. Rich console output for better readability
3. Proper logging of errors for debugging
4. Exit codes for script integration

***REMOVED******REMOVED*** Contributing

1. Follow the Google Python Style Guide
2. Add type hints to all functions
3. Include docstrings for all public functions
4. Add tests for new functionality
5. Update this README for new features
