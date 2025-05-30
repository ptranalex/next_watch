import { useQueryClient, QueryClient } from "@tanstack/react-query";
import { CacheManager } from "./strategies";
import { Movie } from "@/domain/entities";

/**
 * Global cache utilities for accessing the cache manager
 * instance created in providers.tsx
 */

// Extended QueryClient interface with cache manager
interface ExtendedQueryClient extends QueryClient {
  cacheManager?: CacheManager;
}

/**
 * Hook to access the global cache manager
 * This provides a clean API to access the cache manager
 * that was attached to the QueryClient in providers.tsx
 */
export function useGlobalCacheManager(): CacheManager {
  const queryClient = useQueryClient();

  // Access the cache manager that was attached in providers.tsx
  const extendedClient = queryClient as ExtendedQueryClient;
  const cacheManager = extendedClient.cacheManager;

  if (!cacheManager) {
    throw new Error(
      "Cache manager not found. Make sure providers.tsx is properly configured."
    );
  }

  return cacheManager;
}

/**
 * Global cache utilities that can be used outside of React components
 * Note: These require the QueryClient to be available in the React tree
 */
export class GlobalCacheUtils {
  private static instance: CacheManager | null = null;

  /**
   * Initialize the global cache manager
   * Called automatically by providers.tsx
   */
  static initialize(cacheManager: CacheManager) {
    this.instance = cacheManager;
  }

  /**
   * Get the global cache manager instance
   */
  static getInstance(): CacheManager {
    if (!this.instance) {
      throw new Error(
        "Global cache manager not initialized. Make sure providers.tsx is properly configured."
      );
    }
    return this.instance;
  }

  /**
   * Convenience methods for common cache operations
   */
  static async invalidateAllMovieLists() {
    return this.getInstance().invalidateMovieRelatedQueries(0, "debounced");
  }

  static async warmMovieCache(movieId: number) {
    return this.getInstance().warmRelatedCaches(movieId);
  }

  static updateMovieOptimistically(
    movieId: number,
    updateFn: (movie: Movie) => Movie
  ) {
    return this.getInstance().updateMovieOptimistically(movieId, updateFn);
  }

  static cleanupStaleData() {
    return this.getInstance().cleanupStaleMovieData();
  }
}
