"""CLI commands for Schema Registry management.

This module provides commands for:
- Registering all event schemas with Schema Registry
- Listing registered schemas
- Validating schema compatibility
"""

import asyncio
import json
from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from kafka.config import KafkaConfig
from kafka.schema_registry import SchemaRegistryClient

app = typer.Typer(help="Schema Registry management commands")
console = Console()


def run_async(coro):
    """Helper to run async functions in Typer commands."""
    return asyncio.run(coro)


@app.command()
def register(
    schema_dir: Path = typer.Option(
        Path("schemas"),
        "--schema-dir",
        "-d",
        help="Directory containing .avsc schema files",
        exists=False,
    ),
    registry_url: str = typer.Option(
        "http://localhost:8081",
        "--registry-url",
        "-u",
        help="Schema Registry URL",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be registered without actually registering",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip compatibility checks during registration",
    ),
):
    """Register all .avsc schemas from a directory with Schema Registry.

    This command reads all .avsc files from the specified directory and
    registers them with Schema Registry. Each schema is registered under
    a subject following the pattern: <event_type>-value

    Example:
        kafka-schemas register
        kafka-schemas register --schema-dir /path/to/schemas
        kafka-schemas register --dry-run
    """

    async def _register():
        # Find schema directory (look for it in parent dirs if not found)
        search_path = schema_dir if schema_dir.is_absolute() else Path.cwd() / schema_dir

        # Try to find schemas directory by walking up
        if not search_path.exists():
            current = Path.cwd()
            for _ in range(5):  # Search up to 5 levels
                test_path = current / "schemas"
                if test_path.exists() and test_path.is_dir():
                    search_path = test_path
                    break
                current = current.parent

        if not search_path.exists():
            console.print(f"[red]Schema directory not found: {schema_dir}[/red]")
            console.print("[yellow]Searched locations:[/yellow]")
            console.print(f"  - {schema_dir}")
            console.print(f"  - {Path.cwd() / 'schemas'}")
            raise typer.Exit(code=1)

        # Find all .avsc files
        schema_files = list(search_path.glob("*.avsc"))

        if not schema_files:
            console.print(f"[yellow]No .avsc files found in {search_path}[/yellow]")
            return

        console.print(f"[cyan]Found {len(schema_files)} schema files in {search_path}[/cyan]\n")

        # Create config with custom registry URL
        config = KafkaConfig(schema_registry_url=registry_url)
        config.check_schema_compatibility = not force

        client = SchemaRegistryClient(config)
        await client.start()

        if dry_run:
            console.print("[yellow]DRY RUN MODE - No schemas will be registered[/yellow]\n")

        # Create results table
        table = Table(title="Schema Registration Results")
        table.add_column("Event Type", style="cyan")
        table.add_column("Subject", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Schema ID", style="yellow")

        registered_count = 0
        failed_count = 0

        for avsc_file in sorted(schema_files):
            # Extract event type from filename
            # e.g., "user.registered.v1.avsc" → "user.registered"
            event_type = (
                avsc_file.stem.rsplit(".v", 1)[0] if ".v" in avsc_file.stem else avsc_file.stem
            )
            subject = f"{event_type}-value"

            try:
                # Load schema from file
                with open(avsc_file) as f:
                    schema = json.load(f)

                if dry_run:
                    # Just show what would be registered
                    table.add_row(event_type, subject, "Would register", "N/A")
                    registered_count += 1
                else:
                    # Actually register the schema
                    schema_id = await client.register_schema(subject, schema)
                    table.add_row(
                        event_type,
                        subject,
                        "✓ Registered",
                        str(schema_id),
                    )
                    registered_count += 1
            except json.JSONDecodeError as e:
                table.add_row(
                    event_type,
                    subject,
                    f"✗ Invalid JSON: {str(e)[:30]}",
                    "N/A",
                )
                failed_count += 1
            except Exception as e:
                table.add_row(
                    event_type,
                    subject,
                    f"✗ Failed: {str(e)[:40]}",
                    "N/A",
                )
                failed_count += 1

        console.print(table)
        console.print()

        if dry_run:
            console.print(f"[yellow]Would register {registered_count} schemas[/yellow]")
        else:
            console.print(f"[green]Successfully registered {registered_count} schemas[/green]")
            if failed_count > 0:
                console.print(f"[red]Failed to register {failed_count} schemas[/red]")

        await client.close()

    run_async(_register())


@app.command()
def list_schemas(
    registry_url: str = typer.Option(
        "http://localhost:8081",
        "--registry-url",
        "-u",
        help="Schema Registry URL",
    ),
    subject: str | None = typer.Option(
        None,
        "--subject",
        "-s",
        help="Filter by subject pattern",
    ),
):
    """List all registered schemas in Schema Registry.

    Example:
        kafka-schemas list-schemas
        kafka-schemas list-schemas --subject user.registered-value
    """

    async def _list_schemas():
        config = KafkaConfig(schema_registry_url=registry_url)
        client = SchemaRegistryClient(config)
        await client.start()

        try:
            # Get all subjects
            subjects = await client.list_subjects()

            if subject:
                subjects = [s for s in subjects if subject in s]

            if not subjects:
                console.print("[yellow]No schemas found[/yellow]")
                return

            # Create results table
            table = Table(title="Registered Schemas")
            table.add_column("Subject", style="cyan")
            table.add_column("Version", style="magenta")
            table.add_column("Schema ID", style="yellow")
            table.add_column("Schema Type", style="green")

            for subj in subjects:
                try:
                    # Get schema metadata from the registry response
                    response = await client._client.get(f"/subjects/{subj}/versions/latest")
                    data = response.json()
                    table.add_row(
                        subj,
                        str(data.get("version", "?")),
                        str(data.get("id", "?")),
                        "AVRO",
                    )
                except Exception as e:
                    table.add_row(
                        subj,
                        "Error",
                        "N/A",
                        f"Failed: {str(e)[:30]}",
                    )

            console.print(table)
            console.print(f"\n[green]Total subjects: {len(subjects)}[/green]")

        except Exception as e:
            console.print(f"[red]Error listing schemas: {e}[/red]")
            raise typer.Exit(code=1)
        finally:
            await client.close()

    run_async(_list_schemas())


@app.command()
def validate(
    event_type: str = typer.Argument(..., help="Event type to validate"),
    schema_dir: Path = typer.Option(
        Path("schemas"),
        "--schema-dir",
        "-d",
        help="Directory containing .avsc schema files",
    ),
    registry_url: str = typer.Option(
        "http://localhost:8081",
        "--registry-url",
        "-u",
        help="Schema Registry URL",
    ),
    show_schema: bool = typer.Option(
        False,
        "--show-schema",
        "-s",
        help="Display the full schema",
    ),
):
    """Validate schema compatibility for an event type.

    Checks if the local .avsc schema file is compatible with
    the version registered in Schema Registry.

    Example:
        kafka-schemas validate user.registered
        kafka-schemas validate movie.viewed --show-schema
    """

    async def _validate():
        # Find schema directory
        search_path = schema_dir if schema_dir.is_absolute() else Path.cwd() / schema_dir

        if not search_path.exists():
            current = Path.cwd()
            for _ in range(5):
                test_path = current / "schemas"
                if test_path.exists():
                    search_path = test_path
                    break
                current = current.parent

        if not search_path.exists():
            console.print(f"[red]Schema directory not found: {schema_dir}[/red]")
            raise typer.Exit(code=1)

        # Find the schema file for this event type
        schema_files = list(search_path.glob(f"{event_type}*.avsc"))

        if not schema_files:
            console.print(f"[red]Error: No .avsc file found for '{event_type}'[/red]")
            console.print(f"[yellow]Searched in: {search_path}[/yellow]")
            raise typer.Exit(code=1)

        schema_file = schema_files[0]  # Take first match

        # Load local schema
        with open(schema_file) as f:
            local_schema = json.load(f)

        config = KafkaConfig(schema_registry_url=registry_url)
        client = SchemaRegistryClient(config)
        await client.start()

        subject = f"{event_type}-value"

        try:
            # Get latest schema from registry
            registered_schema = await client.get_latest_schema(subject)

            # Get metadata
            response = await client._client.get(f"/subjects/{subject}/versions/latest")
            data = response.json()
            version = data.get("version")
            schema_id = data.get("id")

            console.print("[green]✓ Schema found in registry[/green]")
            console.print(f"  Subject: {subject}")
            console.print(f"  Version: {version}")
            console.print(f"  Schema ID: {schema_id}")
            console.print(f"  Local file: {schema_file.name}")

            # Compare schemas
            if local_schema == registered_schema:
                console.print("\n[green]✓ Local schema matches registered schema[/green]")
            else:
                console.print("\n[yellow]⚠ Local schema differs from registered schema[/yellow]")
                console.print(
                    "[yellow]This may be a new version. Consider updating the schema.[/yellow]"
                )

            if show_schema:
                console.print("\n[cyan]Registered Schema:[/cyan]")
                rprint(json.dumps(registered_schema, indent=2))

                console.print("\n[cyan]Local Schema:[/cyan]")
                rprint(json.dumps(local_schema, indent=2))

        except Exception as e:
            if "not found" in str(e).lower():
                console.print(f"[yellow]Schema not yet registered for '{event_type}'[/yellow]")
                console.print(
                    "[yellow]Run 'kafka-schemas register' to register all schemas[/yellow]"
                )
            else:
                console.print(f"[red]Error validating schema: {e}[/red]")
            raise typer.Exit(code=1)
        finally:
            await client.close()

    run_async(_validate())


@app.command()
def show(
    event_type: str = typer.Argument(..., help="Event type to display"),
    schema_dir: Path = typer.Option(
        Path("schemas"),
        "--schema-dir",
        "-d",
        help="Directory containing .avsc schema files",
    ),
):
    """Show the Avro schema for an event type from .avsc file.

    Example:
        kafka-schemas show user.registered
        kafka-schemas show movie.viewed
    """
    # Find schema directory
    search_path = schema_dir if schema_dir.is_absolute() else Path.cwd() / schema_dir

    if not search_path.exists():
        current = Path.cwd()
        for _ in range(5):
            test_path = current / "schemas"
            if test_path.exists():
                search_path = test_path
                break
            current = current.parent

    if not search_path.exists():
        console.print(f"[red]Schema directory not found: {schema_dir}[/red]")
        raise typer.Exit(code=1)

    # Find the schema file
    schema_files = list(search_path.glob(f"{event_type}*.avsc"))

    if not schema_files:
        console.print(f"[red]Error: No .avsc file found for '{event_type}'[/red]")
        console.print(f"[yellow]Available schemas in {search_path}:[/yellow]")
        for schema_path in search_path.glob("*.avsc"):
            et = (
                schema_path.stem.rsplit(".v", 1)[0]
                if ".v" in schema_path.stem
                else schema_path.stem
            )
            console.print(f"  - {et}")
        raise typer.Exit(code=1)

    schema_file = schema_files[0]

    # Load and display schema
    with open(schema_file) as f:
        schema = json.load(f)

    console.print(f"[cyan]Schema for event type: {event_type}[/cyan]")
    console.print(f"[dim]File: {schema_file}[/dim]\n")
    rprint(json.dumps(schema, indent=2))


if __name__ == "__main__":
    app()
