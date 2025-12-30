"""Tests for response builder functionality."""

from fast_core.responses import ResponseBuilder


class TestResponseBuilder:
    """Test cases for ResponseBuilder class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()

    def test_paginated_response_basic(self):
        """Test basic paginated response."""
        items = [{"id": 1, "name": "Movie 1"}, {"id": 2, "name": "Movie 2"}]

        response = self.builder.paginated(items=items, page=1, limit=20, total=100)

        assert response["results"] == items
        assert response["pagination"]["page"] == 1
        assert response["pagination"]["per_page"] == 20
        assert response["pagination"]["total"] == 100
        assert response["pagination"]["total_pages"] == 5
        assert response["pagination"]["has_next"] is True
        assert response["pagination"]["has_prev"] is False

    def test_paginated_response_last_page(self):
        """Test paginated response on last page."""
        items = [{"id": 1, "name": "Movie 1"}]

        response = self.builder.paginated(items=items, page=5, limit=20, total=100)

        assert response["pagination"]["has_next"] is False
        assert response["pagination"]["has_prev"] is True

    def test_paginated_response_with_metadata(self):
        """Test paginated response with metadata."""
        items = [{"id": 1, "name": "Movie 1"}]
        metadata = {"cache_hit": True, "query_time_ms": 45}

        response = self.builder.paginated(
            items=items, page=1, limit=20, total=100, metadata=metadata
        )

        assert response["metadata"] == metadata

    def test_paginated_response_config_override(self):
        """Test paginated response with config override."""
        items = [{"id": 1, "name": "Movie 1"}]

        response = self.builder.paginated(
            items=items, page=1, limit=20, total=100, config_override={"include_total_pages": False}
        )

        assert "total_pages" not in response["pagination"]
        assert "has_next" in response["pagination"]  # Still included by default

    def test_detail_response_basic(self):
        """Test basic detail response."""
        item = {"id": 1, "title": "Test Movie", "year": 2023}

        response = self.builder.detail(item=item)

        assert response["data"] == item
        assert "related" not in response
        assert "context" not in response

    def test_detail_response_with_related(self):
        """Test detail response with related items."""
        item = {"id": 1, "title": "Test Movie"}
        related = {
            "cast": [{"name": "Actor 1"}, {"name": "Actor 2"}],
            "trailers": [{"url": "trailer1.mp4"}],
        }

        response = self.builder.detail(item=item, related=related)

        assert response["data"] == item
        assert response["related"] == related

    def test_detail_response_with_context(self):
        """Test detail response with user context."""
        item = {"id": 1, "title": "Test Movie"}
        context = {"user_id": 123, "liked": True, "watched": False}

        response = self.builder.detail(item=item, context=context)

        assert response["data"] == item
        assert response["context"] == context

    def test_collection_response(self):
        """Test collection response."""
        groups = {
            "popular": [{"id": 1, "title": "Popular Movie"}],
            "trending": [{"id": 2, "title": "Trending Movie"}],
            "recommended": [{"id": 3, "title": "Recommended Movie"}],
        }

        response = self.builder.collection(groups=groups)

        assert response["collections"] == groups

    def test_search_response_basic(self):
        """Test basic search response."""
        query = "action movies"
        results = [{"id": 1, "title": "Action Movie 1"}]

        response = self.builder.search(query=query, results=results)

        assert response["query"] == query
        assert response["results"] == results

    def test_search_response_with_facets_and_suggestions(self):
        """Test search response with facets and suggestions."""
        query = "action movies"
        results = [{"id": 1, "title": "Action Movie 1"}]
        facets = {
            "genre": {"name": "Genre", "values": [{"action": 10}, {"drama": 5}]},
            "year": {"name": "Year", "values": [{"2023": 3}, {"2022": 7}]},
        }
        suggestions = ["action films", "adventure movies"]

        response = self.builder.search(
            query=query, results=results, facets=facets, suggestions=suggestions
        )

        assert response["facets"] == facets
        assert response["suggestions"] == suggestions

    def test_action_response_success(self):
        """Test successful action response."""
        data = {"id": 1, "title": "New Movie"}

        response = self.builder.action(
            success=True, action="created", data=data, message="Movie created successfully"
        )

        assert response["success"] is True
        assert response["action"] == "created"
        assert response["data"] == data
        assert response["message"] == "Movie created successfully"

    def test_action_response_failure(self):
        """Test failed action response."""
        response = self.builder.action(
            success=False, action="delete", message="Failed to delete movie"
        )

        assert response["success"] is False
        assert response["action"] == "delete"
        assert response["message"] == "Failed to delete movie"
        assert "data" not in response

    def test_error_response_basic(self):
        """Test basic error response."""
        response = self.builder.error(
            code="MOVIE_NOT_FOUND", message="The requested movie was not found"
        )

        assert response["error"]["code"] == "MOVIE_NOT_FOUND"
        assert response["error"]["message"] == "The requested movie was not found"

    def test_error_response_with_details_and_suggestions(self):
        """Test error response with details and suggestions."""
        details = [{"field": "movie_id", "code": "INVALID", "message": "Must be positive integer"}]
        suggestions = ["Check movie ID", "Browse popular movies"]

        response = self.builder.error(
            code="VALIDATION_ERROR",
            message="Invalid input data",
            details=details,
            suggestions=suggestions,
        )

        assert response["error"]["details"] == details
        assert response["error"]["suggestions"] == suggestions

    def test_success_response(self):
        """Test simple success response."""
        data = {"status": "ok", "count": 42}

        response = self.builder.success(data=data, message="Operation completed successfully")

        assert response["data"] == data
        assert response["message"] == "Operation completed successfully"

    def test_builder_with_custom_config(self):
        """Test builder with custom configuration."""
        config = {
            "pagination": {"include_total_pages": False, "include_has_next_prev": False},
            "search": {"include_suggestions": False},
        }

        builder = ResponseBuilder(config=config)

        # Test pagination config
        paginated_response = builder.paginated(items=[{"id": 1}], page=1, limit=20, total=100)

        assert "total_pages" not in paginated_response["pagination"]
        assert "has_next" not in paginated_response["pagination"]

        # Test search config
        search_response = builder.search(
            query="test", results=[{"id": 1}], suggestions=["suggestion1", "suggestion2"]
        )

        assert "suggestions" not in search_response


class TestResponseBuilderEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()

    def test_paginated_empty_items(self):
        """Test paginated response with empty items."""
        response = self.builder.paginated(items=[], page=1, limit=20, total=0)

        assert response["results"] == []
        assert response["pagination"]["total"] == 0
        assert response["pagination"]["total_pages"] == 0
        assert response["pagination"]["has_next"] is False
        assert response["pagination"]["has_prev"] is False

    def test_paginated_zero_limit(self):
        """Test paginated response with zero limit."""
        response = self.builder.paginated(items=[], page=1, limit=0, total=100)

        assert response["pagination"]["total_pages"] == 0

    def test_detail_response_none_values(self):
        """Test detail response with None values."""
        response = self.builder.detail(item={"id": 1}, related=None, context=None, metadata=None)

        assert response["data"] == {"id": 1}
        assert "related" not in response
        assert "context" not in response
        assert "metadata" not in response

    def test_search_response_empty_results(self):
        """Test search response with empty results."""
        response = self.builder.search(query="nonexistent movie", results=[])

        assert response["query"] == "nonexistent movie"
        assert response["results"] == []

    def test_action_response_data_is_none(self):
        """Test action response when data is explicitly None."""
        response = self.builder.action(success=True, action="delete", data=None)

        # data=None should not be included in response
        assert "data" not in response

    def test_action_response_data_is_false(self):
        """Test action response when data is False (falsy but not None)."""
        response = self.builder.action(success=True, action="check", data=False)

        # data=False should be included since it's not None
        assert response["data"] is False
