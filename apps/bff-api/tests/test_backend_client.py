"""Tests for backend client API path construction."""

from unittest.mock import Mock

from bff_api.services.backend_client import BackendClient


class TestBackendClient:
    """Test cases for BackendClient API path construction."""

    def test_build_api_path_adds_version_prefix(self):
        """Test that _build_api_path adds /api/v1/ prefix correctly."""
        # Setup
        config = Mock()
        config.backend_api_url = "http://localhost:8000"
        config.backend_api_timeout = 30
        client = BackendClient(config)

        # Test various path formats
        test_cases = [
            ("movies", "/api/v1/movies"),
            ("/movies", "/api/v1/movies"),
            ("movies/123", "/api/v1/movies/123"),
            ("/movies/123", "/api/v1/movies/123"),
            ("genres", "/api/v1/genres"),
            ("movies/search", "/api/v1/movies/search"),
            ("users/123/watchlist", "/api/v1/users/123/watchlist"),
        ]

        for input_path, expected_output in test_cases:
            result = client._build_api_path(input_path)
            assert result == expected_output, f"Expected {expected_output}, got {result}"

    def test_build_api_path_handles_empty_path(self):
        """Test that _build_api_path handles empty path."""
        # Setup
        config = Mock()
        config.backend_api_url = "http://localhost:8000"
        config.backend_api_timeout = 30
        client = BackendClient(config)

        # Test
        result = client._build_api_path("")
        assert result == "/api/v1/"

    def test_build_api_path_handles_multiple_slashes(self):
        """Test that _build_api_path handles multiple leading slashes."""
        # Setup
        config = Mock()
        config.backend_api_url = "http://localhost:8000"
        config.backend_api_timeout = 30
        client = BackendClient(config)

        # Test
        result = client._build_api_path("///movies")
        assert result == "/api/v1/movies"
