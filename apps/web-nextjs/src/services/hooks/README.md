# React Hooks

This directory contains all the React hooks used in the application, organized by their responsibility.

## 📂 Structure

```
hooks/
├── core/                # Application-wide hooks
│   ├── useAuth.ts       # Authentication hooks
│   ├── useSettings.ts   # Application settings
│   └── useProtectedRoute.ts # Route protection logic
├── domain/              # Domain-specific hooks
│   ├── movie/           # Movie-related hooks
│   │   ├── useMovie.ts  # Individual movie data
│   │   ├── useMovieList.ts # Movie listings
│   │   ├── useMovieActions.ts # Movie interactions
│   │   └── useMovieSearch.ts # Search functionality
│   ├── user/            # User-related hooks
│   │   ├── useProfile.ts # User profile data
│   │   └── usePreferences.ts # User preferences
│   ├── genre/           # Genre-related hooks
│   └── actors/          # Actor-related hooks
├── ui/                  # UI-related hooks
│   ├── useDebounce.ts   # Input debounce
│   ├── useIntersectionObserver.ts # Scroll detection
│   ├── useLocalStorage.ts # Local storage persistence
│   ├── useMediaQuery.ts # Media query matching
│   ├── useSwipe.ts      # Swipe gesture detection
│   └── useHapticFeedback.ts # Haptic feedback utilities
├── performance/         # Performance optimization hooks
│   ├── useMemoizedCallback.ts # Callback memoization
│   ├── useDeepCompareMemo.ts # Deep comparison memoization
│   └── useDebouncedEffect.ts # Debounced effects
├── navigation/          # Navigation-related hooks
│   ├── useRouteParams.ts # Route parameter access
│   ├── useQueryParams.ts # URL query parameter handling
│   └── useNavigation.ts # Navigation utilities
├── filter/              # Filter and sorting hooks
│   ├── useFilterState.ts # Filter state management
│   ├── useSortOptions.ts # Sorting options
│   └── useFilterURL.ts  # URL-based filtering
└── index.ts             # Re-exports all hooks
```

## 🧩 Hook Categories

### Core Hooks

Core hooks handle application-wide concerns:

- **Authentication**: Login, logout, and user state management
- **Authorization**: Access control and permissions
- **Routing**: Navigation and route protection
- **Configuration**: App-wide settings and feature flags
- **Theme**: Theme selection and application

### Domain Hooks

Domain hooks interact with specific business domains:

- **Movie hooks**: Fetch and manage movie data
- **User hooks**: Fetch and manage user data
- **Genre hooks**: Fetch and manage genre data
- **Search hooks**: Handle search functionality
- **Watchlist hooks**: Manage user watchlist

### UI Hooks

UI hooks handle presentation concerns:

- **useDebounce**: Delay value updates for input fields
- **useMediaQuery**: Respond to viewport changes
- **useIntersectionObserver**: Detect element visibility
- **useLocalStorage**: Persist data in browser storage
- **useSwipe**: Detect and handle swipe gestures
- **useHapticFeedback**: Trigger device vibration feedback

### Performance Hooks

Performance hooks optimize rendering and data flow:

- **useMemoizedCallback**: Enhanced useCallback with deep comparisons
- **useDeepCompareMemo**: useMemo with deep equality checks
- **useDebouncedEffect**: useEffect with debounce to prevent rapid re-executions
- **useLazyRef**: Lazy initialization of refs with complex values

### Navigation Hooks

Navigation hooks simplify routing and navigation:

- **useRouteParams**: Access and validate route parameters
- **useQueryParams**: Parse and update URL query parameters
- **useNavigation**: Navigate between routes with type safety
- **useScrollRestoration**: Restore scroll position when navigating

### Filter Hooks

Filter hooks handle data filtering and sorting:

- **useFilterState**: Manage filter criteria state
- **useSortOptions**: Define and apply sorting logic
- **useFilterURL**: Synchronize filters with URL parameters
- **useInfiniteScroll**: Load more data on scroll

## 🚀 Usage

All hooks should be imported from the main `hooks` directory:

```tsx
import { useMovie, useAuth, useDebounce } from "@/hooks";
```

### Example: Domain Hook

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

### Example: UI Hook

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

### Example: Combined Hooks

```tsx
function MovieFilterPage() {
  // URL parameters
  const { params, updateParams } = useQueryParams();

  // Filter state synchronized with URL
  const { filters, setFilter, resetFilters } = useFilterURL({
    defaultFilters: { genre: [], year: null, rating: 0 },
    urlParams: params,
  });

  // Movie data with filters applied
  const { movies, isLoading, fetchNextPage } = useMovieList({ filters });

  // Infinite scroll to load more movies
  const loadMoreRef = useInfiniteScroll(fetchNextPage);

  return (
    <div>
      <FilterPanel
        filters={filters}
        onChange={setFilter}
        onReset={resetFilters}
      />
      <MovieList movies={movies} isLoading={isLoading} />
      <div ref={loadMoreRef} />
    </div>
  );
}
```

### Example: Advanced Hook Composition

```tsx
// A custom hook built from multiple hooks
function useMovieFilters() {
  const { params, updateParams } = useQueryParams();
  const { genres } = useGenres();

  // Filter state synchronized with URL
  const { filters, setFilter, resetFilters, applyPreset } = useFilterURL({
    defaultFilters: { genre: [], year: null, rating: 0 },
    urlParams: params,
  });

  // Create preset filters
  const presets = useMemo(
    () => ({
      popular: { sort: "popularity", order: "desc" },
      newest: { sort: "release_date", order: "desc" },
      topRated: { sort: "rating", order: "desc" },
    }),
    []
  );

  return {
    filters,
    setFilter,
    resetFilters,
    genres,
    presets,
    applyPreset,
  };
}
```

## 📝 Guidelines

When creating new hooks:

1. **Placement**: Put the hook in the appropriate directory based on its responsibility
2. **Naming**: Use consistent naming convention `use[Resource][Action]`
3. **TypeScript**: Include comprehensive type definitions
4. **Error Handling**: Handle and expose errors appropriately
5. **Loading States**: Provide loading state indicators
6. **Documentation**: Add JSDoc comments for all functions and parameters
7. **Minimal Dependencies**: Avoid unnecessary dependencies
8. **Testing**: Write tests for all hooks
9. **Composability**: Design hooks to be composable with other hooks
10. **SSR Compatibility**: Ensure hooks work with server-side rendering

### React Query Pattern

For data fetching hooks, use React Query's patterns:

```tsx
export function useMovie(id: number) {
  return useQuery({
    queryKey: ["movie", id],
    queryFn: () => MovieAPI.getById(id),
    select: (data) => toMovieEntity(data),
  });
}

export function useToggleMovieLike(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (liked: boolean) =>
      liked ? MovieAPI.likeMovie(id) : MovieAPI.unlikeMovie(id),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["movie", id] });
    },
  });
}
```

## 🧪 Testing

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

## 🔄 Data Flow

The hooks layer connects the domain layer to the UI layer:

1. **UI Components** call hooks to interact with data
2. **Hooks** use services to fetch/update data from APIs
3. **Hooks** transform API data to domain entities
4. **UI Components** receive domain entities

## 📚 Related Documentation

For more details on specific hook categories:

- [Movie Hooks](./domain/movie/README.md) - Movie domain hooks
- [Domain Layer](../domain/README.md) - Domain layer architecture
- [Services API](../services/README.md) - API services documentation
