***REMOVED*** BFF API Command Line Interface

This module provides a comprehensive command-line interface (CLI) for the BFF API service, built using Typer.

***REMOVED******REMOVED*** Structure

The CLI is organized as follows:

```
bff_api/cli/
│
├── main.py           ***REMOVED*** Main CLI application entry point
├── __init__.py       ***REMOVED*** Package initialization
├── utils.py          ***REMOVED*** Utility functions for CLI commands
└── commands/         ***REMOVED*** Individual command groups
    ├── serve.py      ***REMOVED*** Server commands
    ├── health.py     ***REMOVED*** Health check commands
    ├── cache.py      ***REMOVED*** Cache management commands
    └── __init__.py   ***REMOVED*** Command module initialization
```

***REMOVED******REMOVED*** Command Groups

- **serve**: Commands for starting and managing the BFF API server
  - `serve` or `serve start`: Start the BFF API server
- **health**: Health check commands for BFF and dependent services
  - `health check`: Check health of all services
  - `health backend`: Check Backend API health
  - `health auth`: Check Auth API health
- **cache**: Redis cache management commands
  - `cache info`: Display Redis cache information
  - `cache keys`: List cache keys
  - `cache clear`: Clear cache keys
  - `cache get`: Get value for a specific key
  - `cache delete`: Delete a specific key
- **config**: Display current configuration
  - `config --verbose`: Show detailed configuration
  - `config --show-secrets`: Show sensitive configuration values
- **version**: Show BFF API version information

***REMOVED******REMOVED*** Usage

Run the CLI using the module format:

```bash
***REMOVED*** Using the Python module approach (recommended)
PYTHONPATH=src python -m bff_api.cli.main [COMMAND] [OPTIONS]

***REMOVED*** Examples:
PYTHONPATH=src python -m bff_api.cli.main version
PYTHONPATH=src python -m bff_api.cli.main serve
PYTHONPATH=src python -m bff_api.cli.main health check --verbose
PYTHONPATH=src python -m bff_api.cli.main config --verbose
```

For development with auto-reload:

```bash
PYTHONPATH=src python -m bff_api.cli.main serve --reload
```

***REMOVED******REMOVED*** Design Principles

1. **Command Structure**: Commands are organized into logical groups with consistent naming
2. **Sensible Defaults**: Primary commands work without arguments and use sensible defaults
3. **Rich Output**: User-friendly console output with color and formatting
4. **Environment Variables**: Support for configuration via environment variables
5. **Type Safety**: Full type annotations for reliability and maintainability
6. **Comprehensive Help**: Detailed help text for all commands and options
7. **Error Handling**: Robust error reporting and appropriate exit codes

***REMOVED******REMOVED*** Extending the CLI

To add new command groups or commands:

1. Create a new module in the `commands/` directory
2. Define a `typer.Typer` app in the module
3. Add command functions using `@app.command()`
4. Import and register in `main.py` using `app.add_typer()`

***REMOVED******REMOVED*** Best Practices

- Commands should have clear, descriptive names
- Use verb-noun format for commands (e.g., `cache clear`, `health check`)
- Provide sensible defaults for all options
- Include comprehensive help text for all commands and options
- Handle errors gracefully with appropriate exit codes
- Log information at appropriate levels
