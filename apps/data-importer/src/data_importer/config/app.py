"""Application configuration management.

This module provides centralized configuration for the data-importer application,
loading settings from environment variables with sensible defaults.
"""

from datetime import datetime
from pathlib import Path
from typing import TypedDict

# Load environment variables from .env files
from .env import get_env_bool, get_env_int, get_env_var

# ------------------------------------------------------------------------------
# DEFAULT PATHS AND DIRECTORIES
# ------------------------------------------------------------------------------

# Directory paths
DEFAULT_LOGS_DIR = Path(get_env_var("LOGS_DIR", "logs"))
DEFAULT_DATA_DIR = Path(get_env_var("DATA_DIR", "data"))

# ------------------------------------------------------------------------------
# API SETTINGS AND CREDENTIALS
# ------------------------------------------------------------------------------

# API Keys and Tokens
# These are loaded from environment variables or .env files
# Set these in your .env file or environment
DEFAULT_TMDB_ACCESS_TOKEN = get_env_var("TMDB_ACCESS_TOKEN", "")
DEFAULT_IMDB_API_KEY = get_env_var("IMDB_API_KEY", "")
DEFAULT_OMDB_API_KEY = get_env_var("OMDB_API_KEY", "")

# ------------------------------------------------------------------------------
# LOGGING AND OUTPUT SETTINGS
# ------------------------------------------------------------------------------

# Logging Configuration
DEFAULT_LOG_LEVEL = get_env_var("LOG_LEVEL", "INFO")
DEFAULT_VERBOSE = get_env_bool("VERBOSE", False)  # Detailed output
DEFAULT_QUIET = get_env_bool("QUIET", False)  # Minimal output

# ------------------------------------------------------------------------------
# MOVIE SYNC SETTINGS
# ------------------------------------------------------------------------------

# Get current year for default end_year
CURRENT_YEAR = datetime.now().year

# Movie sync configuration
DEFAULT_MOVIE_SYNC_START_YEAR = get_env_int("MOVIE_SYNC_START_YEAR", 1990)
DEFAULT_MOVIE_SYNC_END_YEAR = get_env_int("MOVIE_SYNC_END_YEAR", CURRENT_YEAR)
DEFAULT_MOVIE_SYNC_LIMIT_PER_YEAR = get_env_int("MOVIE_SYNC_LIMIT_PER_YEAR", 100)
DEFAULT_MOVIE_SYNC_MIN_VOTE_COUNT = get_env_int("MOVIE_SYNC_MIN_VOTE_COUNT", 100)
DEFAULT_MOVIE_SYNC_SORT_BY = get_env_var("MOVIE_SYNC_SORT_BY", "vote_count.desc")
DEFAULT_MOVIE_SYNC_INCLUDE_CREDITS = get_env_bool("MOVIE_SYNC_INCLUDE_CREDITS", True)
DEFAULT_MOVIE_SYNC_INCLUDE_VIDEOS = get_env_bool("MOVIE_SYNC_INCLUDE_VIDEOS", True)
DEFAULT_MOVIE_SYNC_SAVE_TO_DB = get_env_bool("MOVIE_SYNC_SAVE_TO_DB", True)

# ------------------------------------------------------------------------------
# API URLs
# ------------------------------------------------------------------------------

TMDB_URL = "https://api.themoviedb.org/3"
OMDB_URL = "http://www.omdbapi.com"

# ------------------------------------------------------------------------------
# CONFIGURATION CLASS
# ------------------------------------------------------------------------------


class ConfigDict(TypedDict):
    """Type definition for configuration dictionary."""

    logs_dir: Path
    data_dir: Path
    tmdb_access_token: str
    imdb_api_key: str
    omdb_api_key: str
    log_level: str
    verbose: bool
    quiet: bool
    movie_sync_start_year: int
    movie_sync_end_year: int
    movie_sync_limit_per_year: int
    movie_sync_min_vote_count: int
    movie_sync_sort_by: str
    movie_sync_include_credits: bool
    movie_sync_include_videos: bool
    movie_sync_save_to_db: bool


class Config:
    """Configuration class for the data importer."""

    config_dir: Path
    logs_dir: Path
    data_dir: Path
    tmdb_access_token: str
    imdb_api_key: str
    omdb_api_key: str
    log_level: str
    verbose: bool
    quiet: bool

    # Movie sync configuration
    movie_sync_start_year: int
    movie_sync_end_year: int
    movie_sync_limit_per_year: int
    movie_sync_min_vote_count: int
    movie_sync_sort_by: str
    movie_sync_include_credits: bool
    movie_sync_include_videos: bool
    movie_sync_save_to_db: bool

    # Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls) -> "Config":
        """Get the singleton instance of Config.

        Returns:
            The global Config instance
        """
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance

    def __init__(
        self,
        logs_dir: Path = DEFAULT_LOGS_DIR,
        data_dir: Path = DEFAULT_DATA_DIR,
        tmdb_access_token: str = DEFAULT_TMDB_ACCESS_TOKEN,
        imdb_api_key: str = DEFAULT_IMDB_API_KEY,
        omdb_api_key: str = DEFAULT_OMDB_API_KEY,
        log_level: str = DEFAULT_LOG_LEVEL,
        verbose: bool = DEFAULT_VERBOSE,
        quiet: bool = DEFAULT_QUIET,
        movie_sync_start_year: int = DEFAULT_MOVIE_SYNC_START_YEAR,
        movie_sync_end_year: int = DEFAULT_MOVIE_SYNC_END_YEAR,
        movie_sync_limit_per_year: int = DEFAULT_MOVIE_SYNC_LIMIT_PER_YEAR,
        movie_sync_min_vote_count: int = DEFAULT_MOVIE_SYNC_MIN_VOTE_COUNT,
        movie_sync_sort_by: str = DEFAULT_MOVIE_SYNC_SORT_BY,
        movie_sync_include_credits: bool = DEFAULT_MOVIE_SYNC_INCLUDE_CREDITS,
        movie_sync_include_videos: bool = DEFAULT_MOVIE_SYNC_INCLUDE_VIDEOS,
        movie_sync_save_to_db: bool = DEFAULT_MOVIE_SYNC_SAVE_TO_DB,
    ):
        """Initialize configuration.

        Args:
            config_dir: Directory for configuration files
            logs_dir: Directory to save log files
            data_dir: Directory for downloaded data files
            tmdb_access_token: Bearer token for The Movie Database API
            imdb_api_key: API key for IMDb
            omdb_api_key: API key for Open Movie Database
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            verbose: Whether to show verbose output
            quiet: Whether to suppress non-essential output
            movie_sync_start_year: Start year for movie sync
            movie_sync_end_year: End year for movie sync
            movie_sync_limit_per_year: Maximum number of movies to sync per year
            movie_sync_min_vote_count: Minimum vote count for movies to include
            movie_sync_sort_by: How to sort movies ('popularity.desc' or 'vote_count.desc')
            movie_sync_include_credits: Whether to include cast and crew information
            movie_sync_include_videos: Whether to include videos in movie sync
            movie_sync_save_to_db: Whether to save movies to the database
        """
        self.logs_dir = logs_dir
        self.data_dir = data_dir
        self.tmdb_access_token = tmdb_access_token
        self.imdb_api_key = imdb_api_key
        self.omdb_api_key = omdb_api_key
        self.log_level = log_level
        self.verbose = verbose
        self.quiet = quiet

        # Movie sync settings
        self.movie_sync_start_year = movie_sync_start_year
        self.movie_sync_end_year = movie_sync_end_year
        self.movie_sync_limit_per_year = movie_sync_limit_per_year
        self.movie_sync_min_vote_count = movie_sync_min_vote_count
        self.movie_sync_sort_by = movie_sync_sort_by
        self.movie_sync_include_credits = movie_sync_include_credits
        self.movie_sync_include_videos = movie_sync_include_videos
        self.movie_sync_save_to_db = movie_sync_save_to_db

    def __str__(self) -> str:
        """Return a string representation of the Config instance."""
        # Mask sensitive values like API keys in the string representation
        masked_tmdb = (
            f"{'*' * (len(self.tmdb_access_token) - 4)}{self.tmdb_access_token[-4:]}"
            if self.tmdb_access_token
            else ""
        )
        masked_imdb = (
            f"{'*' * (len(self.imdb_api_key) - 4)}{self.imdb_api_key[-4:]}"
            if self.imdb_api_key
            else ""
        )
        masked_omdb = (
            f"{'*' * (len(self.omdb_api_key) - 4)}{self.omdb_api_key[-4:]}"
            if self.omdb_api_key
            else ""
        )

        return (
            f"Config(\n"
            f"  logs_dir={self.logs_dir},\n"
            f"  data_dir={self.data_dir},\n"
            f"  tmdb_access_token={masked_tmdb},\n"
            f"  imdb_api_key={masked_imdb},\n"
            f"  omdb_api_key={masked_omdb},\n"
            f"  log_level={self.log_level},\n"
            f"  verbose={self.verbose},\n"
            f"  quiet={self.quiet},\n"
            f"  movie_sync_start_year={self.movie_sync_start_year},\n"
            f"  movie_sync_end_year={self.movie_sync_end_year},\n"
            f"  movie_sync_limit_per_year={self.movie_sync_limit_per_year},\n"
            f"  movie_sync_min_vote_count={self.movie_sync_min_vote_count},\n"
            f"  movie_sync_sort_by={self.movie_sync_sort_by},\n"
            f"  movie_sync_include_credits={self.movie_sync_include_credits},\n"
            f"  movie_sync_include_videos={self.movie_sync_include_videos},\n"
            f"  movie_sync_save_to_db={self.movie_sync_save_to_db}\n"
            f")"
        )
