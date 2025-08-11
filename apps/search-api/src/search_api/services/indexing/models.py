"""Indexing models and options for Search API suggestion indexing."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IndexOptions:
    """Configuration options for suggestion indexing operations."""

    include_movies: bool = True
    include_actors: bool = True
    include_directors: bool = False
    include_words: bool = True
    min_word_length: int = 3
    batch_size: int = 100
    clear_existing: bool = True
    fetch_limit: Optional[int] = None


@dataclass
class IndexStats:
    """Aggregate statistics about an indexing run."""

    movies_indexed: int = 0
    actors_indexed: int = 0
    directors_indexed: int = 0
    zset_entries: int = 0
    entity_records: int = 0


