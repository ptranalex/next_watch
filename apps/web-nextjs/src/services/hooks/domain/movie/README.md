***REMOVED*** Movie Hooks

This directory contains hooks for working with movie data in the application.

***REMOVED******REMOVED*** 🔄 API Conventions

We follow the backend API naming conventions for movie user interactions:

| Property Name  | Description                                  |
| -------------- | -------------------------------------------- |
| `liked`        | Whether the user has liked the movie         |
| `watched`      | Whether the user has watched the movie       |
| `in_watchlist` | Whether the movie is in the user's watchlist |

***REMOVED******REMOVED******REMOVED*** API Response Structure

User movie interactions from the API follow this structure:

```typescript
interface UserMovieInteractionResponse {
  id: number;
  user_id: number;
  movie_id: number;
  liked: boolean;
  watched: boolean;
  in_watchlist: boolean;
  rating?: number;
  created_at: string;
  updated_at: string;
}
```

***REMOVED******REMOVED*** 🧩 Available Hooks

***REMOVED******REMOVED******REMOVED*** `useMovie`

Fetches and manages a single movie's data:

```typescript
const {
  movie, // Movie entity with full details
  isLoading, // Loading state
  error, // Error state
  toggleLiked, // Function to toggle liked status
  toggleWatched, // Function to toggle watched status
  toggleWatchlist, // Function to toggle watchlist status
  cast, // Array of cast members
} = useMovie(movieId);
```

***REMOVED******REMOVED******REMOVED*** `useMovies`

Fetches and manages a paginated list of movies:

```typescript
const {
  movies, // Array of Movie entities
  isLoading, // Loading state
  error, // Error state
  hasNextPage, // Whether there are more pages
  fetchNextPage, // Function to load next page
  isFetchingNextPage, // Whether next page is loading
  filter, // Filter options
} = useMovies(filterOptions);
```

***REMOVED******REMOVED******REMOVED*** `useMovieTrailer`

Fetches movie trailer information:

```typescript
const {
  trailer, // Trailer data if available
  isLoading, // Loading state
  error, // Error state
} = useMovieTrailer(movieId);
```

***REMOVED******REMOVED******REMOVED*** `useMovieCast`

Fetches movie cast information:

```typescript
const {
  cast, // Array of cast members
  isLoading, // Loading state
  error, // Error state
} = useMovieCast(movieId);
```

***REMOVED******REMOVED******REMOVED*** `useTopMovies`

Fetches top-rated movies:

```typescript
const {
  movies, // Array of top-rated movies
  isLoading, // Loading state
  error, // Error state
} = useTopMovies({
  limit: 10, // Number of movies to fetch
  sortBy: "imdb_rating", // Sort criteria
});
```

***REMOVED******REMOVED*** 🔄 Data Flow

These hooks integrate with the domain layer to transform API data:

1. **API Data** is fetched from backend services
2. Data is transformed to **Domain Entities** using conversion functions
3. **React Components** receive the entity data for display
4. **User Interactions** are processed and sent back to the API

***REMOVED******REMOVED*** 💡 Usage Examples

***REMOVED******REMOVED******REMOVED*** Single Movie Page

```tsx
function MovieDetail({ movieId }) {
  const { movie, isLoading, error, toggleLiked } = useMovie(movieId);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!movie) return <NotFound />;

  return (
    <div>
      <h1>{movie.title}</h1>
      <p>{movie.overview}</p>
      <button onClick={toggleLiked}>{movie.liked ? "Unlike" : "Like"}</button>
    </div>
  );
}
```

***REMOVED******REMOVED******REMOVED*** Movie Grid with Infinite Scroll

```tsx
function MovieGrid() {
  const { movies, isLoading, hasNextPage, fetchNextPage, isFetchingNextPage } =
    useMovies();

  return (
    <div>
      <div className="grid">
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </div>

      {(hasNextPage || isLoading) && (
        <button
          onClick={() => fetchNextPage()}
          disabled={!hasNextPage || isFetchingNextPage}
        >
          {isFetchingNextPage ? "Loading more..." : "Load more"}
        </button>
      )}
    </div>
  );
}
```

***REMOVED******REMOVED*** 🧪 Testing

Example test for a movie hook:

```typescript
describe("useMovie", () => {
  it("should fetch movie data", async () => {
    // Mock API response
    server.use(
      rest.get("/api/movies/1", (req, res, ctx) => {
        return res(ctx.json({ id: 1, title: "Test Movie" }));
      })
    );

    const { result, waitForNextUpdate } = renderHook(() => useMovie(1));

    // Initial state should be loading
    expect(result.current.isLoading).toBe(true);

    // Wait for the query to resolve
    await waitForNextUpdate();

    // Should have movie data
    expect(result.current.movie).toEqual(
      expect.objectContaining({ id: 1, title: "Test Movie" })
    );
  });
});
```
