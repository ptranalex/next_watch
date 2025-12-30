"""Tests for BFF routes."""

from bff_api.services.backend_client import BackendClientError

API_V1 = "/bff/v1"


class TestMetaRoutes:
    """Test cases for fast-core meta endpoints."""

    def test_info(self, client):
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data or "service_name" in data

    def test_version(self, client):
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data


class TestBFFRoutes:
    """Test cases for main BFF routes."""

    def test_home_screen_success(self, client, mock_backend_client):
        mock_backend_client.get_movies.side_effect = [
            {"results": [{"id": 1, "title": "Featured Movie"}]},
            {"results": [{"id": 2, "title": "Popular Movie"}]},
            {"results": [{"id": 3, "title": "Recent Movie"}]},
        ]
        mock_backend_client.get_genres.return_value = [{"id": 1, "name": "Action"}]

        response = client.get(f"{API_V1}/home")

        assert response.status_code == 200
        data = response.json()
        assert "featured_movies" in data
        assert "popular_movies" in data
        assert "recent_releases" in data
        assert "genres" in data
        assert len(data["featured_movies"]) == 1

    def test_home_screen_backend_error(self, client, mock_backend_client):
        mock_backend_client.get_movies.side_effect = BackendClientError("Backend down")

        response = client.get(f"{API_V1}/home")

        # Upstream failures become ExternalServiceException (typically 502)
        assert response.status_code in {502, 500}

    def test_search_screen_success(self, client, mock_backend_client):
        mock_backend_client.search_movies.return_value = {
            "results": [{"id": 1, "title": "Search Result"}],
            "total": 1,
            "has_next": False,
        }

        response = client.get(f"{API_V1}/search?q=test")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "pagination" in data
        assert data["pagination"]["total"] == 1
