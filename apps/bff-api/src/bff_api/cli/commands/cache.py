"""Cache management commands for BFF API Redis cache."""

import asyncio
from typing import Optional, Union
from typer import Typer

import typer
from rich.table import Table
from rich.prompt import Confirm

from bff_api.cli.logging import get_cli_output, CLIOutput

app: Typer = typer.Typer(name="cache", help="Redis cache management commands.")


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
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Display Redis cache information and statistics.

    Args:
        redis_url: Redis URL to connect to
        verbose: Show detailed Redis information
        quiet: Suppress output except errors
    """
    out = get_cli_output("cache.info", verbose=verbose, quiet=quiet)

    out.log_operation("Starting cache info command", redis_url=redis_url or "default")
    asyncio.run(_display_cache_info_async(redis_url, out))


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
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """List cache keys matching a pattern.

    Args:
        pattern: Key pattern to match (supports wildcards)
        limit: Maximum number of keys to display
        verbose: Show key details including TTL
        quiet: Suppress output except errors
    """
    out = get_cli_output("cache.keys", verbose=verbose, quiet=quiet)

    out.log_operation("Starting key listing", pattern=pattern, limit=limit)
    asyncio.run(_list_keys_async(pattern, limit, out))


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
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Clear cache keys matching a pattern.

    Args:
        pattern: Key pattern to clear (supports wildcards)
        confirm: Whether to confirm before clearing
        verbose: Show detailed output
        quiet: Suppress output except errors
    """
    out = get_cli_output("cache.clear", verbose=verbose, quiet=quiet)

    if confirm:
        if pattern == "*":
            out.warning("This will clear ALL cache keys!")
        else:
            out.warning(f"This will clear keys matching pattern: {pattern}")

        confirmed = Confirm.ask("Are you sure you want to proceed?", console=out.console)
        if not confirmed:
            out.info("Cache clear operation cancelled.")
            return

    out.log_operation("Starting cache clear", pattern=pattern)
    asyncio.run(_clear_cache_async(pattern, out))


@app.command(name="get")
def get_key(
    key: str = typer.Argument(..., help="Cache key to retrieve"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Get value for a specific cache key.

    Args:
        key: Cache key to retrieve
        verbose: Show detailed output
        quiet: Suppress output except errors
    """
    out = get_cli_output("cache.get", verbose=verbose, quiet=quiet)

    out.log_operation("Retrieving cache key", key=key)
    asyncio.run(_get_key_async(key, out))


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
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Delete a specific cache key.

    Args:
        key: Cache key to delete
        confirm: Whether to confirm before deleting
        verbose: Show detailed output
        quiet: Suppress output except errors
    """
    out = get_cli_output("cache.delete", verbose=verbose, quiet=quiet)

    if confirm:
        confirmed = Confirm.ask(
            f"Are you sure you want to delete key '{key}'?", console=out.console
        )
        if not confirmed:
            out.info("Key deletion cancelled.")
            return

    out.log_operation("Deleting cache key", key=key)
    asyncio.run(_delete_key_async(key, out))


async def _display_cache_info_async(redis_url: Optional[str], out: CLIOutput) -> None:
    """Async implementation of cache info display.

    Args:
        redis_url: Redis URL to connect to
        out: CLI output handler
    """
    try:
        import redis.asyncio as redis
        from bff_api.config.app import get_settings

        settings = get_settings()
        url = redis_url or settings.redis_url

        out.log_operation("Connecting to Redis", url=url)
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

        out.console.print(table)

        if out.verbose:
            ***REMOVED*** Additional detailed info
            out.info("\n[bold]Detailed Information:[/bold]")
            out.info(f"  • Uptime: {info.get('uptime_in_seconds', 0)} seconds")
            out.info(f"  • Total Commands Processed: {info.get('total_commands_processed', 0)}")
            out.info(f"  • Instantaneous Ops/sec: {info.get('instantaneous_ops_per_sec', 0)}")
            out.info(f"  • Role: {info.get('role', 'Unknown')}")
            out.info(f"  • Redis Mode: {info.get('redis_mode', 'Unknown')}")

        out.log_operation(
            "Cache info retrieved successfully",
            redis_version=info.get("redis_version"),
            total_keys=await client.dbsize(),
        )
        await client.close()

    except Exception as e:
        out.error(f"Error connecting to Redis: {e}")
        out.log_error("Redis connection failed", e, url=redis_url or "default")
        raise typer.Exit(1)


async def _list_keys_async(pattern: str, limit: int, out: CLIOutput) -> None:
    """Async implementation of key listing.

    Args:
        pattern: Key pattern to match
        limit: Maximum number of keys
        out: CLI output handler
    """
    try:
        import redis.asyncio as redis
        from bff_api.config.app import get_settings

        settings = get_settings()
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Get keys matching pattern
        keys = []
        async for key in client.scan_iter(match=pattern, count=100):
            keys.append(key)
            if len(keys) >= limit:
                break

        if not keys:
            out.warning(f"No keys found matching pattern: {pattern}")
            await client.close()
            return

        if out.verbose:
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
                key_type = await client.type(key)  ***REMOVED*** type: ignore
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

            out.console.print(table)
        else:
            ***REMOVED*** Simple list
            out.success(f"Found {len(keys)} keys matching pattern: {pattern}")
            for key in keys:
                out.info(f"  • {key}")

        out.log_operation(
            "Key listing completed", pattern=pattern, keys_found=len(keys), limit=limit
        )
        await client.close()

    except Exception as e:
        out.error(f"Error listing keys: {e}")
        out.log_error("Redis key listing failed", e, pattern=pattern)
        raise typer.Exit(1)


async def _clear_cache_async(pattern: str, out: CLIOutput) -> None:
    """Async implementation of cache clearing.

    Args:
        pattern: Key pattern to clear
        out: CLI output handler
    """
    try:
        import redis.asyncio as redis
        from bff_api.config.app import get_settings

        settings = get_settings()
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Get keys to delete
        keys_to_delete = []
        async for key in client.scan_iter(match=pattern, count=100):
            keys_to_delete.append(key)

        if not keys_to_delete:
            out.warning(f"No keys found matching pattern: {pattern}")
            await client.close()
            return

        ***REMOVED*** Delete keys in batches
        deleted_count = 0
        batch_size = 100

        for i in range(0, len(keys_to_delete), batch_size):
            batch = keys_to_delete[i : i + batch_size]
            deleted = await client.delete(*batch)
            deleted_count += deleted

            out.debug(f"Deleted batch {i//batch_size + 1}: {deleted} keys")

        out.success(f"Successfully deleted {deleted_count} cache keys!")

        out.log_operation(
            "Cache clear completed",
            pattern=pattern,
            keys_deleted=deleted_count,
            total_processed=len(keys_to_delete),
        )
        await client.close()

    except Exception as e:
        out.error(f"Error clearing cache: {e}")
        out.log_error("Redis cache clear failed", e, pattern=pattern)
        raise typer.Exit(1)


async def _get_key_async(key: str, out: CLIOutput) -> None:
    """Async implementation of key retrieval.

    Args:
        key: Cache key to retrieve
        out: CLI output handler
    """
    try:
        import redis.asyncio as redis
        from bff_api.config.app import get_settings

        settings = get_settings()
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Check if key exists
        if not await client.exists(key):
            out.error(f"Key '{key}' not found in cache")
            await client.close()
            raise typer.Exit(1)

        ***REMOVED*** Get key info
        key_type = await client.type(key)  ***REMOVED*** type: ignore
        ttl = await client.ttl(key)

        out.info(f"[green]Key: {key}[/green]")
        out.info(f"[blue]Type: {key_type}[/blue]")

        if ttl == -1:
            out.info("[yellow]TTL: No expiry[/yellow]")
        elif ttl == -2:
            out.info("[red]TTL: Expired[/red]")
        else:
            out.info(f"[yellow]TTL: {ttl} seconds[/yellow]")

        ***REMOVED*** Get value based on type
        if key_type == "string":
            value = await client.get(key)
            out.info(f"[cyan]Value: {value}[/cyan]")
        elif key_type == "list":
            length = await client.llen(key)
            out.info(f"[cyan]List length: {length}[/cyan]")
            if out.verbose and length > 0:
                items = await client.lrange(key, 0, min(10, length - 1))
                out.info("[cyan]First 10 items:[/cyan]")
                for i, item in enumerate(items):
                    out.info(f"  {i}: {item}")
        elif key_type == "hash":
            length = await client.hlen(key)
            out.info(f"[cyan]Hash fields: {length}[/cyan]")
            if out.verbose and length > 0:
                fields = await client.hgetall(key)
                out.info("[cyan]Hash contents:[/cyan]")
                for field, value in list(fields.items())[:10]:
                    out.info(f"  {field}: {value}")
        elif key_type == "set":
            length = await client.scard(key)
            out.info(f"[cyan]Set members: {length}[/cyan]")
        elif key_type == "zset":
            length = await client.zcard(key)
            out.info(f"[cyan]Sorted set members: {length}[/cyan]")

        out.log_operation("Key retrieved successfully", key=key, key_type=key_type, ttl=ttl)
        await client.close()

    except Exception as e:
        out.error(f"Error retrieving key: {e}")
        out.log_error("Redis key retrieval failed", e, key=key)
        raise typer.Exit(1)


async def _delete_key_async(key: str, out: CLIOutput) -> None:
    """Async implementation of key deletion.

    Args:
        key: Cache key to delete
        out: CLI output handler
    """
    try:
        import redis.asyncio as redis
        from bff_api.config.app import get_settings

        settings = get_settings()
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

        ***REMOVED*** Check if key exists
        if not await client.exists(key):
            out.warning(f"Key '{key}' not found in cache")
            await client.close()
            return

        ***REMOVED*** Delete key
        deleted = await client.delete(key)

        if deleted:
            out.success(f"Successfully deleted key: {key}")
        else:
            out.error(f"Failed to delete key: {key}")

        out.log_operation("Key deletion completed", key=key, deleted=bool(deleted))
        await client.close()

    except Exception as e:
        out.error(f"Error deleting key: {e}")
        out.log_error("Redis key deletion failed", e, key=key)
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
