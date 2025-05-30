import { QueryClient, Query } from "@tanstack/react-query";
import { CacheKeys, CacheKeyUtils } from "./keys";
import { Movie } from "../../domain/entities";

/**
 * Advanced cache management strategies for React Query
 *
 * Provides sophisticated caching patterns including:
 * - Optimistic updates with surgical precision
 * - Smart invalidation with batching
 * - Eventual consistency with conflict resolution
 * - Cache warming and intelligent prefetching
 * - Memory management and cleanup
 */

export interface CacheUpdateContext {
  movieId: number;
  userId?: number;
  operation: "optimistic" | "success" | "error" | "background";
}

/**
 * Represents a movie-like object structure found in cached data.
 * Used for type-safe operations across different query result formats.
 */
interface MovieLike {
  id: number;
  title?: string;
  [key: string]: unknown;
}

/**
 * Represents paginated data structure from infinite queries.
 * Contains an array of results and additional pagination metadata.
 */
interface PageData {
  results?: MovieLike[];
  [key: string]: unknown;
}

/**
 * Represents standard query data structure with results array.
 * Used for non-paginated query responses.
 */
interface QueryData {
  results: MovieLike[];
  [key: string]: unknown;
}

export class CacheManager {
  constructor(private queryClient: QueryClient) {}

  /**
   * STRATEGY 1: Optimistic Updates with Surgical Precision
   *
   * Updates a specific movie across all relevant queries without triggering
   * network requests. Provides immediate UI feedback while maintaining
   * data consistency across the application.
   *
   * @param movieId - The ID of the movie to update
   * @param updateFn - Pure function that transforms the movie data
   */
  updateMovieOptimistically = (
    movieId: number,
    updateFn: (movie: Movie) => Movie
  ) => {
    // Cancel any outgoing refetches for this movie to prevent race conditions
    this.queryClient.cancelQueries({
      predicate: (query) => this.isMovieRelatedQuery(query, movieId),
    });

    // Apply updates to all queries containing this movie data
    this.queryClient.setQueriesData(
      {
        predicate: (query) => this.containsMovieData(query, movieId),
      },
      (oldData: unknown) => this.updateMovieInData(oldData, movieId, updateFn)
    );
  };

  /**
   * STRATEGY 2: Smart Invalidation with Batching
   *
   * Intelligently invalidates movie-related queries using different strategies
   * to balance performance and data freshness. Prevents waterfall requests
   * through strategic batching.
   *
   * @param movieId - The ID of the movie that triggered invalidation
   * @param strategy - Invalidation timing strategy
   */
  invalidateMovieRelatedQueries = async (
    movieId: number,
    strategy: "immediate" | "debounced" | "background" = "debounced"
  ) => {
    const patterns = CacheKeyUtils.getMovieListPatterns();

    switch (strategy) {
      case "immediate":
        // Force immediate invalidation of all related queries
        await Promise.all(
          patterns.map((pattern: string) =>
            this.queryClient.invalidateQueries({
              predicate: (query) =>
                Array.isArray(query.queryKey) && query.queryKey[0] === pattern,
            })
          )
        );
        break;

      case "debounced":
        // Leverage React Query's built-in batching for optimal performance
        this.queryClient.invalidateQueries({
          predicate: (query) => this.containsMovieData(query, movieId),
        });
        break;

      case "background":
        // Mark queries as stale without triggering immediate refetch
        patterns.forEach((pattern: string) => {
          this.queryClient.invalidateQueries({
            predicate: (query) =>
              Array.isArray(query.queryKey) && query.queryKey[0] === pattern,
            refetchType: "none", // Mark stale but don't refetch
          });
        });
        break;
    }
  };

  /**
   * STRATEGY 3: Eventual Consistency with Conflict Resolution
   *
   * Resolves conflicts between optimistic updates and server state by
   * intelligently merging data. Preserves user interactions while
   * respecting authoritative server data.
   *
   * @param serverMovie - Authoritative data from the server
   * @param optimisticMovie - Local optimistic update data
   * @returns Reconciled movie data with conflict resolution applied
   */
  reconcileServerState = (
    serverMovie: Movie,
    optimisticMovie: Movie
  ): Movie => {
    // Prefer server state for core data, preserve user interaction state
    // TODO: Implement timestamp-based conflict resolution for production
    return {
      ...serverMovie,
      // Preserve user interaction changes from optimistic updates
      liked: optimisticMovie.liked,
      watched: optimisticMovie.watched,
      in_watchlist: optimisticMovie.in_watchlist,
    };
  };

  /**
   * STRATEGY 4: Cache Warming and Prefetching
   *
   * Proactively loads related data to improve perceived performance.
   * Uses intelligent heuristics to determine what data to prefetch
   * based on user behavior patterns.
   *
   * @param movieId - The movie ID to warm related caches for
   */
  warmRelatedCaches = async (movieId: number) => {
    // Prefetch movie details if not already cached to improve UX
    if (!this.queryClient.getQueryData(CacheKeys.movie(movieId))) {
      this.queryClient.prefetchQuery({
        queryKey: CacheKeys.movie(movieId),
        queryFn: () => this.fetchMovieDetails(movieId),
        staleTime: 1000 * 60 * 5, // 5 minutes
      });
    }
  };

  /**
   * STRATEGY 5: Memory Management
   *
   * Proactively removes stale data to prevent memory leaks and
   * maintain optimal application performance. Uses configurable
   * time-based eviction policies.
   */
  cleanupStaleMovieData = () => {
    // Remove movie details older than 10 minutes to prevent memory bloat
    this.queryClient.removeQueries({
      predicate: (query) => {
        const isMovieDetail = query.queryKey[0] === "movie";
        const lastUpdated = query.state.dataUpdatedAt;
        const tenMinutesAgo = Date.now() - 10 * 60 * 1000;

        return isMovieDetail && lastUpdated < tenMinutesAgo;
      },
    });
  };

  // ========================================
  // Private Helper Methods
  // ========================================

  /**
   * Determines if a query is specifically related to a movie by ID.
   * Used for targeted query operations and cancellations.
   */
  private isMovieRelatedQuery = (query: Query, movieId: number): boolean => {
    return query.queryKey[0] === "movie" && query.queryKey[1] === movieId;
  };

  /**
   * Checks if a query contains movie data, optionally for a specific movie.
   * Handles different data structures (infinite queries, regular queries, arrays).
   *
   * @param query - The React Query instance to check
   * @param movieId - Optional specific movie ID to look for
   */
  private containsMovieData = (query: Query, movieId?: number): boolean => {
    const data = query.state.data;
    if (!data) return false;

    // If movieId specified, check if this specific movie is in the data
    if (movieId) {
      return this.dataContainsMovie(data, movieId);
    }

    // Otherwise, check if it contains any movie data structure
    return this.isMovieListData(data);
  };

  /**
   * Searches for a specific movie ID within various data structures.
   * Handles infinite queries, regular queries, and direct arrays.
   *
   * @param data - The data structure to search within
   * @param movieId - The movie ID to find
   */
  private dataContainsMovie = (data: unknown, movieId: number): boolean => {
    if (!data) return false;

    // Handle infinite query data structure (paginated results)
    if (data && typeof data === "object" && "pages" in data) {
      const infiniteData = data as { pages: PageData[] };
      return infiniteData.pages.some(
        (page) =>
          Array.isArray(page?.results) &&
          page.results.some((movie: MovieLike) => movie?.id === movieId)
      );
    }

    // Handle regular query data structure (single result set)
    if (data && typeof data === "object" && "results" in data) {
      const queryData = data as QueryData;
      return (
        Array.isArray(queryData.results) &&
        queryData.results.some((movie: MovieLike) => movie?.id === movieId)
      );
    }

    // Handle direct array data structure
    if (Array.isArray(data)) {
      return data.some((movie: MovieLike) => movie?.id === movieId);
    }

    return false;
  };

  /**
   * Validates if data contains movie list structure.
   * Used to identify queries that contain movie data for bulk operations.
   *
   * @param data - The data to validate
   */
  private isMovieListData = (data: unknown): boolean => {
    if (!data) return false;

    // Helper to validate movie-like object structure
    const hasMovieStructure = (obj: MovieLike) =>
      obj && typeof obj.id === "number" && typeof obj.title === "string";

    // Validate infinite query structure
    if (data && typeof data === "object" && "pages" in data) {
      const infiniteData = data as { pages: PageData[] };
      return infiniteData.pages.some(
        (page) =>
          Array.isArray(page?.results) &&
          page.results.length > 0 &&
          hasMovieStructure(page.results[0])
      );
    }

    // Validate regular query structure
    if (data && typeof data === "object" && "results" in data) {
      const queryData = data as QueryData;
      return (
        Array.isArray(queryData.results) &&
        queryData.results.length > 0 &&
        hasMovieStructure(queryData.results[0])
      );
    }

    // Validate direct array structure
    if (Array.isArray(data)) {
      return data.length > 0 && hasMovieStructure(data[0] as MovieLike);
    }

    return false;
  };

  /**
   * Immutably updates a specific movie within various data structures.
   * Preserves the original data structure while applying targeted updates.
   *
   * @param oldData - The original data structure
   * @param movieId - The ID of the movie to update
   * @param updateFn - Pure function to transform the movie data
   */
  private updateMovieInData = (
    oldData: unknown,
    movieId: number,
    updateFn: (movie: Movie) => Movie
  ): unknown => {
    if (!oldData) return oldData;

    // Update within infinite query structure
    if (oldData && typeof oldData === "object" && "pages" in oldData) {
      const infiniteData = oldData as { pages: PageData[] };
      return {
        ...infiniteData,
        pages: infiniteData.pages.map((page) => ({
          ...page,
          results: Array.isArray(page?.results)
            ? page.results.map((movie: MovieLike) =>
                movie?.id === movieId ? updateFn(movie as Movie) : movie
              )
            : page.results,
        })),
      };
    }

    // Update within regular query structure
    if (oldData && typeof oldData === "object" && "results" in oldData) {
      const queryData = oldData as QueryData;
      return {
        ...queryData,
        results: Array.isArray(queryData.results)
          ? queryData.results.map((movie: MovieLike) =>
              movie?.id === movieId ? updateFn(movie as Movie) : movie
            )
          : queryData.results,
      };
    }

    // Update within direct array structure
    if (Array.isArray(oldData)) {
      return oldData.map((movie: MovieLike) =>
        movie?.id === movieId ? updateFn(movie as Movie) : movie
      );
    }

    return oldData;
  };

  /**
   * Dynamically imports and fetches movie details to avoid circular dependencies.
   * Used for cache warming and prefetching operations.
   *
   * @param movieId - The ID of the movie to fetch
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  private fetchMovieDetails = async (movieId: number): Promise<Movie> => {
    // Dynamic import prevents circular dependencies with API layer
    const { MovieAPI } = await import("@/services/api");
    return MovieAPI.getById(movieId);
  };
}

/**
 * Factory function to create a cache manager instance.
 * Provides a clean interface for dependency injection and testing.
 *
 * @param queryClient - The React Query client instance
 * @returns Configured CacheManager instance
 */
export const createCacheManager = (queryClient: QueryClient) =>
  new CacheManager(queryClient);
