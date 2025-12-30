# Recommendation API CLI Commands

This directory contains the various command modules for the Recommendation API CLI.

## Command Modules

- `serve.py`: Commands for running the API server
- `config.py`: Configuration management commands
- `health.py`: Health check commands
- `embeddings.py`: Commands for working with movie embeddings
- `debug.py`: Debugging and diagnostic tools
- `cache.py`: Cache management commands
- `ml.py`: ML API integration commands

## ML Commands

The `ml.py` module provides commands for interacting with the ML API service:

- `test-connection`: Test connectivity to the ML API
- `generate-embedding`: Generate a vector embedding for a movie

### Example Usage

Test the connection to the ML API:

```bash
python -m recommendation_api.cli.main ml test-connection
```

Generate an embedding for a test movie:

```bash
python -m recommendation_api.cli.main ml generate-embedding "The Matrix" "A computer hacker learns about the true nature of reality" --genres "Action,Sci-Fi"
```

## Adding New Commands

To add a new command module:

1. Create a new Python file in this directory
2. Define a Typer app instance in your module
3. Add your command functions with appropriate decorators
4. Import your module in `__init__.py`
5. Add your app to the main CLI in `main.py`
