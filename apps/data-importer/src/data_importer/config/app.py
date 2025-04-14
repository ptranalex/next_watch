"""Configuration settings for the data importer."""

import os
from pathlib import Path

***REMOVED*** Load environment variables from .env files
try:
    from dotenv import load_dotenv  ***REMOVED*** type: ignore

    ***REMOVED*** Find the project root directory (looking for .env file)
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / ".env"
    env_local_path = project_root / ".env.local"

    ***REMOVED*** Load .env first (default values)
    load_dotenv(dotenv_path=env_path)

    ***REMOVED*** Then override with .env.local if it exists (custom values)
    if env_local_path.exists():
        load_dotenv(dotenv_path=env_local_path, override=True)
except ImportError:
    print("python-dotenv not installed. Using environment variables only.")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** DEFAULT PATHS AND DIRECTORIES
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** File system defaults
DEFAULT_CONFIG_DIR = Path(os.getenv("CONFIG_DIR", "config"))
DEFAULT_LOGS_DIR = Path(os.getenv("LOGS_DIR", "logs"))
DEFAULT_DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** API SETTINGS AND CREDENTIALS
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Default API keys
DEFAULT_TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN", "")
DEFAULT_IMDB_API_KEY = os.getenv("IMDB_API_KEY", "")
DEFAULT_OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** LOGGING AND OUTPUT SETTINGS
***REMOVED*** ------------------------------------------------------------------------------

***REMOVED*** Log verbosity
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"  ***REMOVED*** Detailed output
DEFAULT_QUIET = os.getenv("QUIET", "false").lower() == "true"  ***REMOVED*** Minimal output


***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** API URLs
***REMOVED*** ------------------------------------------------------------------------------

TMDB_URL = "https://api.themoviedb.org/3"
OMDB_URL = "http://www.omdbapi.com"

***REMOVED*** ------------------------------------------------------------------------------
***REMOVED*** CONFIGURATION CLASS
***REMOVED*** ------------------------------------------------------------------------------


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

    ***REMOVED*** Singleton instance
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
        config_dir: Path = DEFAULT_CONFIG_DIR,
        logs_dir: Path = DEFAULT_LOGS_DIR,
        data_dir: Path = DEFAULT_DATA_DIR,
        tmdb_access_token: str = DEFAULT_TMDB_ACCESS_TOKEN,
        imdb_api_key: str = DEFAULT_IMDB_API_KEY,
        omdb_api_key: str = DEFAULT_OMDB_API_KEY,
        log_level: str = DEFAULT_LOG_LEVEL,
        verbose: bool = DEFAULT_VERBOSE,
        quiet: bool = DEFAULT_QUIET,
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
        """
        self.config_dir = config_dir
        self.logs_dir = logs_dir
        self.data_dir = data_dir
        self.tmdb_access_token = tmdb_access_token
        self.imdb_api_key = imdb_api_key
        self.omdb_api_key = omdb_api_key
        self.log_level = log_level
        self.verbose = verbose
        self.quiet = quiet

    def __str__(self) -> str:
        """Return a string representation of the Config instance."""
        return (
            f"Config(config_dir={self.config_dir}, logs_dir={self.logs_dir}, "
            f"data_dir={self.data_dir}, tmdb_access_token={self.tmdb_access_token}, "
            f"imdb_api_key={self.imdb_api_key}, omdb_api_key={self.omdb_api_key}, "
            f"log_level={self.log_level}, verbose={self.verbose}, quiet={self.quiet})"
        )
