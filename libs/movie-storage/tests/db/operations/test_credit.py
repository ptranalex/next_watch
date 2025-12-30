"""Tests for credit database operations."""

from movie_storage.db.operations import (
    create_credit,
    create_credits_from_tmdb_data,
    create_movie,
    delete_credit,
    delete_credits_for_movie,
    get_credit_by_id,
    get_credits,
    get_credits_by_movie_id,
    get_credits_by_person_id,
    update_credit,
)
from sqlmodel import Session


def test_create_credit(db_session: Session):
    """Test creating a credit record."""
    # Create a movie first
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Create a credit
    credit_data = {
        "movie_id": movie.id,
        "tmdb_person_id": 456,
        "name": "John Doe",
        "character": "Test Character",
        "department": "Acting",
        "order": 1,
    }

    credit = create_credit(db_session, credit_data)

    # Verify credit was created
    assert credit.id is not None
    assert credit.movie_id == movie.id
    assert credit.tmdb_person_id == 456
    assert credit.name == "John Doe"
    assert credit.character == "Test Character"
    assert credit.department == "Acting"
    assert credit.order == 1


def test_get_credit_by_id(db_session: Session):
    """Test retrieving a credit by ID."""
    # Create a movie
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Create a credit
    credit_data = {
        "movie_id": movie.id,
        "tmdb_person_id": 456,
        "name": "John Doe",
    }
    credit = create_credit(db_session, credit_data)

    # Make sure we have a valid ID
    assert credit.id is not None

    # Retrieve credit by ID
    retrieved_credit = get_credit_by_id(db_session, credit.id)

    # Verify retrieval
    assert retrieved_credit is not None
    assert retrieved_credit.id == credit.id
    assert retrieved_credit.name == "John Doe"


def test_get_credits_by_movie_id(db_session: Session):
    """Test retrieving all credits for a movie."""
    # Create a movie
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Create multiple credits for the movie
    credit_data_1 = {
        "movie_id": movie.id,
        "tmdb_person_id": 456,
        "name": "John Doe",
        "order": 1,
    }
    credit_data_2 = {
        "movie_id": movie.id,
        "tmdb_person_id": 789,
        "name": "Jane Smith",
        "order": 2,
    }

    create_credit(db_session, credit_data_1)
    create_credit(db_session, credit_data_2)

    # Retrieve credits by movie ID
    credits = get_credits_by_movie_id(db_session, movie.id)

    # Verify retrieval
    assert len(credits) == 2
    assert {c.name for c in credits} == {"John Doe", "Jane Smith"}


def test_get_credits_by_person_id(db_session: Session):
    """Test retrieving all credits for a person."""
    # Create two movies
    movie1 = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie 1"})
    movie2 = create_movie(db_session, {"tmdb_id": 456, "title": "Test Movie 2"})

    # Create credits for the same person in different movies
    person_id = 789

    credit_data_1 = {
        "movie_id": movie1.id,
        "tmdb_person_id": person_id,
        "name": "John Doe",
        "character": "Character 1",
    }
    credit_data_2 = {
        "movie_id": movie2.id,
        "tmdb_person_id": person_id,
        "name": "John Doe",
        "character": "Character 2",
    }

    create_credit(db_session, credit_data_1)
    create_credit(db_session, credit_data_2)

    # Retrieve credits by person ID
    credits = get_credits_by_person_id(db_session, person_id)

    # Verify retrieval
    assert len(credits) == 2
    assert {c.character for c in credits} == {"Character 1", "Character 2"}


def test_get_credits_with_filtering(db_session: Session):
    """Test retrieving credits with filtering."""
    # Create a movie
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Create credits with different departments
    create_credit(
        db_session,
        {
            "movie_id": movie.id,
            "tmdb_person_id": 456,
            "name": "John Director",
            "department": "Directing",
        },
    )
    create_credit(
        db_session,
        {
            "movie_id": movie.id,
            "tmdb_person_id": 789,
            "name": "Jane Actor",
            "department": "Acting",
        },
    )
    create_credit(
        db_session,
        {
            "movie_id": movie.id,
            "tmdb_person_id": 101,
            "name": "Sam Writer",
            "department": "Writing",
        },
    )

    # Retrieve credits filtered by department
    acting_credits = get_credits(db_session, department="Acting")
    directing_credits = get_credits(db_session, department="Directing")

    # Verify filtering
    assert len(acting_credits) == 1
    assert acting_credits[0].name == "Jane Actor"

    assert len(directing_credits) == 1
    assert directing_credits[0].name == "John Director"


def test_update_credit(db_session: Session):
    """Test updating a credit record."""
    # Create a movie
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Create a credit
    credit_data = {
        "movie_id": movie.id,
        "tmdb_person_id": 456,
        "name": "John Doe",
        "character": "Original Character",
    }
    credit = create_credit(db_session, credit_data)

    # Ensure credit has an ID
    assert credit.id is not None

    # Update the credit
    update_data = {
        "character": "Updated Character",
        "order": 5,
    }
    updated_credit = update_credit(db_session, credit.id, update_data)

    # Verify update
    assert updated_credit is not None
    assert updated_credit.character == "Updated Character"
    assert updated_credit.order == 5
    assert updated_credit.name == "John Doe"  # Unchanged field


def test_delete_credit(db_session: Session):
    """Test deleting a credit record."""
    # Create a movie
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Create a credit
    credit_data = {
        "movie_id": movie.id,
        "tmdb_person_id": 456,
        "name": "John Doe",
    }
    credit = create_credit(db_session, credit_data)

    # Ensure credit has an ID
    assert credit.id is not None
    credit_id = credit.id

    # Delete the credit
    result = delete_credit(db_session, credit_id)

    # Verify deletion
    assert result is True
    assert get_credit_by_id(db_session, credit_id) is None


def test_delete_credits_for_movie(db_session: Session):
    """Test deleting all credits for a movie."""
    # Create a movie
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Create multiple credits
    for i in range(3):
        credit_data = {
            "movie_id": movie.id,
            "tmdb_person_id": 100 + i,
            "name": f"Person {i}",
        }
        create_credit(db_session, credit_data)

    # Delete all credits for the movie
    count = delete_credits_for_movie(db_session, movie.id)

    # Verify deletion
    assert count == 3
    assert len(get_credits_by_movie_id(db_session, movie.id)) == 0


def test_create_credits_from_tmdb_data(db_session: Session):
    """Test creating credits from TMDB API data."""
    # Create a movie
    movie = create_movie(db_session, {"tmdb_id": 123, "title": "Test Movie"})

    # Sample TMDB credits data
    tmdb_credits = {
        "cast": [
            {
                "id": 1,
                "name": "Actor One",
                "character": "Character One",
                "order": 0,
                "profile_path": "/path1.jpg",
                "credit_id": "credit1",
            },
            {
                "id": 2,
                "name": "Actor Two",
                "character": "Character Two",
                "order": 1,
                "profile_path": "/path2.jpg",
                "credit_id": "credit2",
            },
        ],
        "crew": [
            {
                "id": 3,
                "name": "Director",
                "department": "Directing",
                "job": "Director",
                "profile_path": "/path3.jpg",
                "credit_id": "credit3",
            }
        ],
    }

    # Create credits from TMDB data
    created_credits = create_credits_from_tmdb_data(db_session, movie.id, tmdb_credits)

    # Verify creation
    assert len(created_credits) == 3

    # Verify data is retrieved correctly
    db_credits = get_credits_by_movie_id(db_session, movie.id)
    assert len(db_credits) == 3

    # Verify cast members
    cast_credits = [c for c in db_credits if c.character is not None]
    assert len(cast_credits) == 2
    assert {c.name for c in cast_credits} == {"Actor One", "Actor Two"}

    # Verify crew members
    crew_credits = [c for c in db_credits if c.job is not None]
    assert len(crew_credits) == 1
    assert crew_credits[0].name == "Director"
    assert crew_credits[0].department == "Directing"
    assert crew_credits[0].job == "Director"
