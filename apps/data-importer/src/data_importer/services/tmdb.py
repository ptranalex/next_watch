import os
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TMDBClient:
    """Client for The Movie Database API."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.api_key = os.environ.get("TMDB_API_KEY", "")
        if not self.api_key:
            logger.warning(
                "TMDB_API_KEY not set. Using demo mode with limited functionality."
            )

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the TMDB API."""
        if params is None:
            params = {}
        params["api_key"] = self.api_key

        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, params=params)

        if response.status_code != 200:
            logger.error(
                f"Error fetching from TMDB: {response.status_code} {response.text}"
            )
            return {}

        return response.json()

    def get_popular_movies(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get popular movies from TMDB."""
        data = self._make_request("/movie/popular", {"page": page})
        return data.get("results", [])

    ***REMOVED*** More methods will be implemented during development
