"""Command modules for the Recommendation API CLI."""

from . import cache as cache
from . import config as config
from . import debug as debug
from . import embeddings as embeddings
from . import health as health
from . import ml as ml
from . import serve as serve

__all__ = [
    "cache",
    "config",
    "debug",
    "embeddings",
    "health",
    "ml",
    "serve",
]
