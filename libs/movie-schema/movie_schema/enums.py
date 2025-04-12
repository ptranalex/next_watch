from enum import Enum, auto
from typing import Dict, List


class MediaType(str, Enum):
    """Types of media content."""

    MOVIE = "movie"
    TV = "tv"
    PERSON = "person"


class ContentRating(str, Enum):
    """Content ratings based on US rating system."""

    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"
    TV_Y = "TV-Y"
    TV_Y7 = "TV-Y7"
    TV_G = "TV-G"
    TV_PG = "TV-PG"
    TV_14 = "TV-14"
    TV_MA = "TV-MA"
    UNRATED = "UNRATED"
