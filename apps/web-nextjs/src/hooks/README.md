***REMOVED*** React Hooks

This directory contains all the React hooks used in the application, organized by their responsibility.

***REMOVED******REMOVED*** 📂 Structure

```
hooks/
├── core/           ***REMOVED*** Application-wide hooks
│   ├── useAuth.ts  ***REMOVED*** Authentication hooks
│   └── useProtectedRoute.ts ***REMOVED*** Route protection logic
├── domain/         ***REMOVED*** Domain-specific hooks
│   ├── movie/      ***REMOVED*** Movie-related hooks
│   ├── actor/      ***REMOVED*** Actor-related hooks
│   ├── genre/      ***REMOVED*** Genre-related hooks
│   └── ...         ***REMOVED*** Other domain hooks
├── ui/             ***REMOVED*** UI-related hooks
│   ├── useDebounce.ts ***REMOVED*** Input debounce
│   ├── useDevice.ts ***REMOVED*** Device detection
│   └── useIntersectionObserver.ts ***REMOVED*** Scroll detection
└── index.ts        ***REMOVED*** Re-exports all hooks
```

***REMOVED******REMOVED*** 🧩 Hook Categories

***REMOVED******REMOVED******REMOVED*** Core Hooks

Core hooks handle application-wide concerns:

- **Authentication**: Login, logout, and user state management
- **Authorization**: Access control and permissions
- **Routing**: Navigation and route protection
- **Configuration**: App-wide settings and feature flags

***REMOVED******REMOVED******REMOVED*** Domain Hooks

Domain hooks interact with specific business domains:

- **Movie hooks**: Fetch and manage movie data
- **Actor hooks**: Fetch and manage actor data
- **Genre hooks**: Fetch and manage genre data
- **Search hooks**: Handle search functionality

***REMOVED******REMOVED******REMOVED*** UI Hooks

UI hooks handle presentation concerns:

- **useDebounce**: Delay value updates for input fields
- **useMediaQuery**: Respond to viewport changes
- **useIntersectionObserver**: Detect element visibility
- **useLocalStorage**: Persist data in browser storage

***REMOVED******REMOVED*** 🚀 Usage

All hooks should be imported from the main `hooks` directory:

```tsx
import { useMovie, useAuth, useDebounce } from "@/hooks";
```

***REMOVED******REMOVED******REMOVED*** Example: Domain Hook

```tsx
// Inside a component
function MovieDetail({ id }) {
  const { movie, isLoading, error, toggleLiked } = useMovie(id);

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h1>{movie.title}</h1>
      <button onClick={toggleLiked}>{movie.liked ? "Unlike" : "Like"}</button>
    </div>
  );
}
```

***REMOVED******REMOVED******REMOVED*** Example: UI Hook

```tsx
function SearchBar() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 500);

  // This effect only runs after the query has been stable for 500ms
  useEffect(() => {
    if (debouncedQuery) {
      searchMovies(debouncedQuery);
    }
  }, [debouncedQuery]);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search movies..."
    />
  );
}
```

***REMOVED******REMOVED*** 📝 Guidelines

When creating new hooks:

1. **Placement**: Put the hook in the appropriate directory based on its responsibility
2. **Naming**: Use consistent naming convention `use[Resource][Action]`
3. **TypeScript**: Include comprehensive type definitions
4. **Error Handling**: Handle and expose errors appropriately
5. **Loading States**: Provide loading state indicators
6. **Documentation**: Add JSDoc comments for all functions and parameters
7. **Minimal Dependencies**: Avoid unnecessary dependencies
8. **Testing**: Write tests for all hooks

***REMOVED******REMOVED******REMOVED*** React Query Pattern

For data fetching hooks, use React Query's patterns:

```tsx
export function useMovie(id: number) {
  return useQuery({
    queryKey: ["movie", id],
    queryFn: () => MovieAPI.getById(id),
    select: (data) => toMovieEntity(data),
  });
}
```

***REMOVED******REMOVED*** 🧪 Testing

Hooks should be tested using React Testing Library and its hooks testing utilities:

```tsx
import { renderHook, act } from "@testing-library/react-hooks";
import { useMyHook } from "@/hooks";

test("my hook works correctly", () => {
  const { result } = renderHook(() => useMyHook());

  // Test initial state
  expect(result.current.value).toBe(initialValue);

  // Test state changes
  act(() => {
    result.current.setValue(newValue);
  });

  expect(result.current.value).toBe(newValue);
});
```

***REMOVED******REMOVED*** 🔄 Data Flow

The hooks layer connects the domain layer to the UI layer:

1. **UI Components** call hooks to interact with data
2. **Hooks** use services to fetch/update data from APIs
3. **Hooks** transform API data to domain entities
4. **UI Components** receive domain entities

***REMOVED******REMOVED*** 📚 Related Documentation

For more details on specific hook categories:

- [Movie Hooks](./domain/movie/README.md) - Movie domain hooks
- [Domain Layer](../domain/README.md) - Domain layer architecture
- [Services API](../services/README.md) - API services documentation
