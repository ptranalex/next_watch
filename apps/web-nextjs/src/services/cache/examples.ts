/**
 * CacheKeyUtils Usage Examples
 *
 * This file demonstrates practical ways to use CacheKeyUtils functions
 * to replace manual query key checking throughout the application.
 */

import { QueryClient } from "@tanstack/react-query";
import { CacheKeys, CacheKeyUtils } from "./keys";
import { Movie } from "@/domain/entities";

/**
 * EXAMPLE 1: Smart Query Invalidation
 * Replace manual string checking with type-safe utilities
 */

// ❌ BEFORE: Manual checking (error-prone, inconsistent)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function invalidateMovieListsManual(queryClient: QueryClient) {
  queryClient.invalidateQueries({
    predicate: (query) => {
      return query.queryKey[0] === "movies" && query.queryKey[1] === "lists";
    },
  });
}

// ✅ AFTER: Using CacheKeyUtils (type-safe, consistent)
function invalidateMovieListsWithUtils(queryClient: QueryClient) {
  queryClient.invalidateQueries({
    predicate: (query) => CacheKeyUtils.isMovieListKey(query.queryKey),
  });
}

/**
 * EXAMPLE 2: Selective Cache Updates
 * Update specific movie data across all relevant queries
 */

// ❌ BEFORE: Complex manual checking
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function updateMovieInCacheManual(
  queryClient: QueryClient,
  movieId: number,
  updateFn: (movie: Movie) => Movie
) {
  queryClient.setQueriesData(
    {
      predicate: (query) => {
        // Manual checking for movie detail queries
        if (
          query.queryKey[0] === "movies" &&
          query.queryKey[1] === "detail" &&
          query.queryKey[2] === movieId
        ) {
          return true;
        }

        // Manual checking for movie list queries
        if (query.queryKey[0] === "movies" && query.queryKey[1] === "lists") {
          return true;
        }

        return false;
      },
    },
    (oldData) => {
      // Update logic would use updateFn here
      console.log("Updating with function:", updateFn.name);
      return oldData;
    }
  );
}

// ✅ AFTER: Using CacheKeyUtils
function updateMovieInCacheWithUtils(
  queryClient: QueryClient,
  movieId: number,
  updateFn: (movie: Movie) => Movie
) {
  queryClient.setQueriesData(
    {
      predicate: (query) => {
        // Check if it's the specific movie detail
        if (
          CacheKeyUtils.isMovieKey(query.queryKey) &&
          CacheKeyUtils.extractMovieId(query.queryKey) === movieId
        ) {
          return true;
        }

        // Check if it's any movie list that might contain this movie
        return CacheKeyUtils.isMovieListKey(query.queryKey);
      },
    },
    (oldData) => {
      // Update logic would use updateFn here
      console.log("Updating with function:", updateFn.name);
      return oldData;
    }
  );
}

/**
 * EXAMPLE 3: Granular Cache Management
 * Different strategies for different query types
 */

// ✅ Using CacheKeyUtils for sophisticated cache management
function smartCacheInvalidation(queryClient: QueryClient, movieId: number) {
  // Get all queries in the cache
  const allQueries = queryClient.getQueryCache().getAll();

  const movieDetailQueries = allQueries.filter((query) =>
    CacheKeyUtils.isMovieKey(query.queryKey)
  );

  const movieListQueries = allQueries.filter((query) =>
    CacheKeyUtils.isMovieListKey(query.queryKey)
  );

  const userInteractionQueries = allQueries.filter((query) =>
    CacheKeyUtils.isUserInteractionKey(query.queryKey)
  );

  const specificMovieQueries = allQueries.filter(
    (query) =>
      CacheKeyUtils.isMovieSpecificKey(query.queryKey) &&
      CacheKeyUtils.extractMovieId(query.queryKey) === movieId
  );

  console.log("Cache Analysis:", {
    totalQueries: allQueries.length,
    movieDetails: movieDetailQueries.length,
    movieLists: movieListQueries.length,
    userInteractions: userInteractionQueries.length,
    specificToMovie: specificMovieQueries.length,
  });

  // Invalidate only what's needed
  queryClient.invalidateQueries({
    predicate: (query) => {
      // Invalidate specific movie data
      if (
        CacheKeyUtils.isMovieSpecificKey(query.queryKey) &&
        CacheKeyUtils.extractMovieId(query.queryKey) === movieId
      ) {
        return true;
      }

      // Invalidate movie lists (they might contain this movie)
      return CacheKeyUtils.isMovieListKey(query.queryKey);
    },
  });
}

/**
 * EXAMPLE 4: Cache Debugging and Monitoring
 * Use utilities for better debugging
 */

// ✅ Debug cache state with CacheKeyUtils
function debugCacheState(queryClient: QueryClient) {
  const allQueries = queryClient.getQueryCache().getAll();

  const cacheReport = {
    total: allQueries.length,
    byType: {
      movieDetails: 0,
      movieLists: 0,
      userInteractions: 0,
      other: 0,
    },
    movieIds: new Set<number>(),
    staleQueries: 0,
    errorQueries: 0,
  };

  allQueries.forEach((query) => {
    // Categorize by type
    if (CacheKeyUtils.isMovieKey(query.queryKey)) {
      cacheReport.byType.movieDetails++;
      const movieId = CacheKeyUtils.extractMovieId(query.queryKey);
      if (movieId) cacheReport.movieIds.add(movieId);
    } else if (CacheKeyUtils.isMovieListKey(query.queryKey)) {
      cacheReport.byType.movieLists++;
    } else if (CacheKeyUtils.isUserInteractionKey(query.queryKey)) {
      cacheReport.byType.userInteractions++;
      const movieId = CacheKeyUtils.extractMovieId(query.queryKey);
      if (movieId) cacheReport.movieIds.add(movieId);
    } else {
      cacheReport.byType.other++;
    }

    // Check state
    if (query.isStale()) cacheReport.staleQueries++;
    if (query.state.error) cacheReport.errorQueries++;
  });

  console.log("Cache Report:", {
    ...cacheReport,
    uniqueMovies: cacheReport.movieIds.size,
  });

  return cacheReport;
}

/**
 * EXAMPLE 5: Prefetching Strategy
 * Smart prefetching based on query types
 */

// ✅ Smart prefetching with CacheKeyUtils
function smartPrefetchStrategy(queryClient: QueryClient, movieIds: number[]) {
  movieIds.forEach((movieId) => {
    const movieDetailKey = CacheKeys.movies.detail(movieId);

    // Only prefetch if not already cached
    if (!queryClient.getQueryData(movieDetailKey)) {
      queryClient.prefetchQuery({
        queryKey: movieDetailKey,
        queryFn: async () => {
          // Fetch movie details
          const response = await fetch(`/api/movies/${movieId}`);
          return response.json();
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
      });
    }
  });
}

/**
 * EXAMPLE 6: Cache Cleanup Strategy
 * Remove stale data intelligently
 */

// ✅ Intelligent cache cleanup
function cleanupStaleCache(queryClient: QueryClient) {
  const now = Date.now();
  const fiveMinutesAgo = now - 5 * 60 * 1000;
  const tenMinutesAgo = now - 10 * 60 * 1000;

  // Remove old movie details
  queryClient.removeQueries({
    predicate: (query) => {
      return (
        CacheKeyUtils.isMovieKey(query.queryKey) &&
        query.state.dataUpdatedAt < tenMinutesAgo
      );
    },
  });

  // Remove old user interactions
  queryClient.removeQueries({
    predicate: (query) => {
      return (
        CacheKeyUtils.isUserInteractionKey(query.queryKey) &&
        query.state.dataUpdatedAt < fiveMinutesAgo
      );
    },
  });

  console.log("Cache cleanup completed");
}

/**
 * EXAMPLE 7: Query Key Analysis
 * Analyze and categorize all cache keys
 */

// ✅ Comprehensive query analysis
function analyzeCacheKeys(queryClient: QueryClient) {
  const allQueries = queryClient.getQueryCache().getAll();

  const analysis = {
    patterns: {
      movieRelated: 0,
      movieSpecific: 0,
      unknown: 0,
    },
    basePatterns: new Map<string, number>(),
    movieIds: new Set<number>(),
  };

  allQueries.forEach((query) => {
    const queryKey = query.queryKey;

    // Use utilities for pattern detection
    if (CacheKeyUtils.isMovieRelated(queryKey)) {
      analysis.patterns.movieRelated++;

      if (CacheKeyUtils.isMovieSpecificKey(queryKey)) {
        analysis.patterns.movieSpecific++;
        const movieId = CacheKeyUtils.extractMovieId(queryKey);
        if (movieId) analysis.movieIds.add(movieId);
      }
    } else {
      analysis.patterns.unknown++;
    }

    // Track base patterns
    const basePattern = CacheKeyUtils.getBasePattern(queryKey);
    if (basePattern) {
      analysis.basePatterns.set(
        basePattern,
        (analysis.basePatterns.get(basePattern) || 0) + 1
      );
    }
  });

  return {
    ...analysis,
    uniqueMovies: analysis.movieIds.size,
    basePatterns: Object.fromEntries(analysis.basePatterns),
  };
}

export {
  invalidateMovieListsWithUtils,
  updateMovieInCacheWithUtils,
  smartCacheInvalidation,
  debugCacheState,
  smartPrefetchStrategy,
  cleanupStaleCache,
  analyzeCacheKeys,
};
