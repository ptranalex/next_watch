***REMOVED*** Recommendation API v1

This directory contains the v1 API endpoints for the Next Watch recommendation service.

***REMOVED******REMOVED*** Endpoints

***REMOVED******REMOVED******REMOVED*** Trending Movies

```http
GET /v1/trending
```

Get trending movie recommendations based on recent activity.

**Query Parameters:**

- `limit` (int, optional): Maximum number of recommendations (1-100, default: 20)
- `days` (int, optional): Number of days to look back (1-30, default: 7)
- `min_rating` (float, optional): Minimum IMDb rating filter (0-10)

***REMOVED******REMOVED******REMOVED*** Popular Movies

```http
GET /v1/popular
```

Get popular movie recommendations based on ratings and vote counts.

**Query Parameters:**

- `limit` (int, optional): Maximum number of recommendations (1-100, default: 20)
- `min_rating` (float, optional): Minimum IMDb rating (0-10, default: 7.0)
- `min_vote_count` (int, optional): Minimum vote count threshold (default: 1000)

***REMOVED******REMOVED******REMOVED*** Personalized Recommendations

```http
GET /v1/user/{user_id}
```

Get personalized movie recommendations for a specific user.

**Path Parameters:**

- `user_id` (int): User ID to get recommendations for

**Query Parameters:**

- `limit` (int, optional): Maximum number of recommendations (1-100, default: 20)
- `min_rating` (float, optional): Minimum IMDb rating (0-10, default: 7.0)
- `min_vote_count` (int, optional): Minimum vote count threshold (default: 1000)

***REMOVED******REMOVED******REMOVED*** Similar Movies

```http
GET /v1/similar/{movie_id}
```

Get movies similar to a specific movie.

**Path Parameters:**

- `movie_id` (int): Movie ID to find similar movies for

**Query Parameters:**

- `limit` (int, optional): Maximum number of similar movies (1-50, default: 20)
- `min_rating` (float, optional): Minimum IMDb rating (0-10, default: 7.0)
- `min_vote_count` (int, optional): Minimum vote count threshold (default: 1000)

***REMOVED******REMOVED*** Response Models

All endpoints return a response with the following structure:

```json
{
  "recommendations": [
    {
      "id": "string",
      "title": "string",
      "overview": "string",
      "poster_path": "string",
      "release_date": "string",
      "vote_average": "float",
      "vote_count": "integer",
      "genres": ["string"],
      "similarity_score": "float"
    }
  ],
  "total": "integer",
  "type": "string",
  "filters": {
    "limit": "integer",
    "min_rating": "float",
    "min_vote_count": "integer",
    "days": "integer"
  }
}
```

***REMOVED******REMOVED*** Error Responses

The API uses standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `503 Service Unavailable`: Database service unavailable
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Error message"
}
```

***REMOVED******REMOVED*** Rate Limiting

The API implements rate limiting based on the following configuration:

- Maximum concurrent requests: 100 (configurable via `MAX_CONCURRENT_REQUESTS`)
- Request timeout: 30 seconds (configurable via `REQUEST_TIMEOUT`)

***REMOVED******REMOVED*** Caching

Recommendations are cached by default with the following settings:

- Cache TTL: 1 hour (configurable via `CACHE_TTL`)
- Cache can be disabled via `ENABLE_CACHING`
