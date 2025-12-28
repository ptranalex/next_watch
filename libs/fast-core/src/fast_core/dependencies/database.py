"""Database dependency providers for FastAPI applications.

This module provides dependency providers for database sessions and
transaction management in FastAPI applications.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, cast

from config.logging import get_logger
from fastapi import Depends, Request

logger = get_logger(__name__)


def get_db_session() -> Any:
    """Get database session from app state.

    Returns:
        Dependency function that returns database session instance

    Raises:
        RuntimeError: If database session not found in app state
    """

    async def _get_db_session(request: Request) -> AsyncGenerator[Any, None]:
        ***REMOVED*** Try to get database session factory from app state
        db_session_factory = getattr(request.app.state, "db_session_factory", None)

        if db_session_factory is None:
            ***REMOVED*** Try to get from settings
            settings = getattr(request.app.state, "settings", None)
            if settings and hasattr(settings, "db_session_factory"):
                db_session_factory = settings.db_session_factory

        if db_session_factory is None:
            raise RuntimeError("Database session factory not found in app state")

        ***REMOVED*** Create and yield session
        session = None
        try:
            if callable(db_session_factory):
                session = db_session_factory()
            else:
                session = db_session_factory

            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            if session and hasattr(session, "rollback"):
                try:
                    rollback_method = getattr(session, "rollback", None)
                    if rollback_method and callable(rollback_method):
                        rollback_result = rollback_method()
                        if hasattr(rollback_result, "__await__"):
                            await rollback_result
                except Exception:
                    pass
            raise
        finally:
            if session and hasattr(session, "close"):
                try:
                    close_result = session.close()
                    if hasattr(close_result, "__await__"):
                        await close_result
                except Exception:
                    pass

    return Depends(_get_db_session)


def get_db_transaction() -> Any:
    """Get database transaction context.

    Returns:
        Dependency function that returns database transaction context

    Raises:
        RuntimeError: If database session not available
    """

    @asynccontextmanager
    async def _get_db_transaction(
        session: Any = Depends(get_db_session()),
    ) -> AsyncGenerator[Any, None]:
        ***REMOVED*** Start transaction
        transaction = None
        try:
            if hasattr(session, "begin"):
                transaction = await session.begin()

            yield session

            ***REMOVED*** Commit transaction
            if transaction and hasattr(transaction, "commit"):
                await transaction.commit()
            elif hasattr(session, "commit"):
                await session.commit()
        except Exception as e:
            logger.error(f"Database transaction error: {e}")
            ***REMOVED*** Rollback transaction
            if transaction and hasattr(transaction, "rollback"):
                try:
                    await transaction.rollback()
                except Exception:
                    pass
            elif hasattr(session, "rollback"):
                try:
                    await session.rollback()
                except Exception:
                    pass
            raise

    return Depends(_get_db_transaction)


def get_database_engine() -> Any:
    """Get database engine from app state.

    Returns:
        Dependency function that returns database engine instance

    Raises:
        RuntimeError: If database engine not found
    """

    def _get_database_engine(request: Request) -> Any:
        ***REMOVED*** Try to get database engine from app state
        db_engine = getattr(request.app.state, "db_engine", None)

        if db_engine is None:
            ***REMOVED*** Try to get from settings
            settings = getattr(request.app.state, "settings", None)
            if settings and hasattr(settings, "db_engine"):
                db_engine = settings.db_engine

        if db_engine is None:
            raise RuntimeError("Database engine not found in app state")

        return db_engine

    return Depends(_get_database_engine)


class DatabaseService:
    """Service for database operations with dependency injection."""

    def __init__(self, session: Any):
        """Initialize database service.

        Args:
            session: Database session
        """
        self.session = session

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """Execute a raw SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query result
        """
        try:
            if hasattr(self.session, "execute"):
                if params:
                    return await self.session.execute(query, params)
                else:
                    return await self.session.execute(query)
            else:
                raise RuntimeError("Session does not support execute method")
        except Exception as e:
            logger.error(f"Database execute error: {e}")
            raise

    async def fetch_one(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """Fetch one row from query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Single row result or None
        """
        result = await self.execute(query, params)
        if hasattr(result, "fetchone"):
            return await result.fetchone()
        elif hasattr(result, "first"):
            return result.first()
        else:
            return result

    async def fetch_all(self, query: str, params: dict[str, Any] | None = None) -> list[Any]:
        """Fetch all rows from query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of rows
        """
        result = await self.execute(query, params)
        if hasattr(result, "fetchall"):
            fetchall_result = await result.fetchall()
            return cast(list[Any], fetchall_result)
        elif hasattr(result, "all"):
            all_result = result.all()
            return cast(list[Any], all_result)
        else:
            return [result] if result else []

    async def commit(self) -> None:
        """Commit current transaction."""
        if hasattr(self.session, "commit"):
            await self.session.commit()

    async def rollback(self) -> None:
        """Rollback current transaction."""
        if hasattr(self.session, "rollback"):
            await self.session.rollback()


def get_database_service() -> Any:
    """Get database service instance.

    Returns:
        Dependency function that returns DatabaseService instance
    """

    def _get_database_service(
        session: Any = Depends(get_db_session()),
    ) -> DatabaseService:
        return DatabaseService(session)

    return Depends(_get_database_service)


def get_read_only_session() -> Any:
    """Get read-only database session.

    Returns:
        Dependency function that returns read-only database session

    Note:
        This is a marker dependency. The actual read-only behavior
        should be implemented in the database configuration.
    """

    async def _get_read_only_session(
        session: Any = Depends(get_db_session()),
    ) -> Any:
        ***REMOVED*** Mark session as read-only if supported
        if hasattr(session, "info"):
            session.info["read_only"] = True

        return session

    return Depends(_get_read_only_session)
