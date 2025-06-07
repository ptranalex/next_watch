***REMOVED*** BFF API Command Line Interface

This module provides a comprehensive command-line interface (CLI) for the BFF API service, built using Typer.

***REMOVED******REMOVED*** Structure

The CLI is organized as follows:

```
bff_api/cli/
│
├── main.py           ***REMOVED*** Main CLI application entry point
├── __main__.py       ***REMOVED*** Entry point for direct module execution
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

***REMOVED******REMOVED*** Installation

The CLI is installed as part of the BFF API package:

```bash
***REMOVED*** Install in development mode
cd /path/to/bff-api
pip install -e .
```

After installation, the CLI is available via:

```bash
***REMOVED*** As a console script
bff-api [COMMAND] [OPTIONS]

***REMOVED*** As a Python module
python -m bff_api.cli [COMMAND] [OPTIONS]
```

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Server Management

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

***REMOVED******REMOVED******REMOVED*** Health Checks

Check health of all services:

```bash
bff-api health check
```

Check with detailed output:

```bash
bff-api health check --verbose
```

Check specific backend service:

```bash
bff-api health backend --timeout 10
```

***REMOVED******REMOVED******REMOVED*** Cache Management

Display cache information:

```bash
bff-api cache info --verbose
```

List all cache keys:

```bash
bff-api cache keys --pattern "user:*" --limit 50
```

Clear specific cache keys:

```bash
bff-api cache clear --pattern "movie:*" --confirm
```

***REMOVED******REMOVED******REMOVED*** Configuration

Display current configuration:

```bash
bff-api config
```

Show detailed configuration:

```bash
bff-api config --verbose
```

***REMOVED******REMOVED*** Environment Variables

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
| `REDIS_URL`       | URL for Redis connection    | redis://localhost:6379/0 |

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

***REMOVED******REMOVED*** Shell Completion

The BFF API CLI supports shell completion for Bash, Zsh, and Fish shells. This enables tab-completion for commands, options, and their values.

***REMOVED******REMOVED******REMOVED*** Installation

To enable shell completion, run one of the following commands based on your shell:

***REMOVED******REMOVED******REMOVED******REMOVED*** Automatic Setup

Use the provided setup script to automatically configure shell completion:

```bash
***REMOVED*** From the project root
./scripts/setup_completion.sh
```

This will detect your shell and add the appropriate completion configuration to your shell's config file.

***REMOVED******REMOVED******REMOVED******REMOVED*** Manual Setup

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** Bash

```bash
***REMOVED*** Add to your ~/.bashrc file
eval "$(bff-api --completion bash)"

***REMOVED*** Or temporarily enable for current session
source <(bff-api --completion bash)
```

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** Zsh

```bash
***REMOVED*** Add to your ~/.zshrc file
eval "$(bff-api --completion zsh)"

***REMOVED*** Or temporarily enable for current session
source <(bff-api --completion zsh)
```

***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED*** Fish

```bash
***REMOVED*** Add to your ~/.config/fish/config.fish
bff-api --completion fish | source

***REMOVED*** Or temporarily enable for current session
bff-api --completion fish | source
```

***REMOVED******REMOVED******REMOVED*** Usage

Once shell completion is set up, you can use tab completion:

```bash
***REMOVED*** Press Tab to see available commands
bff-api [TAB]

***REMOVED*** Press Tab to see subcommands
bff-api health [TAB]

***REMOVED*** Press Tab to see options
bff-api serve --[TAB]
```

This makes it easier to discover and use CLI commands without having to refer to the help documentation.
