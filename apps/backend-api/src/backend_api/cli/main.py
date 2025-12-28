"""Main CLI entry point for backend API service."""

import sys

from rich.traceback import install

from backend_api.cli import app

***REMOVED*** Install rich traceback handler
install()


def main() -> None:
    """Main entry point for the backend API CLI."""
    try:
        app()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
