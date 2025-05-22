***REMOVED*** Domain Layer

The domain layer represents the core business logic and data structures of the application. It's organized around domain concepts rather than technical concepts, making it easier to express and understand the application's purpose.

***REMOVED******REMOVED*** 📂 Directory Structure

```
src/domain/
├── entities/           ***REMOVED*** Domain entities (data structures with behavior)
│   ├── movies/         ***REMOVED*** Movie domain entities
│   │   ├── Movie.ts    ***REMOVED*** Movie entity definition
│   │   └── types.ts    ***REMOVED*** Movie-related types
│   ├── users/          ***REMOVED*** User domain entities
│   │   ├── User.ts     ***REMOVED*** User entity definition
│   │   └── types.ts    ***REMOVED*** User-related types
│   ├── genres/         ***REMOVED*** Genre domain entities
│   │   ├── Genre.ts    ***REMOVED*** Genre entity definition
│   │   └── types.ts    ***REMOVED*** Genre-related types
│   └── index.ts        ***REMOVED*** Entity exports
├── models/             ***REMOVED*** Domain models with business logic
│   ├── movies/         ***REMOVED*** Movie domain models
│   ├── users/          ***REMOVED*** User domain models
│   └── genres/         ***REMOVED*** Genre domain models
├── usecases/           ***REMOVED*** Application use cases/business logic
├── repositories/       ***REMOVED*** Repository interfaces
└── services/           ***REMOVED*** Domain service interfaces
```

***REMOVED******REMOVED*** 🧩 Core Concepts

***REMOVED******REMOVED******REMOVED*** Entities

Entities are the core data structures of the application's domain. They:

1. Extend API service types with UI-specific properties
2. Provide conversion utilities between API and UI representations
3. Include type guards for runtime type checking
4. Define core business rules for data validation

***REMOVED******REMOVED******REMOVED*** Models

Domain models extend entities by adding:

1. Business logic operations (functions that operate on the data)
2. Complex validation rules
3. Relationships between different domain concepts

***REMOVED******REMOVED******REMOVED*** API and UI Separation

The domain layer creates a clear separation between:

- **API/Service Types**: Raw data structures from backend services
- **UI/Domain Types**: Enhanced types with UI-specific properties and behavior

This separation allows each layer to evolve independently while maintaining compatibility.

***REMOVED******REMOVED*** 🔄 Usage Examples

***REMOVED******REMOVED******REMOVED*** Working with Entity Types

```typescript
import { Movie, toMovieEntity, toServiceMovie } from "@/domain/entities";

// Converting from API to UI
const uiMovie = toMovieEntity(apiMovie);

// Converting from UI to API
const apiMovie = toServiceMovie(uiMovie);

// Type guards
if (isMovie(data)) {
  // TypeScript knows data is a Movie here
}
```

***REMOVED******REMOVED******REMOVED*** Entity Relationships

The domain layer models relationships between entities:

```typescript
// Movie entity may reference actors and genres
movie.cast.forEach((actor) => {
  console.log(actor.name);
});

movie.genres.forEach((genre) => {
  console.log(genre.name);
});
```

***REMOVED******REMOVED******REMOVED*** Working with Domain Models

```typescript
import { MovieModel } from "@/domain/models/movies";

// Create a movie model from entity
const movieModel = new MovieModel(movieEntity);

// Perform business operations
const relatedMovies = movieModel.findRelatedMovies();
const isAppropriateForAge = movieModel.isAppropriateForAge(userAge);

// Convert back to entity for UI rendering
const updatedEntity = movieModel.toEntity();
```

***REMOVED******REMOVED*** 🏛️ Architecture Background

This project follows a Clean Architecture approach with these key principles:

1. **Separation of Concerns**: Domain logic is separated from technical implementations
2. **Dependency Rule**: Inner layers don't depend on outer layers (domain doesn't depend on UI or services)
3. **Use-Case Driven**: Organized around business capabilities, not technical frameworks
4. **Entity-Centric**: Core business entities are at the center of the architecture

***REMOVED******REMOVED*** 🔄 Layer Organization

From inner to outer:

1. **Domain Layer** (this directory): Core business concepts and logic
   - Entities: Data structures with behavior
   - Models: Business logic operations on entities
   - Use Cases: Application business rules
   - Repository Interfaces: Data access abstractions
2. **Services Layer**: Technical implementations of domain interfaces
   - API Clients: HTTP communication with backend
   - Repository Implementations: Concrete data access
3. **UI Layer**: Presentation components and logic
   - Components: UI presentation
   - Hooks: React integration with domain

***REMOVED******REMOVED*** 🧪 Testing

Domain entities and logic should be highly testable in isolation from technical implementations:

```typescript
describe("Movie Entity", () => {
  it("should convert from service to entity format", () => {
    const serviceMovie = {
      /* ... */
    };
    const entityMovie = toMovieEntity(serviceMovie);

    expect(entityMovie.liked).toBe(serviceMovie.is_liked);
    expect(entityMovie.watched).toBe(serviceMovie.is_watched);
    expect(entityMovie.inWatchlist).toBe(serviceMovie.to_watch);
  });
});

describe("MovieModel", () => {
  it("should calculate related movies correctly", () => {
    const model = new MovieModel(movieEntity);
    const related = model.findRelatedMovies();

    expect(related).toHaveLength(5);
    expect(related[0].genres).toEqual(expect.arrayContaining(movie.genres));
  });
});
```

***REMOVED******REMOVED*** 📚 Further Reading

For more detailed information about domain entities:

- [Domain Entities README](./entities/README.md) - Specific entity implementations
- [Domain Models README](./models/README.md) - Business logic implementation
- [MIGRATION_PLAN.md](./MIGRATION_PLAN.md) - How the domain layer evolved
