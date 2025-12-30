"""Unit tests to exercise backend-api models and schemas.

These tests focus on importability and basic construction of SQLModel/Pydantic
models without requiring a database.
"""

from __future__ import annotations

from datetime import date, datetime


def test_sqlmodel_models_construct() -> None:
    from backend_api.models.credit import Credit
    from backend_api.models.genre import Genre
    from backend_api.models.movie import Movie, MovieGenreLink
    from backend_api.models.trailer import Trailer
    from backend_api.models.user import User
    from backend_api.models.user_interaction import UserMovieInteraction

    link = MovieGenreLink(movie_id=1, genre_id=2)
    assert link.movie_id == 1

    genre = Genre(tmdb_id=28, name="Action")
    assert genre.name == "Action"

    movie = Movie(
        tmdb_id=123,
        imdb_id="tt123",
        title="Test Movie",
        original_title=None,
        overview=None,
        language="en",
        release_date=date(2024, 1, 1),
        runtime=120,
        poster_url=None,
        backdrop_url=None,
        popularity=1.0,
        tmdb_rating=7.5,
        imdb_rating=7.2,
    )
    assert movie.tmdb_id == 123

    credit = Credit(movie_id=1, tmdb_person_id=999, name="Actor")
    assert credit.tmdb_person_id == 999

    trailer = Trailer(
        movie_id=1,
        youtube_key="abc",
        name="Trailer",
        is_official=True,
        published_at=datetime.utcnow(),
    )
    assert trailer.youtube_key == "abc"

    user = User(username="u", email="u@example.com", hashed_password="x")
    assert user.email == "u@example.com"

    interaction = UserMovieInteraction(user_id=1, movie_id=1)
    assert interaction.watched is False


def test_sqlalchemy_mappers_configure() -> None:
    """Regression test: mapper configuration should succeed for all models.

    We previously had a broken relationship annotation in `Trailer`:
    `movie: "Movie | None"`, which SQLAlchemy tried to resolve as a literal
    class name and failed during mapper configuration.
    """

    from sqlalchemy.orm import configure_mappers

    # Ensure both sides of the relationship are imported/registered.
    from backend_api.models.movie import Movie  # noqa: F401
    from backend_api.models.trailer import Trailer  # noqa: F401

    configure_mappers()


def test_pydantic_schemas_construct() -> None:
    from backend_api.schemas.movie_schema import (
        MovieCreate,
        MovieResponse,
        MoviesListResponse,
    )
    from backend_api.schemas.user_interaction_schema import (
        AddToCollectionRequest,
        CollectionItemResponse,
        CollectionOperationResponse,
        CollectionResponse,
        CollectionStatsResponse,
        MovieSummary,
        UserCollectionsSummaryResponse,
        UserMovieInteractionCreate,
        UserMovieInteractionResponse,
        UserMovieInteractionUpdate,
    )

    create = MovieCreate(tmdb_id=1, title="T", genre_ids=[1])
    assert create.tmdb_id == 1

    resp = MovieResponse(id=1, tmdb_id=1, title="T")
    assert resp.id == 1

    lst = MoviesListResponse(
        total=1,
        page=1,
        per_page=20,
        total_pages=1,
        has_next=False,
        has_prev=False,
        results=[resp],
    )
    assert lst.total == 1

    i_create = UserMovieInteractionCreate(user_id=1, movie_id=1, watched=True)
    assert i_create.watched is True

    i_update = UserMovieInteractionUpdate(liked=True)
    assert i_update.liked is True

    i_resp = UserMovieInteractionResponse(user_id=1, movie_id=1)
    assert i_resp.user_id == 1

    summary = MovieSummary(id=1, title="T")
    assert summary.title == "T"

    add_req = AddToCollectionRequest(movie_id=1)
    assert add_req.movie_id == 1

    item = CollectionItemResponse(movie_id=1, user_id=1, added_at=datetime.utcnow())
    coll = CollectionResponse(items=[item], total_count=1)
    assert coll.total_count == 1

    op = CollectionOperationResponse(
        success=True,
        message="ok",
        movie_id=1,
        collection_type="watchlist",
        operation="added",
    )
    assert op.success is True

    stats = CollectionStatsResponse(collection_type="watchlist", total_count=1)
    summary_resp = UserCollectionsSummaryResponse(
        watchlist=stats,
        watched_movies=stats,
        liked_movies=stats,
        total_interactions=1,
    )
    assert summary_resp.total_interactions == 1
