"""Tests for BFF routes."""

from unittest.mock import AsyncMock

import pytest

from bff_api.services.backend_client import BackendClientError


class TestHealthRoutes:
    """Test cases for health check routes."""

    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "0.1.0"

    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data

    def test_liveness_check(self, client):
        """Test liveness check endpoint."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestBFFRoutes:
    """Test cases for main BFF routes."""

    def test_home_screen_success(self, client, mock_backend_client):
        """Test successful home screen data aggregation."""
        ***REMOVED*** Mock backend responses
        mock_backend_client.get_movies.side_effect = [
            {"data": [{"id": 1, "title": "Featured Movie"}]},  ***REMOVED*** featured
            {"data": [{"id": 2, "title": "Popular Movie"}]},  ***REMOVED*** popular
            {"data": [{"id": 3, "title": "Recent Movie"}]},  ***REMOVED*** recent
        ]
        mock_backend_client.get_genres.return_value = [{"id": 1, "name": "Action"}]

        response = client.get("/bff/home")

        assert response.status_code == 200
        data = response.json()
        assert "featured_movies" in data
        assert "popular_movies" in data
        assert "recent_releases" in data
        assert "genres" in data
        assert len(data["featured_movies"]) == 1

    def test_home_screen_with_user_id(self, client, mock_backend_client):
        """Test home screen with user-specific recommendations."""
        ***REMOVED*** Mock backend responses
        mock_backend_client.get_movies.side_effect = [
            {"data": [{"id": 1, "title": "Featured Movie"}]},  ***REMOVED*** featured
            {"data": [{"id": 2, "title": "Popular Movie"}]},  ***REMOVED*** popular
            {"data": [{"id": 3, "title": "Recent Movie"}]},  ***REMOVED*** recent
            {"data": [{"id": 4, "title": "Recommended Movie"}]},  ***REMOVED*** recommendations
        ]
        mock_backend_client.get_genres.return_value = [{"id": 1, "name": "Action"}]

        response = client.get("/bff/home?user_id=123")

        assert response.status_code == 200
        data = response.json()
        assert "user_recommendations" in data
        assert len(data["user_recommendations"]) == 1

    def test_home_screen_backend_error(self, client, mock_backend_client):
        """Test home screen when backend is unavailable."""
        mock_backend_client.get_movies.side_effect = BackendClientError("Backend down")

        response = client.get("/bff/home")

        assert response.status_code == 502
        assert "Backend service unavailable" in response.json()["detail"]

    def test_movie_screen_success(self, client, mock_backend_client):
        """Test successful movie detail screen."""
        mock_backend_client.get_movie.return_value = {
            "id": 1,
            "title": "Test Movie",
            "description": "A test movie",
        }

        response = client.get("/bff/movies/1")

        assert response.status_code == 200
        data = response.json()
        assert "movie" in data
        assert "cast" in data
        assert "similar_movies" in data
        assert "user_interactions" in data
        assert data["movie"]["id"] == 1

    def test_movie_screen_not_found(self, client, mock_backend_client):
        """Test movie detail screen when movie not found."""
        mock_backend_client.get_movie.side_effect = BackendClientError("Backend API error: 404")

        response = client.get("/bff/movies/999")

        assert response.status_code == 404
        assert "Movie not found" in response.json()["detail"]

    def test_search_screen_success(self, client, mock_backend_client):
        """Test successful search."""
        mock_backend_client.search_movies.return_value = {
            "data": [{"id": 1, "title": "Search Result"}],
            "total": 1,
            "has_next": False,
        }

        response = client.get("/bff/search?q=test")

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert "results" in data
        assert data["total_count"] == 1
        assert data["has_next"] is False
