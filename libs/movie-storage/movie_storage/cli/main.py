"""Command-line interface for movie-storage package."""

import argparse
import logging
import sys
from typing import List, Optional

from movie_storage.config.app import Config
from movie_storage.db.db import init_db, get_engine
from movie_storage.db.migrations import run_migration
from sqlmodel import SQLModel
from sqlalchemy import text

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool) -> None:
    """Set up logging configuration.

    Args:
        verbose: Whether to use verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (optional)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Movie Storage Database Management")

    ***REMOVED*** Global options
    parser.add_argument(
        "--database-url", help="Database connection URL (overrides configuration)"
    )

    ***REMOVED*** Create subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    ***REMOVED*** Common parser for shared arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    ***REMOVED*** Initialize database command
    init_parser = subparsers.add_parser(
        "init", help="Initialize database and create tables", parents=[common_parser]
    )
    init_parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create database tables",
    )

    ***REMOVED*** Migrate database command
    migrate_parser = subparsers.add_parser(
        "migrate", help="Run database migrations", parents=[common_parser]
    )

    ***REMOVED*** Teardown database command
    teardown_parser = subparsers.add_parser(
        "teardown", help="Teardown database (development only)", parents=[common_parser]
    )
    teardown_parser.add_argument(
        "--drop-all",
        action="store_true",
        help="Drop all tables (WARNING: Destructive operation)",
    )
    teardown_parser.add_argument(
        "--clear",
        nargs="+",
        choices=["movies", "genres", "migrations"],
        help="Clear specific tables (choices: movies, genres, migrations)",
    )
    teardown_parser.add_argument(
        "--confirm", action="store_true", help="Confirm destructive operation"
    )

    ***REMOVED*** Parse arguments
    return parser.parse_args(args)


def teardown_database(
    drop_all: bool = False,
    clear_tables: Optional[List[str]] = None,
    confirm: bool = False,
    db_url: Optional[str] = None,
    config: Optional[Config] = None,
) -> bool:
    """Teardown database for development.

    Args:
        drop_all: Whether to drop all tables
        clear_tables: List of tables to clear
        confirm: Whether the operation is confirmed
        db_url: Database connection URL (optional)
        config: Config instance (optional)

    Returns:
        Success status
    """
    if not confirm:
        logger.error("Teardown requires --confirm flag due to data loss risk")
        return False

    engine = get_engine(db_url, config)

    if drop_all:
        logger.warning("Dropping all tables from database")
        ***REMOVED*** Import models to ensure they're registered with SQLModel
        from movie_storage.db.models import Movie, Genre, MovieGenreLink

        SQLModel.metadata.drop_all(engine)
        logger.info("All tables dropped successfully")
        return True

    if clear_tables:
        with engine.begin() as conn:
            for table in clear_tables:
                if table == "movies":
                    logger.info("Clearing movie_genrelink table")
                    conn.execute(text("DELETE FROM moviegenrelink"))
                    logger.info("Clearing movie table")
                    conn.execute(text("DELETE FROM movie"))
                elif table == "genres":
                    logger.info("Clearing movie_genrelink table")
                    conn.execute(text("DELETE FROM moviegenrelink"))
                    logger.info("Clearing genre table")
                    conn.execute(text("DELETE FROM genre"))
                elif table == "migrations":
                    logger.info("Clearing migrations table")
                    conn.execute(text("DELETE FROM migrations"))

            logger.info(f"Cleared tables: {', '.join(clear_tables)}")
        return True

    logger.error("No teardown action specified. Use --drop-all or --clear")
    return False


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point.

    Args:
        args: Command-line arguments (optional)

    Returns:
        Exit code
    """
    parsed_args = parse_args(args)

    if not parsed_args.command:
        print("No command specified. Use --help for available commands.")
        return 1

    setup_logging(parsed_args.verbose)

    ***REMOVED*** Load configuration
    config = Config.get_instance()

    ***REMOVED*** Override database URL if provided
    if parsed_args.database_url:
        config.database_url = parsed_args.database_url

    try:
        if parsed_args.command == "init":
            logger.info("Initializing database")
            init_db(
                db_url=parsed_args.database_url,
                create_tables=parsed_args.create_tables,
                config=config,
            )
            logger.info("Database initialized successfully")
        elif parsed_args.command == "migrate":
            logger.info("Running database migrations")
            run_migration(
                db_url=parsed_args.database_url,
                config=config,
            )
            logger.info("Database migrations completed successfully")
        elif parsed_args.command == "teardown":
            logger.warning("Running database teardown (DEVELOPMENT ONLY)")
            success = teardown_database(
                drop_all=parsed_args.drop_all,
                clear_tables=parsed_args.clear,
                confirm=parsed_args.confirm,
                db_url=parsed_args.database_url,
                config=config,
            )
            if not success:
                return 1
            logger.info("Database teardown completed")
        else:
            logger.error(f"Unknown command: {parsed_args.command}")
            return 1

        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if getattr(parsed_args, "verbose", False):
            logger.exception("Stack trace:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
