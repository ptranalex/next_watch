"""Cache management commands for BFF API Redis cache."""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from bff_api.config.app import settings

app = typer.Typer(name="cache", help="Redis cache management commands.")
console = Console()
logger = logging.getLogger(__name__)


@app.command(name="info")
def cache_info(
    redis_url: Optional[str] = typer.Option(
        None,
        "--redis-url",
        help="Redis URL (overrides config)",
        envvar="REDIS_URL",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed Redis information",
    ),
) -> None:
    """Display Redis cache information and statistics.

    Args:
        redis_url: Redis URL to connect to
        verbose: Show detailed Redis information
    """
    if verbose:
        console.print("[blue]📊 Gathering Redis cache information...[/blue]")

    asyncio.run(_display_cache_info_async(redis_url, verbose))


@app.command(name="keys")
def list_keys(
    pattern: str = typer.Option(
        "*",
        "--pattern",
        help="Key pattern to match",
    ),
    limit: int = typer.Option(
        100,
        "--limit",
        help="Maximum number of keys to display",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show key details including TTL",
    ),
) -> None:
    """List cache keys matching a pattern.

    Args:
        pattern: Key pattern to match (supports wildcards)
        limit: Maximum number of keys to display
        verbose: Show key details including TTL
    """
    if verbose:
        console.print(f"[blue]🔍 Searching for keys matching pattern: {pattern}[/blue]")

    asyncio.run(_list_keys_async(pattern, limit, verbose))


@app.command(name="clear")
def clear_cache(
    pattern: str = typer.Option(
        "*",
        "--pattern",
        help="Key pattern to clear",
    ),
    confirm: bool = typer.Option(
        True,
        "--confirm/--no-confirm",
        help="Confirm before clearing cache",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Clear cache keys matching a pattern.

    Args:
        pattern: Key pattern to clear (supports wildcards)
        confirm: Whether to confirm before clearing
        verbose: Show detailed output
    """
    if confirm:
        if pattern == "*":
            console.print("[red]⚠️  This will clear ALL cache keys![/red]")
        else:
            console.print(f"[yellow]This will clear keys matching pattern: {pattern}[/yellow]")

        confirmed = Confirm.ask("Are you sure you want to proceed?")
        if not confirmed:
            console.print("[yellow]Cache clear operation cancelled.[/yellow]")
            return

    if verbose:
        console.print(f"[blue]🗑️  Clearing cache keys matching: {pattern}[/blue]")

    asyncio.run(_clear_cache_async(pattern, verbose))


@app.command(name="get")
def get_key(
    key: str = typer.Argument(..., help="Cache key to retrieve"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Get value for a specific cache key.

    Args:
        key: Cache key to retrieve
        verbose: Show detailed output
    """
    if verbose:
        console.print(f"[blue]🔍 Retrieving cache key: {key}[/blue]")

    asyncio.run(_get_key_async(key, verbose))


@app.command(name="delete")
def delete_key(
    key: str = typer.Argument(..., help="Cache key to delete"),
    confirm: bool = typer.Option(
        True,
        "--confirm/--no-confirm",
        help="Confirm before deleting",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Delete a specific cache key.

    Args:
        key: Cache key to delete
        confirm: Whether to confirm before deleting
        verbose: Show detailed output
    """
    if confirm:
        confirmed = Confirm.ask(f"Are you sure you want to delete key '{key}'?")
        if not confirmed:
            console.print("[yellow]Key deletion cancelled.[/yellow]")
            return

    if verbose:
        console.print(f"[blue]🗑️  Deleting cache key: {key}[/blue]")

    asyncio.run(_delete_key_async(key, verbose))


async def _display_cache_info_async(redis_url: Optional[str], verbose: bool) -> None:
    """Async implementation of cache info display.

    Args:
        redis_url: Redis URL to connect to
        verbose: Show detailed information
    """
    try:
        import redis.asyncio as redis

        url = redis_url or settings.redis_url
        client = redis.Redis.from_url(url, decode_responses=True)

        ***REMOVED*** Get Redis info
        info = await client.info()

        ***REMOVED*** Create info table
        table = Table(title="Redis Cache Information", show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        ***REMOVED*** Basic info
        basic_metrics = [
            ("Redis Version", info.get("redis_version", "Unknown")),
            ("Connected Clients", str(info.get("connected_clients", 0))),
            ("Used Memory", _format_bytes(info.get("used_memory", 0))),
            ("Used Memory Human", info.get("used_memory_human", "Unknown")),
            ("Total Keys", str(await client.dbsize())),
            ("Keyspace Hits", str(info.get("keyspace_hits", 0))),
            ("Keyspace Misses", str(info.get("keyspace_misses", 0))),
        ]

        ***REMOVED*** Calculate hit ratio
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total_requests = hits + misses
        hit_ratio = (hits / total_requests * 100) if total_requests > 0 else 0
        basic_metrics.append(("Hit Ratio", f"{hit_ratio:.2f}%"))

        for metric, value in basic_metrics:
            table.add_row(metric, value)

        console.print(table)

        if verbose:
            ***REMOVED*** Additional detailed info
            console.print("\n[bold]Detailed Information:[/bold]")
            console.print(f"  • Uptime: {info.get('uptime_in_seconds', 0)} seconds")
            console.print(
                f"  • Total Commands Processed: {info.get('total_commands_processed', 0)}"
            )
            console.print(f"  • Instantaneous Ops/sec: {info.get('instantaneous_ops_per_sec', 0)}")
            console.print(f"  • Role: {info.get('role', 'Unknown')}")
            console.print(f"  • Redis Mode: {info.get('redis_mode', 'Unknown')}")

        await client.close()

    except Exception as e:
        console.print(f"[red]❌ Error connecting to Redis: {e}[/red]")
        logger.error(f"Redis connection error: {e}")
        raise typer.Exit(1)


async def _list_keys_async(pattern: str, limit: int, verbose: bool) -> None:
    """Async implementation of key listing.

    Args:
        pattern: Key pattern to match
        limit: Maximum number of keys
        verbose: Show detailed information
    """
    try:
        import redis.asyncio as redis

        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Get keys matching pattern
        keys = []
        async for key in client.scan_iter(match=pattern, count=100):
            keys.append(key)
            if len(keys) >= limit:
                break

        if not keys:
            console.print(f"[yellow]No keys found matching pattern: {pattern}[/yellow]")
            await client.close()
            return

        if verbose:
            ***REMOVED*** Create detailed table with TTL info
            table = Table(
                title=f"Cache Keys (showing {len(keys)} of max {limit})",
                show_header=True,
                header_style="bold green",
            )
            table.add_column("Key", style="cyan")
            table.add_column("Type", style="blue")
            table.add_column("TTL", style="yellow")
            table.add_column("Size", style="dim")

            for key in keys:
                key_type = await client.type(key)
                ttl = await client.ttl(key)

                ***REMOVED*** Format TTL
                if ttl == -1:
                    ttl_display = "No expiry"
                elif ttl == -2:
                    ttl_display = "Expired"
                else:
                    ttl_display = f"{ttl}s"

                ***REMOVED*** Get approximate size
                try:
                    if key_type == "string":
                        size = len(await client.get(key) or "")
                    else:
                        size = await client.memory_usage(key) or 0
                    size_display = _format_bytes(size)
                except:
                    size_display = "Unknown"

                table.add_row(key, key_type, ttl_display, size_display)

            console.print(table)
        else:
            ***REMOVED*** Simple list
            console.print(f"[green]Found {len(keys)} keys matching pattern: {pattern}[/green]")
            for key in keys:
                console.print(f"  • {key}")

        await client.close()

    except Exception as e:
        console.print(f"[red]❌ Error listing keys: {e}[/red]")
        logger.error(f"Redis key listing error: {e}")
        raise typer.Exit(1)


async def _clear_cache_async(pattern: str, verbose: bool) -> None:
    """Async implementation of cache clearing.

    Args:
        pattern: Key pattern to clear
        verbose: Show detailed output
    """
    try:
        import redis.asyncio as redis

        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Get keys to delete
        keys_to_delete = []
        async for key in client.scan_iter(match=pattern, count=100):
            keys_to_delete.append(key)

        if not keys_to_delete:
            console.print(f"[yellow]No keys found matching pattern: {pattern}[/yellow]")
            await client.close()
            return

        ***REMOVED*** Delete keys in batches
        deleted_count = 0
        batch_size = 100

        for i in range(0, len(keys_to_delete), batch_size):
            batch = keys_to_delete[i : i + batch_size]
            deleted = await client.delete(*batch)
            deleted_count += deleted

            if verbose:
                console.print(f"[dim]Deleted batch {i//batch_size + 1}: {deleted} keys[/dim]")

        console.print(f"[green]✅ Successfully deleted {deleted_count} cache keys![/green]")

        if verbose:
            console.print(f"[dim]Pattern used: {pattern}[/dim]")
            console.print(f"[dim]Total keys processed: {len(keys_to_delete)}[/dim]")

        await client.close()

    except Exception as e:
        console.print(f"[red]❌ Error clearing cache: {e}[/red]")
        logger.error(f"Redis cache clear error: {e}")
        raise typer.Exit(1)


async def _get_key_async(key: str, verbose: bool) -> None:
    """Async implementation of key retrieval.

    Args:
        key: Cache key to retrieve
        verbose: Show detailed output
    """
    try:
        import redis.asyncio as redis

        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Check if key exists
        if not await client.exists(key):
            console.print(f"[red]❌ Key '{key}' not found in cache[/red]")
            await client.close()
            raise typer.Exit(1)

        ***REMOVED*** Get key info
        key_type = await client.type(key)
        ttl = await client.ttl(key)

        console.print(f"[green]Key: {key}[/green]")
        console.print(f"[blue]Type: {key_type}[/blue]")

        if ttl == -1:
            console.print("[yellow]TTL: No expiry[/yellow]")
        elif ttl == -2:
            console.print("[red]TTL: Expired[/red]")
        else:
            console.print(f"[yellow]TTL: {ttl} seconds[/yellow]")

        ***REMOVED*** Get value based on type
        if key_type == "string":
            value = await client.get(key)
            console.print(f"[cyan]Value: {value}[/cyan]")
        elif key_type == "list":
            length = await client.llen(key)
            console.print(f"[cyan]List length: {length}[/cyan]")
            if verbose and length > 0:
                items = await client.lrange(key, 0, min(10, length - 1))
                console.print("[cyan]First 10 items:[/cyan]")
                for i, item in enumerate(items):
                    console.print(f"  {i}: {item}")
        elif key_type == "hash":
            length = await client.hlen(key)
            console.print(f"[cyan]Hash fields: {length}[/cyan]")
            if verbose and length > 0:
                fields = await client.hgetall(key)
                console.print("[cyan]Hash contents:[/cyan]")
                for field, value in list(fields.items())[:10]:
                    console.print(f"  {field}: {value}")
        elif key_type == "set":
            length = await client.scard(key)
            console.print(f"[cyan]Set members: {length}[/cyan]")
        elif key_type == "zset":
            length = await client.zcard(key)
            console.print(f"[cyan]Sorted set members: {length}[/cyan]")

        await client.close()

    except Exception as e:
        console.print(f"[red]❌ Error retrieving key: {e}[/red]")
        logger.error(f"Redis key retrieval error: {e}")
        raise typer.Exit(1)


async def _delete_key_async(key: str, verbose: bool) -> None:
    """Async implementation of key deletion.

    Args:
        key: Cache key to delete
        verbose: Show detailed output
    """
    try:
        import redis.asyncio as redis

        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Check if key exists
        if not await client.exists(key):
            console.print(f"[yellow]Key '{key}' not found in cache[/yellow]")
            await client.close()
            return

        ***REMOVED*** Delete key
        deleted = await client.delete(key)

        if deleted:
            console.print(f"[green]✅ Successfully deleted key: {key}[/green]")
        else:
            console.print(f"[red]❌ Failed to delete key: {key}[/red]")

        if verbose:
            console.print(f"[dim]Keys deleted: {deleted}[/dim]")

        await client.close()

    except Exception as e:
        console.print(f"[red]❌ Error deleting key: {e}[/red]")
        logger.error(f"Redis key deletion error: {e}")
        raise typer.Exit(1)


def _format_bytes(bytes_value: Union[int, float]) -> str:
    """Format bytes into human readable format.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string
    """
    bytes_float = float(bytes_value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_float < 1024.0:
            return f"{bytes_float:.1f} {unit}"
        bytes_float /= 1024.0
    return f"{bytes_float:.1f} PB"
