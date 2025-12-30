# Backend API Command Line Interface

This module provides a comprehensive command-line interface (CLI) for the Backend API service, built using Typer.

## Structure

The CLI is organized as follows:

```Text
backend_api/cli/
│
├── __init__.py       # Main CLI application entry point
├── __main__.py       # Entry point for direct module execution
├── README.md         # This documentation file
├── utils.py          # Utility functions for CLI commands
└── commands/         # Individual command groups
    ├── cache.py      # Cache management commands
    ├── config.py     # Configuration commands
    ├── database.py   # Database management commands (consolidated)
    ├── health.py     # Health check commands
    ├── redis.py      # Redis data management commands
    ├── serve.py      # Server commands
    ├── version.py    # Version information commands
    └── __init__.py   # Command module initialization
```

## Command Structure

The CLI follows a clean, flat structure with logical grouping:

### Top-Level Commands

- `config` - Display and manage configuration settings
- `serve` - Start the Backend API server
- `version` - Display version information

### Command Groups

- `db` - Database management commands
- `health` - Health check commands
- `cache` - Cache management commands

## Command Groups

- **db**: Database management commands

  - `db init`: Initialize the database and optionally create tables
  - `db migrate`: Run database migrations to update schema
  - `db downgrade`: Downgrade database migrations
  - `db teardown`: Teardown database (DEVELOPMENT ONLY - destroys all data!)
  - Options: Various options for database URL, verbosity, confirmation, etc.

- **health**: Health check commands for Backend API and dependent services

  - `health`: Check Backend API health status (default command)
  - `health check`: Explicit health check command
  - `health redis`: Check Redis health
  - `health db`: Check database health
  - Options: `--verbose`, `--timeout`

- **cache**: Cache management commands

  - `cache info`: Display Redis cache information
  - `cache keys`: List cache keys matching a pattern
  - `cache get`: Get value for a specific key
  - `cache delete`: Delete a specific key
  - `cache clear`: Clear cache keys matching a pattern
  - Options: Various options depending on the command

- **config**: Display and manage configuration settings

  - `config`: Show current configuration (default)
  - Options: `--verbose`, `--show-secrets`

- **serve**: Start and manage the Backend API server

  - `serve`: Start the Backend API server
  - Options: `--host`, `--port`, `--reload`, `--log-level`, `--log-dir`, `--verbose`, `--quiet`

- **version**: Display version information
  - `version`: Show Backend API version
  - Options: `--verbose`

## Installation

The CLI is installed as part of the Backend API package:

```bash
# Install in development mode
cd /path/to/backend-api
pip install -e .
```

After installation, the CLI is available via:

```bash
# As a console script
backend-api [COMMAND] [OPTIONS]

# As a Python module
python -m backend_api.cli [COMMAND] [OPTIONS]
```

## Usage Examples

### Database Management

Initialize the database:

```bash
backend-api db init
```

Initialize with table creation:

```bash
backend-api db init --create-tables
```

Run database migrations:

```bash
backend-api db migrate
```

Run migrations with verbose output:

```bash
backend-api db migrate --verbose
```

Downgrade the last migration:

```bash
backend-api db downgrade
```

Downgrade multiple migrations:

```bash
backend-api db downgrade --steps 3
```

Downgrade to a specific migration:

```bash
backend-api db downgrade --target 005_add_ratings_and_awards
```

Downgrade all migrations:

```bash
backend-api db downgrade --all --confirm
```

Teardown database (development only):

```bash
backend-api db teardown --confirm
```

### Server Management

Start the server with default settings:

```bash
backend-api serve
```

Start with custom host and port:

```bash
backend-api serve --host 127.0.0.1 --port 8080
```

Start in development mode with auto-reload:

```bash
backend-api serve --reload
```

### Health Checks

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

### Configuration Management

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

### Cache Management

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

### Version Information

Display version information:

```bash
backend-api version
```

Show detailed version information:

```bash
backend-api version --verbose
```

## Environment Variables

The CLI respects the following environment variables:

| Variable       | Description               | Default                                     |
| -------------- | ------------------------- | ------------------------------------------- |
| `HOST`         | Server host address       | 0.0.0.0                                     |
| `PORT`         | Server port number        | 8000                                        |
| `LOG_LEVEL`    | Logging level             | INFO                                        |
| `ENVIRONMENT`  | Environment (dev/prod)    | development                                 |
| `DEBUG`        | Enable debug mode         | false                                       |
| `DATABASE_URL` | PostgreSQL connection URL | postgresql://alex@localhost:5432/next_watch |
| `REDIS_URL`    | URL for Redis connection  | redis://localhost:6379/0                    |

## Design Principles

1. **Flat Command Structure**: Minimal nesting for intuitive usage
2. **Logical Grouping**: Related commands grouped under clear namespaces
3. **Sensible Defaults**: Primary commands work without arguments and use sensible defaults
4. **Rich Output**: User-friendly console output with color and formatting
5. **Environment Variables**: Support for configuration via environment variables
6. **Type Safety**: Full type annotations for reliability and maintainability
7. **Comprehensive Help**: Detailed help text for all commands and options
8. **Error Handling**: Robust error reporting and appropriate exit codes
9. **Consolidated Commands**: Related functionality is grouped in single files for better maintainability

## Database Commands Details

The database commands provide comprehensive database management functionality:

### Database Initialization

- Creates database connection
- Optionally creates all tables
- Supports custom database URLs
- Provides verbose output for debugging

### Database Migrations

- Applies pending migrations in sequence
- Tracks applied migrations in database
- Shows detailed migration information
- Supports custom database URLs

### Database Downgrades

- Supports single or multiple migration downgrades
- Can target specific migrations
- Provides confirmation prompts for safety
- Shows detailed downgrade information
- Supports downgrading all migrations

### Database Teardown

- **DEVELOPMENT ONLY** - Destroys all data
- Multiple confirmation prompts for safety
- Environment-aware (blocks production by default)
- Complete schema reset functionality

## Extending the CLI

To add new command groups or commands:

### Adding Top-Level Commands

1. Create a new module in the `commands/` directory
2. Define command functions using `@app.command()`
3. Register directly with main app: `main_app.command("name")(function)`
4. Import in `commands/__init__.py`

### Adding Command Groups

1. Create a new module in the `commands/` directory
2. Define command functions using `@app.command()`
3. Add new command group to `cli/__init__.py`: `group_app = typer.Typer(...)`
4. Register commands with group: `group_app.command("name")(function)`
5. Register group with main app: `app.add_typer(group_app, name="group")`
6. Import in `commands/__init__.py`

### Adding Database Commands

For database commands specifically, add new commands directly to the existing `database.py` file and register them with `db_app.command()`.

## Best Practices

- Commands should have clear, descriptive names
- Use verb-noun format for commands (e.g., `cache clear`, `health check`)
- Provide sensible defaults for all options
- Include comprehensive help text for all commands and options
- Handle errors gracefully with appropriate exit codes
- Log information at appropriate levels
- Consolidate related functionality in single files when appropriate
- Use confirmation prompts for destructive operations
- Keep command structure flat and intuitive
- Avoid unnecessary nesting (e.g., avoid `cache cache info`)

## Shell Completion

The Backend API CLI supports shell completion for Bash, Zsh, and Fish shells.

### Setup

Enable shell completion by running:

```bash
# For Bash
backend-api --install-completion bash

# For Zsh
backend-api --install-completion zsh

# For Fish
backend-api --install-completion fish
```

Or manually by adding to your shell configuration:

```bash
# Bash
eval "$(backend-api --completion bash)"

# Zsh
eval "$(backend-api --completion zsh)"

# Fish
backend-api --completion fish | source
```
