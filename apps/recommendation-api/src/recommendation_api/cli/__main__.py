"""Main entry point for CLI when executed as a module."""

from recommendation_api.cli.main import app as cli_app


if __name__ == "__main__":
    cli_app() 