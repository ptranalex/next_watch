"""Application configuration for the ML API."""

import os
from pathlib import Path
from typing import Optional

***REMOVED*** Try to import dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class Config:
    """Configuration for the ML API application."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "Config":
        """Get or create the singleton instance of Config."""
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance

    def __init__(
        self,
        host: str = os.getenv("HOST", "0.0.0.0"),
        port: int = int(os.getenv("PORT", "8004")),
        embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        model_cache_dir: Optional[str] = os.getenv("MODEL_CACHE_DIR"),
        log_level: str = os.getenv("LOG_LEVEL", "INFO"),
        max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "32")),
        embeddings_db_path: Optional[str] = os.getenv("EMBEDDINGS_DB_PATH"),
    ):
        """Initialize the configuration with values from environment variables."""
        self.host = host
        self.port = port
        self.embedding_model = embedding_model
        self.model_cache_dir = Path(model_cache_dir) if model_cache_dir else None
        self.log_level = log_level
        self.max_batch_size = max_batch_size
        self.embeddings_db_path = embeddings_db_path

    def __repr__(self) -> str:
        """Return a string representation of the configuration."""
        return (
            f"Config(host='{self.host}', port={self.port}, "
            f"embedding_model='{self.embedding_model}', "
            f"model_cache_dir={self.model_cache_dir}, "
            f"log_level='{self.log_level}', "
            f"max_batch_size={self.max_batch_size}, "
            f"embeddings_db_path='{self.embeddings_db_path}')"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the configuration."""
        return self.__repr__()

    def as_dict(self) -> dict:
        """Return the configuration as a dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "embedding_model": self.embedding_model,
            "model_cache_dir": str(self.model_cache_dir) if self.model_cache_dir else None,
            "log_level": self.log_level,
            "max_batch_size": self.max_batch_size,
            "embeddings_db_path": self.embeddings_db_path,
        }


***REMOVED*** Create a default instance
config = Config.get_instance()
