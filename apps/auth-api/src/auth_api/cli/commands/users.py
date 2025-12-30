"""User management commands for Auth API."""

import asyncio
import logging
from typing import Any

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
from sqlalchemy.exc import SQLAlchemyError

from auth_api.cli.utils import display_user_table
from auth_api.config.app import settings

app = typer.Typer(name="users", help="User management commands.")
console = Console()
logger = logging.getLogger(__name__)


@app.command(name="list")
def list_users(
    limit: int = typer.Option(
        50,
        "--limit",
        "-l",
        help="Maximum number of users to display",
    ),
    active_only: bool = typer.Option(
        False,
        "--active-only",
        help="Show only active users",
    ),
    search: str | None = typer.Option(
        None,
        "--search",
        "-s",
        help="Search users by email or username",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """List users in the authentication system.

    Args:
        limit: Maximum number of users to display
        active_only: Show only active users
        search: Search term for email or username
        verbose: Show detailed output
    """
    if verbose:
        console.print("[blue]🔍 Fetching users from database...[/blue]")

    asyncio.run(_list_users_async(limit, active_only, search, verbose))


@app.command(name="create")
def create_user(
    email: str = typer.Option(..., "--email", "-e", help="User email address"),
    username: str | None = typer.Option(None, "--username", "-u", help="Username (optional)"),
    password: str | None = typer.Option(
        None, "--password", "-p", help="User password (will prompt if not provided)"
    ),
    active: bool = typer.Option(True, "--active/--inactive", help="User active status"),
    admin: bool = typer.Option(False, "--admin", help="Grant admin privileges"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Create a new user in the authentication system.

    Args:
        email: User email address
        username: Username (optional)
        password: User password
        active: Whether user should be active
        admin: Whether to grant admin privileges
        verbose: Show detailed output
    """
    # Prompt for password if not provided
    if not password:
        password = Prompt.ask("Enter password", password=True)
        confirm_password = Prompt.ask("Confirm password", password=True)

        if password != confirm_password:
            console.print("[red]❌ Passwords do not match![/red]")
            raise typer.Exit(1)

    if verbose:
        console.print(f"[blue]Creating user: {email}[/blue]")

    asyncio.run(_create_user_async(email, username, password, active, admin, verbose))


@app.command(name="activate")
def activate_user(
    identifier: str = typer.Argument(..., help="User email or ID"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Activate a user account.

    Args:
        identifier: User email or ID
        verbose: Show detailed output
    """
    if verbose:
        console.print(f"[blue]Activating user: {identifier}[/blue]")

    asyncio.run(_update_user_status_async(identifier, True, verbose))


@app.command(name="deactivate")
def deactivate_user(
    identifier: str = typer.Argument(..., help="User email or ID"),
    confirm: bool = typer.Option(
        True, "--confirm/--no-confirm", help="Confirm before deactivating"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Deactivate a user account.

    Args:
        identifier: User email or ID
        confirm: Whether to confirm before deactivating
        verbose: Show detailed output
    """
    if confirm:
        confirmed = Confirm.ask(f"Are you sure you want to deactivate user '{identifier}'?")
        if not confirmed:
            console.print("[yellow]User deactivation cancelled.[/yellow]")
            return

    if verbose:
        console.print(f"[blue]Deactivating user: {identifier}[/blue]")

    asyncio.run(_update_user_status_async(identifier, False, verbose))


@app.command(name="delete")
def delete_user(
    identifier: str = typer.Argument(..., help="User email or ID"),
    confirm: bool = typer.Option(True, "--confirm/--no-confirm", help="Confirm before deleting"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Delete a user account permanently.

    Args:
        identifier: User email or ID
        confirm: Whether to confirm before deleting
        verbose: Show detailed output
    """
    if confirm:
        console.print(f"[red]⚠️  This will permanently delete user '{identifier}'[/red]")
        confirmed = Confirm.ask("Are you absolutely sure?")
        if not confirmed:
            console.print("[yellow]User deletion cancelled.[/yellow]")
            return

    if verbose:
        console.print(f"[blue]Deleting user: {identifier}[/blue]")

    asyncio.run(_delete_user_async(identifier, verbose))


@app.command(name="stats")
def user_stats(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed statistics"),
) -> None:
    """Display user statistics.

    Args:
        verbose: Show detailed statistics
    """
    if verbose:
        console.print("[blue]📊 Gathering user statistics...[/blue]")

    asyncio.run(_display_user_stats_async(verbose))


async def _list_users_async(
    limit: int, active_only: bool, search: str | None, verbose: bool
) -> None:
    """Async implementation of user listing.

    Args:
        limit: Maximum number of users to display
        active_only: Show only active users
        search: Search term
        verbose: Show detailed output
    """
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.database_url)

        # Build query
        query = "SELECT id, email, username, is_active, created_at, last_login_at FROM users"
        conditions = []
        params: dict[str, Any] = {}

        if active_only:
            conditions.append("is_active = :active")
            params["active"] = True

        if search:
            conditions.append("(email ILIKE :search OR username ILIKE :search)")
            params["search"] = f"%{search}%"

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT :limit"
        params["limit"] = limit

        with engine.connect() as connection:
            result = connection.execute(text(query), params)
            users = [dict(row._mapping) for row in result]

        if verbose:
            console.print(f"[green]Found {len(users)} users[/green]")

        display_user_table(users, f"Users (showing {len(users)} of max {limit})", console)

    except SQLAlchemyError as e:
        console.print(f"[red]❌ Database error: {e}[/red]")
        logger.error(f"Database error in list_users: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        logger.error(f"Unexpected error in list_users: {e}")
        raise typer.Exit(1) from e


async def _create_user_async(
    email: str,
    username: str | None,
    password: str,
    active: bool,
    admin: bool,
    verbose: bool,
) -> None:
    """Async implementation of user creation.

    Args:
        email: User email
        username: Username (optional)
        password: User password
        active: Whether user should be active
        admin: Whether to grant admin privileges
        verbose: Show detailed output
    """
    try:
        from datetime import datetime

        from sqlalchemy import create_engine, text

        # Try to import passlib, but provide fallback
        try:
            from passlib.context import CryptContext

            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(password)
        except ImportError:
            # Fallback to basic hashing if passlib not available
            import hashlib

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            console.print("[yellow]⚠️  Using basic hashing (install passlib for bcrypt)[/yellow]")

        engine = create_engine(settings.database_url)

        # Check if user already exists
        with engine.connect() as connection:
            existing = connection.execute(
                text("SELECT id FROM users WHERE email = :email"), {"email": email}
            ).fetchone()

            if existing:
                console.print(f"[red]❌ User with email '{email}' already exists![/red]")
                raise typer.Exit(1)

            # Insert new user
            insert_query = """
                INSERT INTO users (email, username, hashed_password, is_active, is_admin, created_at)
                VALUES (:email, :username, :password, :active, :admin, :created_at)
                RETURNING id
            """

            result = connection.execute(
                text(insert_query),
                {
                    "email": email,
                    "username": username,
                    "password": hashed_password,
                    "active": active,
                    "admin": admin,
                    "created_at": datetime.utcnow(),
                },
            )

            user_row = result.fetchone()
            if user_row is None:
                raise Exception("Failed to create user - no ID returned")

            user_id = user_row[0]
            connection.commit()

        console.print("[green]✅ User created successfully![/green]")
        console.print(f"   • ID: {user_id}")
        console.print(f"   • Email: {email}")
        console.print(f"   • Username: {username or 'Not set'}")
        console.print(f"   • Active: {'Yes' if active else 'No'}")
        console.print(f"   • Admin: {'Yes' if admin else 'No'}")

    except SQLAlchemyError as e:
        console.print(f"[red]❌ Database error: {e}[/red]")
        logger.error(f"Database error in create_user: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        logger.error(f"Unexpected error in create_user: {e}")
        raise typer.Exit(1) from e


async def _update_user_status_async(identifier: str, active: bool, verbose: bool) -> None:
    """Async implementation of user status update.

    Args:
        identifier: User email or ID
        active: New active status
        verbose: Show detailed output
    """
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.database_url)

        with engine.connect() as connection:
            # Find user by email or ID
            if identifier.isdigit():
                user_query = "SELECT id, email, is_active FROM users WHERE id = :identifier"
            else:
                user_query = "SELECT id, email, is_active FROM users WHERE email = :identifier"

            user = connection.execute(text(user_query), {"identifier": identifier}).fetchone()

            if not user:
                console.print(f"[red]❌ User '{identifier}' not found![/red]")
                raise typer.Exit(1)

            # Update status
            update_query = "UPDATE users SET is_active = :active WHERE id = :user_id"
            connection.execute(text(update_query), {"active": active, "user_id": user.id})
            connection.commit()

        action = "activated" if active else "deactivated"
        console.print(f"[green]✅ User '{user.email}' {action} successfully![/green]")

    except SQLAlchemyError as e:
        console.print(f"[red]❌ Database error: {e}[/red]")
        logger.error(f"Database error in update_user_status: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        logger.error(f"Unexpected error in update_user_status: {e}")
        raise typer.Exit(1) from e


async def _delete_user_async(identifier: str, verbose: bool) -> None:
    """Async implementation of user deletion.

    Args:
        identifier: User email or ID
        verbose: Show detailed output
    """
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.database_url)

        with engine.connect() as connection:
            # Find user by email or ID
            if identifier.isdigit():
                user_query = "SELECT id, email FROM users WHERE id = :identifier"
            else:
                user_query = "SELECT id, email FROM users WHERE email = :identifier"

            user = connection.execute(text(user_query), {"identifier": identifier}).fetchone()

            if not user:
                console.print(f"[red]❌ User '{identifier}' not found![/red]")
                raise typer.Exit(1)

            # Delete user
            delete_query = "DELETE FROM users WHERE id = :user_id"
            connection.execute(text(delete_query), {"user_id": user.id})
            connection.commit()

        console.print(f"[green]✅ User '{user.email}' deleted successfully![/green]")

    except SQLAlchemyError as e:
        console.print(f"[red]❌ Database error: {e}[/red]")
        logger.error(f"Database error in delete_user: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        logger.error(f"Unexpected error in delete_user: {e}")
        raise typer.Exit(1) from e


async def _display_user_stats_async(verbose: bool) -> None:
    """Async implementation of user statistics display.

    Args:
        verbose: Show detailed statistics
    """
    try:
        from rich.table import Table
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.database_url)

        with engine.connect() as connection:
            # Get basic stats
            stats_query = """
                SELECT
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE is_active = true) as active_users,
                    COUNT(*) FILTER (WHERE is_active = false) as inactive_users,
                    COUNT(*) FILTER (WHERE is_admin = true) as admin_users,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as new_users_30d,
                    COUNT(*) FILTER (WHERE last_login_at >= NOW() - INTERVAL '30 days') as active_30d
                FROM users
            """

            stats_row = connection.execute(text(stats_query)).fetchone()

        if stats_row is None:
            console.print("[red]❌ Failed to retrieve user statistics[/red]")
            raise typer.Exit(1)

        # Create stats table
        table = Table(title="User Statistics", show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Count", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")

        # Access row data by index since we know the column order
        total_users = stats_row[0] or 0
        active_users = stats_row[1] or 0
        inactive_users = stats_row[2] or 0
        admin_users = stats_row[3] or 0
        new_users_30d = stats_row[4] or 0
        active_30d = stats_row[5] or 0

        total = total_users or 1  # Avoid division by zero

        metrics = [
            ("Total Users", total_users, "100.0%"),
            (
                "Active Users",
                active_users,
                f"{(active_users / total * 100):.1f}%",
            ),
            (
                "Inactive Users",
                inactive_users,
                f"{(inactive_users / total * 100):.1f}%",
            ),
            (
                "Admin Users",
                admin_users,
                f"{(admin_users / total * 100):.1f}%",
            ),
            (
                "New Users (30d)",
                new_users_30d,
                f"{(new_users_30d / total * 100):.1f}%",
            ),
            (
                "Active in 30d",
                active_30d,
                f"{(active_30d / total * 100):.1f}%",
            ),
        ]

        for metric, count, percentage in metrics:
            table.add_row(metric, str(count), percentage)

        console.print(table)

        if verbose:
            console.print(
                f"\n[dim]Statistics generated from database: {_mask_db_url(settings.database_url)}[/dim]"
            )

    except SQLAlchemyError as e:
        console.print(f"[red]❌ Database error: {e}[/red]")
        logger.error(f"Database error in display_user_stats: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        logger.error(f"Unexpected error in display_user_stats: {e}")
        raise typer.Exit(1) from e


def _mask_db_url(database_url: str) -> str:
    """Mask password in database URL for display."""
    if not database_url:
        return "Not configured"

    if "://" in database_url and "@" in database_url:
        try:
            protocol_part, rest = database_url.split("://", 1)
            if "@" in rest:
                auth_part, host_part = rest.split("@", 1)
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                    return f"{protocol_part}://{username}:****@{host_part}"
        except (IndexError, ValueError):
            pass

    return database_url
