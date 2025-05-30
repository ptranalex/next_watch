/**
 * Cache Keys Management
 *
 * Centralized cache key management for React Query.
 * Provides type-safe cache keys and utilities for cache operations.
 *
 * Following TanStack Query v5 best practices:
 * - Always use arrays (required in v5)
 * - Structure from most generic to most specific
 * - Include all variables that affect data
 */

// Core query key types - structured hierarchically
export type MovieListQueryKey =
  | ["movies", "lists", "home"]
  | ["movies", "lists", "search"]
  | ["movies", "lists", "search", "infinite", string]
  | ["movies", "lists", "genre", string, string]
  | ["movies", "lists", "actor", string, string]
  | ["movies", "lists", "user", "watched"]
  | ["movies", "lists", "user", "watchlist"]
  | ["movies", "lists", "user", "liked"]
  | ["movies", "lists", "top-by-year", string];

export type MovieQueryKey = ["movies", "detail", number];

export type UserInteractionQueryKey = ["movies", "interactions", number];

export type AllQueryKeys =
  | MovieListQueryKey
  | MovieQueryKey
  | UserInteractionQueryKey;

/**
 * Cache Keys factory following TkDodo's recommended pattern
 * Each level builds on the previous one for maximum flexibility
 */
export const CacheKeys = {
  // Base movie keys
  movies: {
    all: ["movies"] as const,

    // Movie lists
    lists: () => [...CacheKeys.movies.all, "lists"] as const,
    home: (): ["movies", "lists", "home"] => [
      ...CacheKeys.movies.lists(),
      "home",
    ],
    search: (): ["movies", "lists", "search"] => [
      ...CacheKeys.movies.lists(),
      "search",
    ],
    infiniteSearch: (
      query: string
    ): ["movies", "lists", "search", "infinite", string] => [
      ...CacheKeys.movies.lists(),
      "search",
      "infinite",
      query,
    ],
    genreList: (
      id: string,
      queryString: string
    ): ["movies", "lists", "genre", string, string] => [
      ...CacheKeys.movies.lists(),
      "genre",
      id,
      queryString,
    ],
    actorList: (
      id: string,
      queryString: string
    ): ["movies", "lists", "actor", string, string] => [
      ...CacheKeys.movies.lists(),
      "actor",
      id,
      queryString,
    ],

    // User-specific lists
    user: {
      watched: (): ["movies", "lists", "user", "watched"] => [
        ...CacheKeys.movies.lists(),
        "user",
        "watched",
      ],
      watchlist: (): ["movies", "lists", "user", "watchlist"] => [
        ...CacheKeys.movies.lists(),
        "user",
        "watchlist",
      ],
      liked: (): ["movies", "lists", "user", "liked"] => [
        ...CacheKeys.movies.lists(),
        "user",
        "liked",
      ],
    },

    topByYear: (year: string): ["movies", "lists", "top-by-year", string] => [
      ...CacheKeys.movies.lists(),
      "top-by-year",
      year,
    ],

    // Movie details
    details: () => [...CacheKeys.movies.all, "detail"] as const,
    detail: (id: number): ["movies", "detail", number] => [
      ...CacheKeys.movies.details(),
      id,
    ],

    // Movie interactions
    interactions: () => [...CacheKeys.movies.all, "interactions"] as const,
    interaction: (movieId: number): ["movies", "interactions", number] => [
      ...CacheKeys.movies.interactions(),
      movieId,
    ],
  },

  // Legacy aliases for backward compatibility
  homePage: (): ["movies", "lists", "home"] => CacheKeys.movies.home(),
  search: (): ["movies", "lists", "search"] => CacheKeys.movies.search(),
  infiniteSearch: (
    query: string
  ): ["movies", "lists", "search", "infinite", string] =>
    CacheKeys.movies.infiniteSearch(query),
  genreScreen: (
    id: string,
    queryString: string
  ): ["movies", "lists", "genre", string, string] =>
    CacheKeys.movies.genreList(id, queryString),
  actorScreen: (
    id: string,
    queryString: string
  ): ["movies", "lists", "actor", string, string] =>
    CacheKeys.movies.actorList(id, queryString),
  watchedMovies: (): ["movies", "lists", "user", "watched"] =>
    CacheKeys.movies.user.watched(),
  watchlistMovies: (): ["movies", "lists", "user", "watchlist"] =>
    CacheKeys.movies.user.watchlist(),
  likedMovies: (): ["movies", "lists", "user", "liked"] =>
    CacheKeys.movies.user.liked(),
  topMoviesByYear: (year: string): ["movies", "lists", "top-by-year", string] =>
    CacheKeys.movies.topByYear(year),
  movie: (id: number): ["movies", "detail", number] =>
    CacheKeys.movies.detail(id),
  userInteractions: (movieId: number): ["movies", "interactions", number] =>
    CacheKeys.movies.interaction(movieId),
} as const;

/**
 * Cache key utilities for pattern matching and operations
 */
export const CacheKeyUtils = {
  /**
   * Check if a query key matches movie list pattern
   */
  isMovieListKey: (
    queryKey: readonly unknown[]
  ): queryKey is MovieListQueryKey => {
    if (!Array.isArray(queryKey) || queryKey.length < 3) return false;

    return (
      queryKey[0] === "movies" &&
      queryKey[1] === "lists" &&
      typeof queryKey[2] === "string"
    );
  },

  /**
   * Check if a query key matches movie detail pattern
   */
  isMovieKey: (queryKey: readonly unknown[]): queryKey is MovieQueryKey => {
    return (
      Array.isArray(queryKey) &&
      queryKey.length === 3 &&
      queryKey[0] === "movies" &&
      queryKey[1] === "detail" &&
      typeof queryKey[2] === "number"
    );
  },

  /**
   * Check if a query key matches user interactions pattern
   */
  isUserInteractionKey: (
    queryKey: readonly unknown[]
  ): queryKey is UserInteractionQueryKey => {
    return (
      Array.isArray(queryKey) &&
      queryKey.length === 3 &&
      queryKey[0] === "movies" &&
      queryKey[1] === "interactions" &&
      typeof queryKey[2] === "number"
    );
  },

  /**
   * Get all possible movie list query key patterns for filtering
   * Updated to reflect new hierarchical structure
   */
  getMovieListPatterns: (): string[] => [
    "movies", // Can invalidate all movie-related queries
    // Specific list types for more granular control
    "home",
    "search",
    "infinite",
    "genre",
    "actor",
    "user",
    "watched",
    "watchlist",
    "liked",
    "top-by-year",
  ],

  /**
   * Extract movie ID from query key if applicable
   */
  extractMovieId: (queryKey: readonly unknown[]): number | null => {
    if (CacheKeyUtils.isMovieKey(queryKey)) {
      return queryKey[2];
    }
    if (CacheKeyUtils.isUserInteractionKey(queryKey)) {
      return queryKey[2];
    }
    return null;
  },

  /**
   * Check if a query key is for a specific movie (detail or interaction)
   */
  isMovieSpecificKey: (queryKey: readonly unknown[]): boolean => {
    return (
      CacheKeyUtils.isMovieKey(queryKey) ||
      CacheKeyUtils.isUserInteractionKey(queryKey)
    );
  },

  /**
   * Get the base pattern for a query key (first element)
   */
  getBasePattern: (queryKey: readonly unknown[]): string | null => {
    return Array.isArray(queryKey) &&
      queryKey.length > 0 &&
      typeof queryKey[0] === "string"
      ? queryKey[0]
      : null;
  },

  /**
   * Check if query key matches any movie-related pattern
   */
  isMovieRelated: (queryKey: readonly unknown[]): boolean => {
    return Array.isArray(queryKey) && queryKey[0] === "movies";
  },
};
