***REMOVED*** Models Module

This module defines all data models and schemas for the Recommendation API service, providing type safety and data validation.

***REMOVED******REMOVED*** Overview

The models module provides:

- Pydantic models for API requests and responses
- Data transfer objects (DTOs) for internal use
- Type definitions and validation
- Schema documentation for OpenAPI/Swagger

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** `movie.py`

Defines movie-related models:

- `Movie`: Core movie model with all metadata
- `MovieDetails`: Extended movie information for detailed views
- `MovieListItem`: Simplified movie model for list views
- `MovieFilter`: Request model for filtering movies

***REMOVED******REMOVED******REMOVED*** `user.py`

Defines user-related models:

- `User`: User profile and preferences
- `UserCreate`: Model for user creation
- `UserUpdate`: Model for user profile updates
- `UserPreferences`: User preference settings

***REMOVED******REMOVED******REMOVED*** `recommendation.py`

Defines recommendation-related models:

- `MovieRecommendation`: A recommended movie with relevance score
- `UserRecommendations`: Set of recommendations for a user
- `RecommendationSource`: Enum of recommendation sources/algorithms
- `RecommendationRequest`: Request parameters for recommendations

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** API Response Models

```python
from recommendation_api.models.movie import Movie
from recommendation_api.models.recommendation import MovieRecommendation

@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    ***REMOVED*** Fetch movie from database
    db_movie = get_movie_by_id(movie_id)
    ***REMOVED*** Return as Pydantic model
    return Movie.from_orm(db_movie)

@app.get("/recommendations", response_model=List[MovieRecommendation])
def get_recommendations(user_id: int):
    ***REMOVED*** Generate recommendations
    recommendations = generate_recommendations(user_id)
    ***REMOVED*** Return as list of Pydantic models
    return [MovieRecommendation.from_movie(movie, score) for movie, score in recommendations]
```

***REMOVED******REMOVED******REMOVED*** Request Validation

```python
from recommendation_api.models.movie import MovieFilter

@app.post("/movies/search", response_model=List[Movie])
def search_movies(filters: MovieFilter):
    ***REMOVED*** Access validated filter parameters
    genre = filters.genre
    min_rating = filters.min_rating
    release_year = filters.release_year

    ***REMOVED*** Search with validated parameters
    results = search_movies_with_filters(genre, min_rating, release_year)
    return results
```

***REMOVED******REMOVED*** Model Design Principles

The models follow these design principles:

1. **Separation of concerns**: Database models are separate from API models
2. **Type safety**: All fields have explicit type annotations
3. **Validation**: Field constraints are enforced through Pydantic validators
4. **Documentation**: All models and fields have docstrings
5. **Consistency**: Naming conventions and patterns are consistent

***REMOVED******REMOVED*** Extending Models

To add new models or extend existing ones:

1. Place new models in the appropriate file based on domain
2. Follow the established patterns for model structure
3. Include proper type annotations for all fields
4. Add docstrings to document the model purpose and fields
5. Implement any necessary conversion methods (e.g., `from_orm`)
