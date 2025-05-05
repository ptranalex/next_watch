***REMOVED*** Domain Layer

The domain layer represents the core business logic and data structures of the application. It's organized around domain concepts rather than technical concepts, making it easier to express and understand the application's purpose.

***REMOVED******REMOVED*** 📂 Directory Structure

```
src/domain/
├── entities/           ***REMOVED*** Domain entities (data structures with behavior)
│   ├── movies/         ***REMOVED*** Movie domain entities
│   ├── actors/         ***REMOVED*** Actor domain entities
│   └── genres/         ***REMOVED*** Genre domain entities
├── usecases/           ***REMOVED*** (Future) Application use cases/business logic
├── repositories/       ***REMOVED*** (Future) Repository interfaces
└── services/           ***REMOVED*** (Future) Domain service interfaces
```

***REMOVED******REMOVED*** 🧩 Core Concepts

***REMOVED******REMOVED******REMOVED*** Entities

Entities are the core data structures of the application's domain. They:

1. Extend API service types with UI-specific properties
2. Provide conversion utilities between API and UI representations
3. Include type guards for runtime type checking

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

***REMOVED******REMOVED*** 🏛️ Architecture Background

This project follows a Clean Architecture approach with these key principles:

1. **Separation of Concerns**: Domain logic is separated from technical implementations
2. **Dependency Rule**: Inner layers don't depend on outer layers (domain doesn't depend on UI or services)
3. **Use-Case Driven**: Organized around business capabilities, not technical frameworks

***REMOVED******REMOVED*** 🔄 Layer Organization

From inner to outer:

1. **Domain Layer** (this directory): Core business concepts and logic
   - Entities: Data structures with behavior
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
    expect(entityMovie.in_watchlist).toBe(serviceMovie.to_watch);
  });
});
```

***REMOVED******REMOVED*** 📚 Further Reading

For more detailed information about domain entities:

- [Domain Entities README](./entities/README.md) - Specific entity implementations
- [MIGRATION_PLAN.md](./entities/MIGRATION_PLAN.md) - How the domain layer evolved
- [REMOVAL_PLAN.md](./entities/REMOVAL_PLAN.md) - Legacy code cleanup strategy
