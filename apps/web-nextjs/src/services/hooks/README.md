***REMOVED*** React Hooks

This directory contains all the React hooks used in the application, organized by their responsibility.

***REMOVED******REMOVED*** 📂 Structure

```
hooks/
├── core/                ***REMOVED*** Application-wide hooks
│   ├── useAuth.ts       ***REMOVED*** Authentication hooks
│   ├── useSettings.ts   ***REMOVED*** Application settings
│   └── useProtectedRoute.ts ***REMOVED*** Route protection logic
├── domain/              ***REMOVED*** Domain-specific hooks
│   ├── movie/           ***REMOVED*** Movie-related hooks
│   │   ├── useMovie.ts  ***REMOVED*** Individual movie data
│   │   ├── useMovieList.ts ***REMOVED*** Movie listings
│   │   ├── useMovieActions.ts ***REMOVED*** Movie interactions
│   │   └── useMovieSearch.ts ***REMOVED*** Search functionality
│   ├── user/            ***REMOVED*** User-related hooks
│   │   ├── useProfile.ts ***REMOVED*** User profile data
│   │   └── usePreferences.ts ***REMOVED*** User preferences
│   ├── genre/           ***REMOVED*** Genre-related hooks
│   └── actors/          ***REMOVED*** Actor-related hooks
├── ui/                  ***REMOVED*** UI-related hooks
│   ├── useDebounce.ts   ***REMOVED*** Input debounce
│   ├── useIntersectionObserver.ts ***REMOVED*** Scroll detection
│   ├── useLocalStorage.ts ***REMOVED*** Local storage persistence
│   ├── useMediaQuery.ts ***REMOVED*** Media query matching
│   ├── useSwipe.ts      ***REMOVED*** Swipe gesture detection
│   └── useHapticFeedback.ts ***REMOVED*** Haptic feedback utilities
├── performance/         ***REMOVED*** Performance optimization hooks
│   ├── useMemoizedCallback.ts ***REMOVED*** Callback memoization
│   ├── useDeepCompareMemo.ts ***REMOVED*** Deep comparison memoization
│   └── useDebouncedEffect.ts ***REMOVED*** Debounced effects
├── navigation/          ***REMOVED*** Navigation-related hooks
│   ├── useRouteParams.ts ***REMOVED*** Route parameter access
│   ├── useQueryParams.ts ***REMOVED*** URL query parameter handling
│   └── useNavigation.ts ***REMOVED*** Navigation utilities
├── filter/              ***REMOVED*** Filter and sorting hooks
│   ├── useFilterState.ts ***REMOVED*** Filter state management
│   ├── useSortOptions.ts ***REMOVED*** Sorting options
│   └── useFilterURL.ts  ***REMOVED*** URL-based filtering
└── index.ts             ***REMOVED*** Re-exports all hooks
```

***REMOVED******REMOVED*** 🧩 Hook Categories

***REMOVED******REMOVED******REMOVED*** Core Hooks

Core hooks handle application-wide concerns:

- **Authentication**: Login, logout, and user state management
- **Authorization**: Access control and permissions
- **Routing**: Navigation and route protection
- **Configuration**: App-wide settings and feature flags
- **Theme**: Theme selection and application

***REMOVED******REMOVED******REMOVED*** Domain Hooks

Domain hooks interact with specific business domains:

- **Movie hooks**: Fetch and manage movie data
- **User hooks**: Fetch and manage user data
- **Genre hooks**: Fetch and manage genre data
- **Search hooks**: Handle search functionality
- **Watchlist hooks**: Manage user watchlist

***REMOVED******REMOVED******REMOVED*** UI Hooks

UI hooks handle presentation concerns:

- **useDebounce**: Delay value updates for input fields
- **useMediaQuery**: Respond to viewport changes
- **useIntersectionObserver**: Detect element visibility
- **useLocalStorage**: Persist data in browser storage
- **useSwipe**: Detect and handle swipe gestures
- **useHapticFeedback**: Trigger device vibration feedback

***REMOVED******REMOVED******REMOVED*** Performance Hooks

Performance hooks optimize rendering and data flow:

- **useMemoizedCallback**: Enhanced useCallback with deep comparisons
- **useDeepCompareMemo**: useMemo with deep equality checks
- **useDebouncedEffect**: useEffect with debounce to prevent rapid re-executions
- **useLazyRef**: Lazy initialization of refs with complex values

***REMOVED******REMOVED******REMOVED*** Navigation Hooks

Navigation hooks simplify routing and navigation:

- **useRouteParams**: Access and validate route parameters
- **useQueryParams**: Parse and update URL query parameters
- **useNavigation**: Navigate between routes with type safety
- **useScrollRestoration**: Restore scroll position when navigating

***REMOVED******REMOVED******REMOVED*** Filter Hooks

Filter hooks handle data filtering and sorting:

- **useFilterState**: Manage filter criteria state
- **useSortOptions**: Define and apply sorting logic
- **useFilterURL**: Synchronize filters with URL parameters
- **useInfiniteScroll**: Load more data on scroll

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

***REMOVED******REMOVED******REMOVED*** Example: Combined Hooks

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

***REMOVED******REMOVED******REMOVED*** Example: Advanced Hook Composition

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
9. **Composability**: Design hooks to be composable with other hooks
10. **SSR Compatibility**: Ensure hooks work with server-side rendering

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
