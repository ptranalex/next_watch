from typing import Any, Dict, List, Optional, Union

"""
Database setup and migration script.
"""

import os

import typer
from typer import Typer

from backend_api.config import settings
from backend_api.db import init_db
from backend_api.db.database import check_database_schema
from backend_api.db.migrations import run_migration
from backend_api.utils import setup_backend_api_storage

app: Typer = typer.Typer()


@app.command()
def initialize_db(create_tables: bool = False) -> None:
    """
    Initialize the database connection.

    Args:
        create_tables: Whether to create tables in the database
    """
    config = settings
    masked_url = config.get_database_url_masked()
    typer.echo(f"Initializing database connection to: {masked_url}")
    init_db(create_tables=create_tables, config=config)
    typer.echo("Database connection initialized successfully!")


@app.command()
def run_migrations() -> None:
    """
    Run database migrations using Alembic.
    """
    config = settings
    typer.echo("Running database migrations...")
    run_migration(config.database_url)
    typer.echo("Migrations completed successfully!")


@app.command()
def setup_storage() -> None:
    """
    Setup movie storage with initial configuration.

    This will initialize the database and create any necessary tables.
    """
    config = settings
    typer.echo("Setting up movie storage...")
    setup_backend_api_storage(database_url=config.database_url, create_tables=True)
    typer.echo("Movie storage setup completed!")


@app.command("check-schema")
def check_schema() -> None:
    """
    Check if the database schema is properly set up.

    This command verifies that all required tables exist.
    """
    config = settings
    masked_url = config.get_database_url_masked()
    typer.echo(f"🔍 Checking database schema on: {masked_url}")

    try:
        result = check_database_schema(config)

        if result["schema_ready"]:
            typer.echo("✅ Database schema is ready!")
            typer.echo(f"   Found {len(result['existing_tables'])} tables")
        else:
            if "error" in result:
                typer.echo(f"❌ Schema check failed: {result['error']}")
                raise typer.Exit(1)
            else:
                typer.echo("⚠️  Database schema is incomplete!")
                typer.echo(f"   Missing tables: {', '.join(result['missing_tables'])}")
                typer.echo()
                typer.echo("💡 Run migrations to set up the schema:")
                typer.echo("   python -m backend_api.scripts.setup_db run-migrations")
                raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Schema check failed: {e}")
        raise typer.Exit(1)


@app.command("profile-db")
def profile_database(duration: int = 30) -> None:
    """
    Profile database queries for a running application (development only).

    This command enables query profiling and monitors database activity.
    Profiling is automatically disabled in production environments.

    Args:
        duration: How long to profile in seconds (default: 30)
    """
    try:
        from backend_api.db.profiler import DatabaseProfiler

        config = settings

        ***REMOVED*** Check if profiling is available
        if config.is_production:
            typer.echo("❌ Database profiling is not available in production")
            typer.echo("   This is disabled for security and performance reasons")
            raise typer.Exit(1)

        if not config.enable_db_profiling:
            typer.echo("❌ Database profiling is disabled")
            typer.echo("   Set ENABLE_DB_PROFILING=true in your environment to enable")
            raise typer.Exit(1)

        masked_url = config.get_database_url_masked()
        profiler = DatabaseProfiler()

        typer.echo(f"🔬 Starting database profiling for {duration} seconds")
        typer.echo(f"🔗 Database: {masked_url}")
        typer.echo(f"🚀 Environment: {config.environment}")
        typer.echo(f"⚡ Slow query threshold: {config.db_profiling_slow_query_threshold_ms}ms")

        if not profiler.start():
            typer.echo("❌ Failed to start profiling")
            raise typer.Exit(1)

        typer.echo()
        typer.echo("💡 Make API requests now to capture queries!")
        typer.echo("   Example requests:")
        typer.echo("   curl 'http://localhost:8000/api/v1/movies?limit=10'")
        typer.echo("   curl 'http://localhost:8000/api/v1/movies/1'")
        typer.echo("   curl 'http://localhost:8000/health'")
        typer.echo()

        ***REMOVED*** Monitor for the specified duration
        import time

        start_time = time.time()
        last_count = 0

        while time.time() - start_time < duration:
            current_queries = profiler.get_profile_report()["total_queries"]
            if current_queries != last_count:
                typer.echo(f"📊 Captured {current_queries} queries...", nl=False)
                typer.echo("\r", nl=False)
                last_count = current_queries
            time.sleep(1)

        ***REMOVED*** Stop profiling and show results
        profiler.stop()
        report = profiler.get_profile_report()

        typer.echo()
        if report["total_queries"] > 0:
            typer.echo(f"✅ {report['summary']}")
            typer.echo(f"📈 Total query time: {report['total_duration_ms']:.2f}ms")
            typer.echo(f"📈 Average query time: {report['average_duration_ms']:.2f}ms")

            if report["slow_queries"] > 0:
                typer.echo(
                    f"🐌 Slow queries (>{report['slow_query_threshold_ms']}ms): {report['slow_queries']}"
                )
                for i, query in enumerate(report["slow_query_details"][:3], 1):
                    short_sql = (
                        query["sql"][:60] + "..." if len(query["sql"]) > 60 else query["sql"]
                    )
                    typer.echo(f"   {i}. {query['duration_ms']:.2f}ms: {short_sql}")

            ***REMOVED*** Save detailed report
            import json

            timestamp = int(time.time())
            filename = f"db_profile_{timestamp}.json"

            with open(filename, "w") as f:
                json.dump(report, f, indent=2)

            typer.echo(f"📄 Detailed report saved to: {filename}")

            ***REMOVED*** Print formatted report to console
            typer.echo()
            typer.echo("📋 Quick Report:")
            profiler.print_report()
        else:
            typer.echo("📭 No queries captured!")
            typer.echo("💡 Make sure your API is running and receiving requests")

    except Exception as e:
        typer.echo(f"❌ Profiling failed: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
