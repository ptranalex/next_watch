"""Example demonstrating ResponseBuilder usage patterns.

This example shows how to use the ResponseBuilder to create consistent,
well-structured API responses across different patterns.
"""

import os
import sys

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fast_core.responses import ResponseBuilder


def demo_paginated_response():
    """Demonstrate paginated response pattern."""
    print("\n🔹 PAGINATED RESPONSE DEMO")
    print("=" * 50)

    builder = ResponseBuilder()

    # Sample movie data
    movies = [
        {"id": 1, "title": "The Matrix", "year": 1999, "rating": 8.7},
        {"id": 2, "title": "Inception", "year": 2010, "rating": 8.8},
        {"id": 3, "title": "Interstellar", "year": 2014, "rating": 8.6},
    ]

    # Create paginated response
    response = builder.paginated(
        items=movies,
        page=1,
        limit=20,
        total=150,
        metadata={
            "filters_applied": {"genre": "sci-fi", "min_rating": 8.0},
            "query_time_ms": 45,
            "cache_hit": True,
        },
    )

    print("Paginated Response Structure:")
    print(f"  📄 Results: {len(response['results'])} items")
    print(
        f"  📊 Pagination: Page {response['pagination']['page']} of {response['pagination']['total_pages']}"
    )
    print(f"  🔢 Total: {response['pagination']['total']} items")
    print(f"  ➡️  Has Next: {response['pagination']['has_next']}")
    print(f"  ⬅️  Has Prev: {response['pagination']['has_prev']}")
    if "metadata" in response:
        print(f"  🏷️  Metadata: {response['metadata']}")


def demo_detail_response():
    """Demonstrate detail response pattern."""
    print("\n🔹 DETAIL RESPONSE DEMO")
    print("=" * 50)

    builder = ResponseBuilder()

    # Sample movie detail data
    movie = {
        "id": 1,
        "title": "The Matrix",
        "year": 1999,
        "rating": 8.7,
        "plot": "A computer programmer discovers reality is a simulation...",
    }

    related_data = {
        "cast": [
            {"name": "Keanu Reeves", "character": "Neo"},
            {"name": "Laurence Fishburne", "character": "Morpheus"},
        ],
        "trailers": [
            {"url": "https://example.com/trailer1.mp4", "quality": "HD"},
        ],
        "similar_movies": [
            {"id": 2, "title": "Inception", "similarity_score": 0.85},
        ],
    }

    context_data = {
        "user_interactions": {
            "in_watchlist": True,
            "is_favorite": False,
            "user_rating": 9.0,
            "watch_progress": 0,
            "is_watched": False,
        },
        "personalized": True,
    }

    # Create detail response
    response = builder.detail(
        item=movie,
        related=related_data,
        context=context_data,
        metadata={
            "response_pattern": "detail",
            "aggregated_from": ["backend-api", "recommendation-api"],
            "api_version": "v1",
        },
    )

    print("Detail Response Structure:")
    print(f"  🎬 Main Item: {response['data']['title']} ({response['data']['year']})")
    print(f"  👥 Cast: {len(response['related']['cast'])} actors")
    print(f"  🎥 Trailers: {len(response['related']['trailers'])} available")
    print(f"  🔗 Similar: {len(response['related']['similar_movies'])} movies")
    print(
        f"  👤 User Context: Watchlist={response['context']['user_interactions']['in_watchlist']}"
    )
    if "metadata" in response:
        print(f"  🏷️  Metadata: {response['metadata']['response_pattern']} pattern")


def demo_search_response():
    """Demonstrate search response pattern."""
    print("\n🔹 SEARCH RESPONSE DEMO")
    print("=" * 50)

    builder = ResponseBuilder()

    # Sample search results
    search_results = [
        {"id": 1, "title": "Action Movie 1", "relevance": 0.95},
        {"id": 2, "title": "Action Hero", "relevance": 0.87},
        {"id": 3, "title": "Action Adventure", "relevance": 0.82},
    ]

    facets = {
        "genre": {"name": "Genre", "values": [{"action": 15}, {"adventure": 8}, {"thriller": 5}]},
        "year": {"name": "Release Year", "values": [{"2023": 3}, {"2022": 7}, {"2021": 8}]},
    }

    suggestions = ["action movies", "action films", "adventure movies"]

    # Create search response
    response = builder.search(
        query="action movies",
        results=search_results,
        facets=facets,
        suggestions=suggestions,
        metadata={
            "search_time_ms": 25,
            "total_indexed": 10000,
            "algorithm": "elasticsearch",
        },
    )

    print("Search Response Structure:")
    print(f"  🔍 Query: '{response['query']}'")
    print(f"  📋 Results: {len(response['results'])} found")
    print(f"  🏷️  Facets: {len(response['facets'])} categories")
    print(f"  💡 Suggestions: {len(response['suggestions'])} alternatives")
    if "metadata" in response:
        print(f"  ⚡ Search Time: {response['metadata']['search_time_ms']}ms")


def demo_action_response():
    """Demonstrate action response pattern."""
    print("\n🔹 ACTION RESPONSE DEMO")
    print("=" * 50)

    builder = ResponseBuilder()

    # Successful action
    success_response = builder.action(
        success=True,
        action="movie_added_to_watchlist",
        data={"movie_id": 123, "watchlist_id": 456},
        message="Movie successfully added to your watchlist",
        metadata={
            "user_id": 789,
            "timestamp": "2024-01-15T10:30:00Z",
        },
    )

    print("Successful Action Response:")
    print(f"  ✅ Success: {success_response['success']}")
    print(f"  🎯 Action: {success_response['action']}")
    print(f"  💬 Message: {success_response['message']}")
    print(f"  📦 Data: {success_response['data']}")

    # Failed action
    failure_response = builder.action(
        success=False,
        action="movie_removal_failed",
        message="Failed to remove movie from watchlist",
        metadata={
            "error_code": "MOVIE_NOT_IN_WATCHLIST",
            "user_id": 789,
        },
    )

    print("\nFailed Action Response:")
    print(f"  ❌ Success: {failure_response['success']}")
    print(f"  🎯 Action: {failure_response['action']}")
    print(f"  💬 Message: {failure_response['message']}")


def demo_error_response():
    """Demonstrate error response pattern."""
    print("\n🔹 ERROR RESPONSE DEMO")
    print("=" * 50)

    builder = ResponseBuilder()

    # Error with details and suggestions
    error_response = builder.error(
        code="MOVIE_NOT_FOUND",
        message="The requested movie could not be found",
        details=[
            {
                "field": "movie_id",
                "code": "INVALID_ID",
                "message": "Movie ID must be a positive integer",
                "value": -1,
            }
        ],
        suggestions=[
            "Check the movie ID is correct",
            "Browse popular movies instead",
            "Use the search feature to find movies",
        ],
        metadata={
            "request_id": "req_123456",
            "api_version": "v1",
            "timestamp": "2024-01-15T10:30:00Z",
        },
    )

    print("Error Response Structure:")
    print(f"  🚨 Code: {error_response['error']['code']}")
    print(f"  💬 Message: {error_response['error']['message']}")
    print(f"  🔍 Details: {len(error_response['error']['details'])} validation errors")
    print(f"  💡 Suggestions: {len(error_response['error']['suggestions'])} provided")
    if "metadata" in error_response:
        print(f"  🏷️  Request ID: {error_response['metadata']['request_id']}")


def demo_collection_response():
    """Demonstrate collection response pattern."""
    print("\n🔹 COLLECTION RESPONSE DEMO")
    print("=" * 50)

    builder = ResponseBuilder()

    # Grouped movie collections
    collections = {
        "popular": [
            {"id": 1, "title": "The Matrix", "popularity": 95},
            {"id": 2, "title": "Inception", "popularity": 92},
        ],
        "trending": [
            {"id": 3, "title": "Dune", "popularity": 88},
            {"id": 4, "title": "Spider-Man", "popularity": 85},
        ],
        "recommended": [
            {"id": 5, "title": "Interstellar", "popularity": 90},
        ],
    }

    # Create collection response
    response = builder.collection(
        groups=collections,
        metadata={
            "collection_types": ["popular", "trending", "recommended"],
            "total_movies": sum(len(movies) for movies in collections.values()),
            "personalized": True,
        },
    )

    print("Collection Response Structure:")
    for category, movies in response["collections"].items():
        print(f"  📚 {category.title()}: {len(movies)} movies")
    if "metadata" in response:
        print(f"  🔢 Total Movies: {response['metadata']['total_movies']}")
        print(f"  👤 Personalized: {response['metadata']['personalized']}")


def demo_custom_configuration():
    """Demonstrate custom ResponseBuilder configuration."""
    print("\n🔹 CUSTOM CONFIGURATION DEMO")
    print("=" * 50)

    # Custom configuration
    custom_config = {
        "pagination": {
            "include_total_pages": False,
            "include_has_next_prev": False,
        },
        "search": {
            "include_suggestions": False,
        },
        "errors": {
            "include_details": False,
        },
    }

    builder = ResponseBuilder(config=custom_config)

    # Test pagination with custom config
    paginated = builder.paginated(items=[{"id": 1}], page=1, limit=20, total=100)

    print("Custom Pagination (minimal):")
    print(f"  📊 Fields: {list(paginated['pagination'].keys())}")
    print("  🚫 Missing: total_pages, has_next, has_prev")

    # Test search with custom config
    search = builder.search(
        query="test", results=[{"id": 1}], suggestions=["suggestion1", "suggestion2"]
    )

    print("\nCustom Search (no suggestions):")
    print(f"  📋 Has suggestions: {'suggestions' in search}")


if __name__ == "__main__":
    print("🚀 FAST-CORE RESPONSEBUILDER DEMO")
    print("=" * 60)

    try:
        demo_paginated_response()
        demo_detail_response()
        demo_search_response()
        demo_action_response()
        demo_error_response()
        demo_collection_response()
        demo_custom_configuration()

        print("\n✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🎉 ResponseBuilder is working perfectly!")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
