***REMOVED*** Backend API Command Line Interface

This module provides a comprehensive command-line interface (CLI) for the Backend API service, built using Typer.

***REMOVED******REMOVED*** Structure

The CLI is organized as follows:

```
backend_api/cli/
│
├── __init__.py       ***REMOVED*** Main CLI application entry point
├── __main__.py       ***REMOVED*** Entry point for direct module execution
├── README.md         ***REMOVED*** This documentation file
├── utils.py          ***REMOVED*** Utility functions for CLI commands
└── commands/         ***REMOVED*** Individual command groups
    ├── cache.py      ***REMOVED*** Cache management commands
    ├── config.py     ***REMOVED*** Configuration commands
    ├── health.py     ***REMOVED*** Health check commands
    ├── redis.py      ***REMOVED*** Redis data management commands
    ├── serve.py      ***REMOVED*** Server commands
    ├── version.py    ***REMOVED*** Version information commands
    └── __init__.py   ***REMOVED*** Command module initialization
```

***REMOVED******REMOVED*** Command Groups

- **serve**: Start and manage the Backend API server

  - `serve` or `serve start`: Start the Backend API server
  - Options: `--host`, `--port`, `--reload`, `--log-level`, `--log-dir`, `--verbose`, `--quiet`

- **health**: Health check commands for Backend API and dependent services

  - `health` or `health check`: Check Backend API health status
  - `health redis`: Check Redis health
  - `health db`: Check database health
  - Options: `--verbose`, `--timeout`

- **config**: Display and manage configuration settings

  - `config` or `config show`: Show current configuration
  - Options: `--verbose`, `--show-secrets`

- **redis**: Redis data management commands

  - `redis populate-suggestions`: Populate Redis with movie, actor, and director suggestions for autocomplete
  - Options: Various options for controlling what data gets populated

- **cache**: Redis cache management commands

  - `cache info`: Display Redis cache information
  - `cache keys`: List cache keys matching a pattern
  - `cache get`: Get value for a specific key
  - `cache delete`: Delete a specific key
  - `cache clear`: Clear cache keys matching a pattern
  - Options: Various options depending on the command

- **version**: Display version information
  - `version`: Show Backend API version
  - Options: `--verbose`

***REMOVED******REMOVED*** Installation

The CLI is installed as part of the Backend API package:

```bash
***REMOVED*** Install in development mode
cd /path/to/backend-api
pip install -e .
```

After installation, the CLI is available via:

```bash
***REMOVED*** As a console script
backend-api [COMMAND] [OPTIONS]

***REMOVED*** As a Python module
python -m backend_api.cli [COMMAND] [OPTIONS]
```

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Server Management

Start the server with default settings:

```bash
backend-api serve
```

Start with custom host and port:

```bash
backend-api serve start --host 127.0.0.1 --port 8080
```

Start in development mode with auto-reload:

```bash
backend-api serve --reload
```

***REMOVED******REMOVED******REMOVED*** Health Checks

Check the Backend API health:

```bash
backend-api health
```

Check with detailed output:

```bash
backend-api health check --verbose
```

Check Redis health:

```bash
backend-api health redis
```

Check database health:

```bash
backend-api health db --timeout 10
```

***REMOVED******REMOVED******REMOVED*** Configuration Management

Display current configuration:

```bash
backend-api config
```

Show detailed configuration:

```bash
backend-api config --verbose
```

Show configuration including secrets (use with caution):

```bash
backend-api config --show-secrets
```

***REMOVED******REMOVED******REMOVED*** Redis Data Management

Populate Redis with suggestions data:

```bash
backend-api redis populate-suggestions
```

Populate with specific limits:

```bash
backend-api redis populate-suggestions --limit 5000 --actor-limit 1000
```

Populate only movies (no actors or directors):

```bash
backend-api redis populate-suggestions --no-actors --no-directors
```

***REMOVED******REMOVED******REMOVED*** Cache Management

Display cache information:

```bash
backend-api cache info
```

Show detailed cache statistics:

```bash
backend-api cache info --verbose
```

List cache keys:

```bash
backend-api cache keys --pattern "user:*" --limit 100
```

Get a specific key value:

```bash
backend-api cache get "movie:123"
```

Delete a specific key:

```bash
backend-api cache delete "session:456" --confirm
```

Clear cache keys matching a pattern:

```bash
backend-api cache clear --pattern "temp:*" --confirm
```

***REMOVED******REMOVED******REMOVED*** Version Information

Display version information:

```bash
backend-api version
```

Show detailed version information:

```bash
backend-api version --verbose
```

***REMOVED******REMOVED*** Environment Variables

The CLI respects the following environment variables:

| Variable      | Description              | Default                  |
| ------------- | ------------------------ | ------------------------ |
| `HOST`        | Server host address      | 0.0.0.0                  |
| `PORT`        | Server port number       | 8000                     |
| `LOG_LEVEL`   | Logging level            | INFO                     |
| `ENVIRONMENT` | Environment (dev/prod)   | development              |
| `DEBUG`       | Enable debug mode        | false                    |
| `REDIS_URL`   | URL for Redis connection | redis://localhost:6379/0 |

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
4. Import and register in `commands/__init__.py`
5. Add to the main app in `__init__.py` using `app.add_typer()`

***REMOVED******REMOVED*** Best Practices

- Commands should have clear, descriptive names
- Use verb-noun format for commands (e.g., `cache clear`, `health check`)
- Provide sensible defaults for all options
- Include comprehensive help text for all commands and options
- Handle errors gracefully with appropriate exit codes
- Log information at appropriate levels

***REMOVED******REMOVED*** Shell Completion

The Backend API CLI supports shell completion for Bash, Zsh, and Fish shells.

***REMOVED******REMOVED******REMOVED*** Setup

Enable shell completion by running:

```bash
***REMOVED*** For Bash
backend-api --install-completion bash

***REMOVED*** For Zsh
backend-api --install-completion zsh

***REMOVED*** For Fish
backend-api --install-completion fish
```

Or manually by adding to your shell configuration:

```bash
***REMOVED*** Bash
eval "$(backend-api --completion bash)"

***REMOVED*** Zsh
eval "$(backend-api --completion zsh)"

***REMOVED*** Fish
backend-api --completion fish | source
```
