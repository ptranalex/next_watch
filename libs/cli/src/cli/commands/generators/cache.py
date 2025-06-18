"""Cache command generator.

Generates Redis cache management commands following the proven patterns from
Backend API CLI with info, keys, get, delete, and clear functionality.
"""

import asyncio
from typing import Optional, List, Callable, Awaitable, Any
import typer
from rich.table import Table
from rich.console import Console

from ...output.handler import CLIOutput, get_cli_output
from ...async_utils import run_with_retries, with_progress


def create_cache_commands(
    get_redis_client: Callable[[], Awaitable[Any]], command_name: str = "cache"
) -> typer.Typer:
    """Create cache management commands following Backend API patterns.

    Args:
        get_redis_client: Async function that returns a Redis client
        command_name: Name for the command group

    Returns:
        Typer app with cache management commands

    Example:
        >>> cache_app = create_cache_commands(
        ...     lambda: get_redis_client(),
        ...     command_name="cache"
        ... )
        >>> main_app.add_typer(cache_app, name="cache")
    """
    app = typer.Typer(name=command_name, help="Cache management commands.")

    @app.command()
    def info(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed cache information"
        )
    ) -> None:
        """Display Redis cache information and statistics."""
        asyncio.run(_cache_info(verbose))

    @app.command()
    def keys(
        pattern: str = typer.Option(
            "*", "--pattern", "-p", help="Key pattern to match"
        ),
        limit: int = typer.Option(
            100, "--limit", "-l", help="Maximum number of keys to display"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed output"
        ),
    ) -> None:
        """List cache keys matching a pattern."""
        asyncio.run(_cache_keys(pattern, limit, verbose))

    @app.command()
    def get(
        key: str = typer.Argument(..., help="Cache key to retrieve"),
        decode: bool = typer.Option(
            True, "--decode/--no-decode", help="Decode value as string"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed output"
        ),
    ) -> None:
        """Get value for a specific cache key."""
        asyncio.run(_cache_get(key, decode, verbose))

    @app.command()
    def delete(
        key: str = typer.Argument(..., help="Cache key to delete"),
        confirm: bool = typer.Option(
            True, "--confirm/--no-confirm", help="Confirm before deleting"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed output"
        ),
    ) -> None:
        """Delete a specific cache key."""
        asyncio.run(_cache_delete(key, confirm, verbose))

    @app.command()
    def clear(
        pattern: str = typer.Option(
            "*", "--pattern", "-p", help="Key pattern to clear"
        ),
        confirm: bool = typer.Option(
            True, "--confirm/--no-confirm", help="Confirm before clearing"
        ),
        batch_size: int = typer.Option(
            1000, "--batch-size", help="Number of keys to delete per batch"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed output"
        ),
    ) -> None:
        """Clear cache keys matching a pattern."""
        asyncio.run(_cache_clear(pattern, confirm, batch_size, verbose))

    async def _cache_info(verbose: bool) -> None:
        """Display cache information."""
        out = get_cli_output("cache-info", verbose=verbose)

        try:
            redis_client = await get_redis_client()

            ***REMOVED*** Get Redis info
            info = await redis_client.info()
            memory_info = await redis_client.info("memory")

            ***REMOVED*** Create summary table
            table = Table(title="Redis Cache Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            ***REMOVED*** Basic info
            table.add_row("Redis Version", info.get("redis_version", "Unknown"))
            table.add_row("Connected Clients", str(info.get("connected_clients", 0)))
            table.add_row(
                "Used Memory", memory_info.get("used_memory_human", "Unknown")
            )
            table.add_row("Max Memory", memory_info.get("maxmemory_human", "Not set"))

            ***REMOVED*** Database info
            total_keys = 0
            for key in info.keys():
                if key.startswith("db"):
                    db_info = info[key]
                    keys = db_info.get("keys", 0)
                    total_keys += keys
                    if verbose:
                        table.add_row(f"Database {key[2:]}", f"{keys} keys")

            table.add_row("Total Keys", str(total_keys))

            if verbose:
                table.add_row("Keyspace Hits", str(info.get("keyspace_hits", 0)))
                table.add_row("Keyspace Misses", str(info.get("keyspace_misses", 0)))
                table.add_row("Uptime (seconds)", str(info.get("uptime_in_seconds", 0)))

            out.console.print(table)
            out.success("Cache information retrieved successfully")

        except Exception as e:
            out.error(f"Failed to get cache information: {e}")
            raise typer.Exit(code=1)

    async def _cache_keys(pattern: str, limit: int, verbose: bool) -> None:
        """List cache keys."""
        out = get_cli_output("cache-keys", verbose=verbose)

        try:
            redis_client = await get_redis_client()

            out.info(f"Searching for keys with pattern: {pattern}")

            ***REMOVED*** Get keys with pattern
            keys = await redis_client.keys(pattern)

            if not keys:
                out.warning(f"No keys found matching pattern: {pattern}")
                return

            ***REMOVED*** Limit results
            if len(keys) > limit:
                out.warning(f"Found {len(keys)} keys, showing first {limit}")
                keys = keys[:limit]

            ***REMOVED*** Display keys
            if verbose:
                table = Table(title=f"Cache Keys (pattern: {pattern})")
                table.add_column("Key", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("TTL", style="green")

                for key in keys:
                    key_type = await redis_client.type(key)
                    ttl = await redis_client.ttl(key)
                    ttl_str = (
                        "Never" if ttl == -1 else f"{ttl}s" if ttl > 0 else "Expired"
                    )
                    table.add_row(
                        key.decode() if isinstance(key, bytes) else str(key),
                        (
                            key_type.decode()
                            if isinstance(key_type, bytes)
                            else str(key_type)
                        ),
                        ttl_str,
                    )

                out.console.print(table)
            else:
                for key in keys:
                    key_str = key.decode() if isinstance(key, bytes) else str(key)
                    out.console.print(key_str)

            out.success(f"Found {len(keys)} keys")

        except Exception as e:
            out.error(f"Failed to list cache keys: {e}")
            raise typer.Exit(code=1)

    async def _cache_get(key: str, decode: bool, verbose: bool) -> None:
        """Get cache value."""
        out = get_cli_output("cache-get", verbose=verbose)

        try:
            redis_client = await get_redis_client()

            ***REMOVED*** Check if key exists
            if not await redis_client.exists(key):
                out.error(f"Key '{key}' not found")
                raise typer.Exit(code=1)

            ***REMOVED*** Get value and metadata
            value = await redis_client.get(key)
            key_type = await redis_client.type(key)
            ttl = await redis_client.ttl(key)

            if verbose:
                table = Table(title=f"Cache Entry: {key}")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")

                table.add_row(
                    "Type",
                    key_type.decode() if isinstance(key_type, bytes) else str(key_type),
                )
                ttl_str = "Never" if ttl == -1 else f"{ttl}s" if ttl > 0 else "Expired"
                table.add_row("TTL", ttl_str)

                if decode and value:
                    try:
                        decoded_value = (
                            value.decode() if isinstance(value, bytes) else str(value)
                        )
                        table.add_row("Value", decoded_value)
                    except UnicodeDecodeError:
                        table.add_row("Value", f"<binary data: {len(value)} bytes>")
                else:
                    table.add_row(
                        "Value", f"<{type(value).__name__}: {len(str(value))} chars>"
                    )

                out.console.print(table)
            else:
                if decode and value:
                    try:
                        decoded_value = (
                            value.decode() if isinstance(value, bytes) else str(value)
                        )
                        out.console.print(decoded_value)
                    except UnicodeDecodeError:
                        out.console.print(f"<binary data: {len(value)} bytes>")
                else:
                    out.console.print(str(value))

        except Exception as e:
            out.error(f"Failed to get cache value: {e}")
            raise typer.Exit(code=1)

    async def _cache_delete(key: str, confirm: bool, verbose: bool) -> None:
        """Delete cache key."""
        out = get_cli_output("cache-delete", verbose=verbose)

        try:
            redis_client = await get_redis_client()

            ***REMOVED*** Check if key exists
            if not await redis_client.exists(key):
                out.error(f"Key '{key}' not found")
                raise typer.Exit(code=1)

            ***REMOVED*** Confirm deletion
            if confirm and not out.confirm(f"Delete cache key '{key}'?"):
                out.info("Deletion cancelled")
                return

            ***REMOVED*** Delete key
            result = await redis_client.delete(key)

            if result:
                out.success(f"Deleted cache key: {key}")
            else:
                out.error(f"Failed to delete key: {key}")
                raise typer.Exit(code=1)

        except Exception as e:
            out.error(f"Failed to delete cache key: {e}")
            raise typer.Exit(code=1)

    async def _cache_clear(
        pattern: str, confirm: bool, batch_size: int, verbose: bool
    ) -> None:
        """Clear cache keys matching pattern."""
        out = get_cli_output("cache-clear", verbose=verbose)

        try:
            redis_client = await get_redis_client()

            ***REMOVED*** Get matching keys
            keys = await redis_client.keys(pattern)

            if not keys:
                out.warning(f"No keys found matching pattern: {pattern}")
                return

            ***REMOVED*** Confirm clearing
            if confirm and not out.confirm(
                f"Clear {len(keys)} cache keys matching '{pattern}'?"
            ):
                out.info("Clear operation cancelled")
                return

            ***REMOVED*** Delete keys in batches
            async with with_progress(
                out, f"Clearing {len(keys)} cache keys...", timeout=None
            ):
                deleted_count = 0

                for i in range(0, len(keys), batch_size):
                    batch = keys[i : i + batch_size]
                    result = await redis_client.delete(*batch)
                    deleted_count += result

                    if verbose:
                        out.log_operation(
                            f"Deleted batch {i//batch_size + 1}: {result} keys"
                        )

            out.success(f"Cleared {deleted_count} cache keys")

        except Exception as e:
            out.error(f"Failed to clear cache: {e}")
            raise typer.Exit(code=1)

    return app
