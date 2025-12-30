"""Command-line interface package."""

import typer

# Create main app
app = typer.Typer(
    help="Backend API Management CLI",
    add_completion=False,
)

# Create command groups
db_app = typer.Typer(help="Database management commands")
health_app = typer.Typer(help="Health check commands")
cache_app = typer.Typer(help="Cache management commands")

# Register command groups
app.add_typer(db_app, name="db")
app.add_typer(health_app, name="health")
app.add_typer(cache_app, name="cache")

# Import commands to register them with the Typer apps via side effects.
# This keeps `python -m backend_api.cli db ...` working.
from backend_api.cli import commands as _commands  # noqa: F401,E402

# Make apps available for importing
__all__ = ["app", "db_app", "health_app", "cache_app"]
