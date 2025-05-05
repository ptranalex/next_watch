***REMOVED*** Services API

***REMOVED******REMOVED*** 📋 Overview

The Services module provides a structured API for interacting with backend services in the Next Watch application. The module is organized into domain-specific API clients following best practices for maintainability and scalability.

***REMOVED******REMOVED*** 📂 Directory Structure

```
services/
├── api/                  ***REMOVED*** API client implementations
│   ├── actors/           ***REMOVED*** Actor domain
│   │   ├── actor-api.ts  ***REMOVED*** Actor API implementation
│   │   └── types.ts      ***REMOVED*** Actor-specific types
│   ├── core/             ***REMOVED*** Core API utilities
│   │   ├── api-client.ts ***REMOVED*** Base API client implementation
│   │   └── errors.ts     ***REMOVED*** API error types
│   ├── genres/           ***REMOVED*** Genre domain
│   │   ├── genre-api.ts  ***REMOVED*** Genre API implementation
│   │   └── types.ts      ***REMOVED*** Genre-specific types
│   ├── movies/           ***REMOVED*** Movie domain
│   │   ├── movie-api.ts  ***REMOVED*** Movie API implementation
│   │   └── types.ts      ***REMOVED*** Movie-specific types
│   ├── search/           ***REMOVED*** Search domain
│   │   ├── search-api.ts ***REMOVED*** Search API implementation
│   │   └── types.ts      ***REMOVED*** Search-specific types
│   ├── common/           ***REMOVED*** Shared types and utilities
│   │   └── types.ts      ***REMOVED*** Common type definitions
│   └── index.ts          ***REMOVED*** API module exports
├── index.ts              ***REMOVED*** Services module exports
└── README.md             ***REMOVED*** This documentation
```

***REMOVED******REMOVED*** 🚀 Usage

***REMOVED******REMOVED******REMOVED*** Importing API Modules

```typescript
// Import specific APIs
import { MovieAPI, GenreAPI, ActorAPI, SearchAPI } from "@/services/api";

// Import from central exports
import { MovieAPI, ActorAPI } from "@/services";

// Import specific types
import { Movie, Genre, Actor } from "@/services/api/common/types";
```

***REMOVED******REMOVED******REMOVED*** Working with Movie API

```typescript
import { MovieAPI } from "@/services";

// Get movies with filters
const getMovies = async () => {
  const response = await MovieAPI.getMovies({
    page: 1,
    pageSize: 20,
    sortBy: "popularity",
    sort_desc: true,
  });
  return response;
};

// Get a single movie
const getMovie = async (id: number) => {
  const movie = await MovieAPI.getById(id);
  return movie;
};

// Get movies by genre
const getMoviesByGenre = async (genreId: number) => {
  const response = await MovieAPI.getMoviesByGenre(genreId);
  return response;
};
```

***REMOVED******REMOVED******REMOVED*** Working with Genre API

```typescript
import { GenreAPI } from "@/services";

// Get all genres
const getAllGenres = async () => {
  const genres = await GenreAPI.getAll();
  return genres;
};
```

***REMOVED******REMOVED******REMOVED*** Working with Actor API

```typescript
import { ActorAPI } from "@/services";

// Get actor details
const getActor = async (id: number) => {
  const actor = await ActorAPI.getById(id);
  return actor;
};

// Get movies featuring an actor
const getActorMovies = async (actorId: number) => {
  const response = await ActorAPI.getMovies(actorId);
  return response;
};
```

***REMOVED******REMOVED******REMOVED*** Working with Search API

```typescript
import { SearchAPI } from "@/services";

// Get search suggestions
const getSuggestions = async (query: string) => {
  const response = await SearchAPI.getSuggestions(query);
  return response.suggestions;
};
```

***REMOVED******REMOVED*** 🔍 API Implementation Pattern

Each domain API follows a consistent pattern:

```typescript
// Define API class with strongly typed methods
export class MovieAPI {
  static async getById(id: number): Promise<Movie> {
    return APIClient.get<Movie>(`/movies/${id}`);
  }

  static async getMovies(
    params: MoviesQueryParams
  ): Promise<MovieListResponse> {
    return APIClient.get<MovieListResponse>("/movies", { params });
  }

  // Other methods...
}
```

Core principles:

1. **Static Methods**: Easy to use without instantiation
2. **Consistent Naming**: Verb-first method names (get, create, update, delete)
3. **Strong Typing**: TypeScript interfaces for all parameters and responses
4. **Centralized Error Handling**: Via the APIClient

***REMOVED******REMOVED*** ⚠️ Error Handling

The API clients provide consistent error handling:

```typescript
import { MovieAPI } from "@/services";
import {
  APIError,
  NetworkError,
  ValidationError,
  AuthError,
} from "@/services/api/core/errors";

try {
  const movie = await MovieAPI.getById(123);
} catch (error) {
  if (error instanceof NetworkError) {
    // Handle network issues
    console.error("Network error:", error.message);
  } else if (error instanceof ValidationError) {
    // Handle validation errors
    console.error("Validation error:", error.validationErrors);
  } else if (error instanceof AuthError) {
    // Handle authentication errors
    console.error("Auth error:", error.message);
    // Redirect to login page
  } else if (error instanceof APIError) {
    // Handle other API errors
    console.error("API error:", error.message, error.statusCode);
  } else {
    // Handle unexpected errors
    console.error("Unexpected error:", error);
  }
}
```

***REMOVED******REMOVED*** 🧪 Testing

Service APIs can be tested using mock fetch or axios-mock-adapter:

```typescript
import MockAdapter from "axios-mock-adapter";
import { APIClient } from "@/services/api/core/api-client";
import { MovieAPI } from "@/services";

describe("MovieAPI", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(APIClient.axios);
  });

  afterEach(() => {
    mock.restore();
  });

  it("should fetch a movie by ID", async () => {
    const mockMovie = { id: 1, title: "Test Movie" };
    mock.onGet("/movies/1").reply(200, mockMovie);

    const result = await MovieAPI.getById(1);
    expect(result).toEqual(mockMovie);
  });
});
```

***REMOVED******REMOVED*** 🔄 Integration with Domain Layer

The services layer works with the domain layer:

1. **Services** fetch raw data from backend APIs
2. **Domain Entities** provide conversion functions between API and UI types
3. **Hooks** use services and domain entities to provide data to components

Example flow:

```typescript
// In a hook
const movie = await MovieAPI.getById(id);
return toMovieEntity(movie); // Convert API type to domain entity
```

***REMOVED******REMOVED*** 🚧 Contributing Guidelines

When adding new API endpoints:

1. **Domain Organization**: Place code in the appropriate domain directory
2. **Type Definitions**: Create or update type definitions as needed
3. **Method Implementation**: Follow the existing API function patterns
4. **Use APIClient**: Use the base client for consistent behavior
5. **Documentation**: Add JSDoc comments for all methods
6. **Testing**: Add tests for all new functionality

***REMOVED******REMOVED*** 📚 Related Documentation

- [Domain Layer](../domain/README.md) - Domain entities architecture
- [Hooks Layer](../hooks/README.md) - React hooks integration
