"""Cache management commands for the Backend API CLI."""

import json
from typing import cast

import typer
from config.logging import configure_logging, get_logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from backend_api.config.app import settings

app = typer.Typer(
    name="cache",
    help="Redis cache management commands.",
    add_completion=False,
)

console = Console()
logger = get_logger("backend_api.cli.commands.cache")


@app.command(name="info")
def cache_info(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed cache information"
    ),
    redis_url: str | None = typer.Option(
        None, "--redis-url", "-r", help="Redis URL (defaults to REDIS_URL env var)"
    ),
) -> None:
    """Display Redis cache information.

    Args:
        verbose: Show detailed cache statistics
        redis_url: Redis connection URL (optional, defaults to REDIS_URL env var)
    """
    import redis
    from redis.exceptions import RedisError

    ***REMOVED*** Configure logging
    configure_logging(logger_name="backend_api", log_level="INFO", quiet=not verbose)
    logger = get_logger(__name__)

    ***REMOVED*** Get Redis URL from options, environment, or default
    actual_redis_url = redis_url or getattr(
        settings, "redis_url", "redis://localhost:6379/0"
    )

    try:
        ***REMOVED*** Connect to Redis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(
                description=f"Connecting to Redis at {actual_redis_url}...", total=None
            )
            ***REMOVED*** Cast to str to satisfy type checker
            redis_client = redis.from_url(cast(str, actual_redis_url))

            ***REMOVED*** Get Redis info
            info = redis_client.info()

        ***REMOVED*** Display basic info
        console.print("📊 Redis Cache Information")
        console.print(f"Version: {info.get('redis_version', 'Unknown')}")
        console.print(f"Mode: {info.get('redis_mode', 'Unknown')}")
        console.print(f"Memory used: {info.get('used_memory_human', 'Unknown')}")
        console.print(f"Connected clients: {info.get('connected_clients', 0)}")

        if verbose:
            ***REMOVED*** Display detailed info
            table = Table(title="Detailed Redis Information")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            ***REMOVED*** Server info
            table.add_row("Redis version", info.get("redis_version", "Unknown"))
            table.add_row("Redis mode", info.get("redis_mode", "Unknown"))
            table.add_row("OS", info.get("os", "Unknown"))
            table.add_row("TCP port", str(info.get("tcp_port", "Unknown")))
            table.add_row("Uptime", f"{info.get('uptime_in_days', 0)} days")
            table.add_row("Process ID", str(info.get("process_id", "Unknown")))

            ***REMOVED*** Memory info
            table.add_row("Used memory", info.get("used_memory_human", "Unknown"))
            table.add_row("Peak memory", info.get("used_memory_peak_human", "Unknown"))
            table.add_row(
                "Memory fragmentation ratio",
                str(info.get("mem_fragmentation_ratio", "Unknown")),
            )

            ***REMOVED*** Stats
            table.add_row("Connected clients", str(info.get("connected_clients", 0)))
            table.add_row(
                "Total connections received",
                str(info.get("total_connections_received", 0)),
            )
            table.add_row(
                "Total commands processed", str(info.get("total_commands_processed", 0))
            )
            table.add_row("Keyspace hits", str(info.get("keyspace_hits", 0)))
            table.add_row("Keyspace misses", str(info.get("keyspace_misses", 0)))

            ***REMOVED*** Keyspace info
            for db, stats in info.items():
                if db.startswith("db"):
                    if isinstance(stats, dict):
                        table.add_row(
                            f"Database {db}",
                            f"Keys: {stats.get('keys', 0)}, Expires: {stats.get('expires', 0)}",
                        )
                    else:
                        table.add_row(f"Database {db}", str(stats))

            console.print(table)

    except RedisError as e:
        console.print(f"❌ Redis error: {str(e)}", style="bold red")
        logger.error(f"Redis error: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command(name="keys")
def list_keys(
    pattern: str = typer.Option("*", "--pattern", "-p", help="Key pattern to match"),
    limit: int = typer.Option(
        50, "--limit", "-l", help="Maximum number of keys to display"
    ),
    redis_url: str | None = typer.Option(
        None, "--redis-url", "-r", help="Redis URL (defaults to REDIS_URL env var)"
    ),
) -> None:
    """List cache keys matching a pattern.

    Args:
        pattern: Key pattern to match (e.g., "user:*", "session:*")
        limit: Maximum number of keys to display
        redis_url: Redis connection URL (optional, defaults to REDIS_URL env var)
    """
    import redis
    from redis.exceptions import RedisError

    ***REMOVED*** Configure logging
    configure_logging(logger_name="backend_api", log_level="INFO")
    logger = get_logger(__name__)

    ***REMOVED*** Get Redis URL from options, environment, or default
    actual_redis_url = redis_url or getattr(
        settings, "redis_url", "redis://localhost:6379/0"
    )

    try:
        ***REMOVED*** Connect to Redis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(
                description=f"Connecting to Redis at {actual_redis_url}...", total=None
            )
            ***REMOVED*** Cast to str to satisfy type checker
            redis_client = redis.from_url(cast(str, actual_redis_url))

            progress.add_task(
                description=f"Scanning for keys matching pattern '{pattern}'...",
                total=None,
            )

            ***REMOVED*** Use SCAN to iterate through keys
            cursor = 0
            keys: list[bytes] = []  ***REMOVED*** Redis keys are always bytes

            while len(keys) < limit:
                cursor, batch = redis_client.scan(
                    cursor=cursor, match=pattern, count=100
                )

                ***REMOVED*** Add keys from this batch
                for key in batch:
                    if len(keys) < limit:
                        keys.append(key)
                    else:
                        break

                ***REMOVED*** If we've scanned all keys, break out
                if cursor == 0:
                    break

        ***REMOVED*** Display keys
        if keys:
            table = Table(title=f"Redis Keys Matching '{pattern}'")
            table.add_column("Key", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Size", style="green")

            for key in keys:
                ***REMOVED*** For type checking safety, create string version of key
                key_str = key.decode("utf-8") if isinstance(key, bytes) else str(key)

                ***REMOVED*** Get key type (we can't use variable name 'type' as it shadows Python's type)
                ***REMOVED*** Add type ignore for untyped function
                key_type_str = redis_client.type(key)  ***REMOVED*** type: ignore

                ***REMOVED*** Get size based on key type
                if key_type_str == "string":
                    ***REMOVED*** Add type ignore for untyped function
                    size = redis_client.strlen(key)  ***REMOVED*** type: ignore
                elif key_type_str == "list":
                    size = redis_client.llen(key)
                elif key_type_str == "set":
                    size = redis_client.scard(key)
                elif key_type_str == "zset":
                    size = redis_client.zcard(key)
                elif key_type_str == "hash":
                    size = redis_client.hlen(key)
                else:
                    size = "N/A"

                table.add_row(key_str, key_type_str, str(size))

            console.print(table)

            if cursor != 0:
                console.print(
                    f"⚠️  Displaying {len(keys)} of {len(keys) + 1}+ keys. Use --limit to see more."
                )
        else:
            console.print(f"ℹ️  No keys found matching pattern '{pattern}'")

    except RedisError as e:
        console.print(f"❌ Redis error: {str(e)}", style="bold red")
        logger.error(f"Redis error: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command(name="get")
def get_key(
    key: str = typer.Argument(..., help="Key to retrieve"),
    format_json: bool = typer.Option(True, "--json/--raw", help="Format JSON values"),
    redis_url: str | None = typer.Option(
        None, "--redis-url", "-r", help="Redis URL (defaults to REDIS_URL env var)"
    ),
) -> None:
    """Get the value of a specific Redis key.

    Args:
        key: Key to retrieve
        format_json: Format JSON values (for string values only)
        redis_url: Redis connection URL (optional, defaults to REDIS_URL env var)
    """
    import redis
    from redis.exceptions import RedisError

    ***REMOVED*** Configure logging
    configure_logging(logger_name="backend_api", log_level="INFO")
    logger = get_logger(__name__)

    ***REMOVED*** Get Redis URL from options, environment, or default
    actual_redis_url = redis_url or getattr(
        settings, "redis_url", "redis://localhost:6379/0"
    )

    try:
        ***REMOVED*** Connect to Redis
        ***REMOVED*** Cast to str to satisfy type checker
        redis_client = redis.from_url(cast(str, actual_redis_url))

        ***REMOVED*** Check if key exists
        if not redis_client.exists(key):
            console.print(f"❌ Key '{key}' not found", style="bold red")
            raise typer.Exit(1)

        ***REMOVED*** Get key type (we can't use variable name 'type' as it shadows Python's type)
        ***REMOVED*** Add type ignore for untyped function
        key_type_str = redis_client.type(key)  ***REMOVED*** type: ignore

        ***REMOVED*** Get value based on type
        if key_type_str == "string":
            value = redis_client.get(key)

            ***REMOVED*** Try to format as JSON if requested
            if format_json and value:
                try:
                    ***REMOVED*** Handle both str and bytes values
                    value_str = (
                        value.decode("utf-8")
                        if isinstance(value, bytes)
                        else str(value)
                    )

                    json_value = json.loads(value_str)
                    console.print(f"📝 Key: {key} (string, JSON)")
                    console.print_json(json.dumps(json_value, indent=2))
                except json.JSONDecodeError:
                    console.print(f"📝 Key: {key} (string)")
                    console.print(
                        value.decode("utf-8") if isinstance(value, bytes) else value
                    )
            else:
                console.print(f"📝 Key: {key} (string)")
                console.print(
                    value.decode("utf-8") if isinstance(value, bytes) else value
                )

        elif key_type_str == "list":
            list_values = redis_client.lrange(key, 0, -1)
            console.print(f"📝 Key: {key} (list, {len(list_values)} items)")

            for i, item in enumerate(list_values):
                item_str = (
                    item.decode("utf-8") if isinstance(item, bytes) else str(item)
                )
                console.print(f"{i}: {item_str}")

        elif key_type_str == "set":
            ***REMOVED*** Redis smembers returns Set[bytes], but we need to add type: ignore
            set_values = redis_client.smembers(key)
            console.print(f"📝 Key: {key} (set, {len(set_values)} items)")

            for item in set_values:
                item_str = (
                    item.decode("utf-8") if isinstance(item, bytes) else str(item)
                )
                console.print(f"- {item_str}")

        elif key_type_str == "zset":
            ***REMOVED*** Redis zrange with withscores returns list of tuples, add type: ignore
            zset_values = redis_client.zrange(key, 0, -1, withscores=True)
            console.print(f"📝 Key: {key} (sorted set, {len(zset_values)} items)")

            for item, score in zset_values:
                item_str = (
                    item.decode("utf-8") if isinstance(item, bytes) else str(item)
                )
                console.print(f"{score}: {item_str}")

        elif key_type_str == "hash":
            ***REMOVED*** Redis hgetall returns Dict[bytes, bytes], add type: ignore
            hash_values = redis_client.hgetall(key)
            console.print(f"📝 Key: {key} (hash, {len(hash_values)} fields)")

            table = Table()
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")

            for field, value in hash_values.items():
                ***REMOVED*** Convert bytes to string for both field and value
                field_str = (
                    field.decode("utf-8") if isinstance(field, bytes) else str(field)
                )
                value_str = (
                    value.decode("utf-8") if isinstance(value, bytes) else str(value)
                )

                ***REMOVED*** Try to format JSON values
                if format_json:
                    try:
                        json_value = json.loads(value_str)
                        value_str = json.dumps(json_value, indent=2)
                    except (json.JSONDecodeError, TypeError):
                        pass

                table.add_row(field_str, value_str)

            console.print(table)
        else:
            console.print(f"📝 Key: {key} (unknown type: {key_type_str})")

    except RedisError as e:
        console.print(f"❌ Redis error: {str(e)}", style="bold red")
        logger.error(f"Redis error: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command(name="delete")
def delete_key(
    key: str = typer.Argument(..., help="Key to delete"),
    confirm: bool = typer.Option(
        True, "--confirm/--no-confirm", help="Confirm deletion"
    ),
    redis_url: str | None = typer.Option(
        None, "--redis-url", "-r", help="Redis URL (defaults to REDIS_URL env var)"
    ),
) -> None:
    """Delete a specific Redis key.

    Args:
        key: Key to delete
        confirm: Confirm deletion
        redis_url: Redis connection URL (optional, defaults to REDIS_URL env var)
    """
    import redis
    from redis.exceptions import RedisError

    ***REMOVED*** Configure logging
    configure_logging(logger_name="backend_api", log_level="INFO")
    logger = get_logger(__name__)

    ***REMOVED*** Get Redis URL from options, environment, or default
    actual_redis_url = redis_url or getattr(
        settings, "redis_url", "redis://localhost:6379/0"
    )

    try:
        ***REMOVED*** Connect to Redis
        ***REMOVED*** Cast to str to satisfy type checker
        redis_client = redis.from_url(cast(str, actual_redis_url))

        ***REMOVED*** Check if key exists
        if not redis_client.exists(key):
            console.print(f"❌ Key '{key}' not found", style="bold red")
            raise typer.Exit(1)

        ***REMOVED*** Confirm deletion if requested
        if confirm:
            ***REMOVED*** Get key type (we can't use variable name 'type' as it shadows Python's type)
            ***REMOVED*** Add type ignore for untyped function
            key_type_str = redis_client.type(key)  ***REMOVED*** type: ignore
            console.print(f"⚠️  About to delete key '{key}' of type {key_type_str}")
            if not typer.confirm("Are you sure?"):
                console.print("Operation cancelled.")
                return

        ***REMOVED*** Delete the key
        redis_client.delete(key)
        console.print(f"✅ Key '{key}' deleted successfully")

    except RedisError as e:
        console.print(f"❌ Redis error: {str(e)}", style="bold red")
        logger.error(f"Redis error: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command(name="clear")
def clear_cache(
    pattern: str = typer.Option("*", "--pattern", "-p", help="Key pattern to delete"),
    confirm: bool = typer.Option(
        True, "--confirm/--no-confirm", help="Confirm deletion"
    ),
    redis_url: str | None = typer.Option(
        None, "--redis-url", "-r", help="Redis URL (defaults to REDIS_URL env var)"
    ),
) -> None:
    """Clear cache keys matching a pattern.

    Args:
        pattern: Key pattern to delete (e.g., "user:*", "session:*")
        confirm: Confirm deletion
        redis_url: Redis connection URL (optional, defaults to REDIS_URL env var)
    """
    import redis
    from redis.exceptions import RedisError

    ***REMOVED*** Configure logging
    configure_logging(logger_name="backend_api", log_level="INFO")
    logger = get_logger(__name__)

    ***REMOVED*** Get Redis URL from options, environment, or default
    actual_redis_url = redis_url or getattr(
        settings, "redis_url", "redis://localhost:6379/0"
    )

    try:
        ***REMOVED*** Connect to Redis
        ***REMOVED*** Cast to str to satisfy type checker
        redis_client = redis.from_url(cast(str, actual_redis_url))

        ***REMOVED*** Get keys matching pattern
        cursor = 0
        keys: list[bytes] = []  ***REMOVED*** Redis keys are always bytes

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                description=f"Scanning for keys matching pattern '{pattern}'...",
                total=None,
            )

            while True:
                cursor, batch = redis_client.scan(
                    cursor=cursor, match=pattern, count=100
                )
                ***REMOVED*** Explicitly cast to bytes to handle type checking
                keys.extend([key for key in batch])

                if cursor == 0:
                    break

        ***REMOVED*** No keys found
        if not keys:
            console.print(f"ℹ️  No keys found matching pattern '{pattern}'")
            return

        ***REMOVED*** Confirm deletion if requested
        if confirm:
            console.print(
                f"⚠️  About to delete {len(keys)} keys matching pattern '{pattern}'"
            )
            if not typer.confirm("Are you sure?"):
                console.print("Operation cancelled.")
                return

        ***REMOVED*** Delete keys in batches
        deleted = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Deleting keys...", total=len(keys))

            ***REMOVED*** Delete in batches of 100
            batch_size = 100
            for i in range(0, len(keys), batch_size):
                batch = keys[i : i + batch_size]
                if batch:
                    deleted += redis_client.delete(*batch)
                progress.update(task, advance=len(batch))

        console.print(f"✅ {deleted} keys deleted successfully")

    except RedisError as e:
        console.print(f"❌ Redis error: {str(e)}", style="bold red")
        logger.error(f"Redis error: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(1)


***REMOVED*** Register cache commands directly with cache_app
from backend_api.cli import cache_app  ***REMOVED*** noqa: E402

***REMOVED*** Register each command directly
cache_app.command("info")(cache_info)
cache_app.command("keys")(list_keys)
cache_app.command("get")(get_key)
cache_app.command("delete")(delete_key)
cache_app.command("clear")(clear_cache)
