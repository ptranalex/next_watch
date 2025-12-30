# Domain Entities

This directory contains the core domain entities used throughout the application. These entities serve as the data model for the UI layer, providing type safety and consistent interfaces.

## 🏗️ Architecture

The domain entities follow a clean architecture pattern:

```
domain/
└── entities/
    ├── movies/              # Movie-related entities
    │   ├── Movie.entity.ts  # Main Movie entity
    │   └── index.ts         # Re-exports
    ├── actors/              # Actor-related entities
    ├── genres/              # Genre-related entities
    └── index.ts             # Main re-export for all entities
```

## 🧩 Entity Pattern

Each entity follows a consistent pattern:

1. **Entity Interface**: Extends the API service type with UI-specific properties
2. **Conversion Functions**: Methods to convert between service and UI representations
   - `toXxxEntity`: Converts service object to UI entity
   - `toServiceXxx`: Converts UI entity back to service object format
3. **Documentation**: JSDoc comments explaining all properties and methods
4. **Type Guards**: Functions to check if an object matches entity structure

### Example Entity Pattern

```typescript
// 1. Entity Interface
export interface Movie extends Omit<ServiceMovie, "is_liked" | "is_watched"> {
  liked?: boolean; // UI-specific property
  watched?: boolean; // UI-specific property
  in_watchlist?: boolean;
  isSelected?: boolean; // UI-only state
}

// 2. Conversion Functions
export function toMovieEntity(serviceMovie: ServiceMovie): Movie {
  const { is_liked, is_watched, to_watch, ...rest } = serviceMovie;
  return {
    ...rest,
    liked: is_liked,
    watched: is_watched,
    in_watchlist: to_watch,
  };
}

// 3. Type Guards
export function isMovie(value: unknown): value is Movie {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "title" in value
  );
}
```

## 📊 API Naming Conventions

We follow the backend API naming conventions for entity properties, particularly for movie user interactions:

| Property Name  | Description                                  |
| -------------- | -------------------------------------------- |
| `liked`        | Whether the user has liked the movie         |
| `watched`      | Whether the user has watched the movie       |
| `in_watchlist` | Whether the movie is in the user's watchlist |

This ensures consistency between API responses and our UI model, eliminating the need for property mapping layers.

## 📚 Usage Guidelines

When working with the domain entities:

### Importing Entities

Always import from the main domain entities module:

```typescript
import { Movie, Actor, Genre } from "@/domain/entities";
```

### Transforming API Responses

Transform API responses to domain entities for use in the UI:

```typescript
import { toMovieEntity } from "@/domain/entities";

// In a service or hook
const apiResponse = await fetchMovie(id);
const movie = toMovieEntity(apiResponse);
```

### Preparing Data for API Requests

Transform domain entities back to service format for API calls:

```typescript
import { toServiceMovie } from "@/domain/entities";

// Before an API call
const serviceData = toServiceMovie(movieEntity);
await updateMovie(id, serviceData);
```

### Entity Relationships

Entities may reference other entities through relationships:

```typescript
// A movie has many actors
const actors = movie.cast;

// A movie has many genres
const genres = movie.genres;

// An actor has many movies
const movies = actor.known_for;
```

## 🔍 Best Practices

1. **Keep Entities Pure**: Domain entities should be focused on business concepts
2. **Consistent Property Naming**: Follow API naming conventions
3. **Type Safety**: Use proper type guards when handling dynamic data
4. **JSDoc Comments**: Document all properties and methods
5. **Minimize UI State**: Only include UI state properties when necessary
6. **Complete Conversions**: Ensure conversion functions handle all properties

## ✅ Migration Status

The migration to standardized API naming conventions is complete:

- ✅ All entity files use JSDoc documentation
- ✅ All components use the standardized API naming (`liked`, `watched`, `in_watchlist`)
- ✅ Mapping layers have been removed for simpler code
- ✅ All imports updated to use the new path
- ✅ Conversion utilities correctly handle property transformations
- ✅ Legacy compatibility layer has been removed

## 🧪 Testing

Entity types and conversion functions should be tested thoroughly:

```typescript
describe("toMovieEntity", () => {
  it("should convert property names correctly", () => {
    const serviceMovie = {
      id: 1,
      title: "Test Movie",
      is_liked: true,
      is_watched: false,
      to_watch: true,
    };

    const movie = toMovieEntity(serviceMovie);

    expect(movie.id).toBe(1);
    expect(movie.title).toBe("Test Movie");
    expect(movie.liked).toBe(true);
    expect(movie.watched).toBe(false);
    expect(movie.in_watchlist).toBe(true);
  });
});
```

## 📖 Related Documentation

- See [Migration Plan](./MIGRATION_PLAN.md) for details on how entities evolved
- See [Removal Plan](./REMOVAL_PLAN.md) for legacy code cleanup strategy
