/**
 * Cache Services Module
 *
 * This module provides centralized cache management for React Query,
 * including cache keys, strategies, and advanced cache operations.
 *
 * Part of the services layer for clean architecture.
 */

// Core cache management
export { CacheKeys, CacheKeyUtils } from "./keys";
export { CacheManager, createCacheManager } from "./strategies";

// Global cache utilities
export { useGlobalCacheManager, GlobalCacheUtils } from "./global";

// Types
export type {
  MovieListQueryKey,
  MovieQueryKey,
  UserInteractionQueryKey,
  AllQueryKeys,
} from "./keys";

export type { CacheUpdateContext } from "./strategies";

// Re-export for convenience (legacy compatibility)
export { CacheKeys as QueryKeys } from "./keys";

/**
 * Cache configuration recommendations:
 *
 * For most queries:
 * - staleTime: 2 * 60 * 1000 (2 minutes) - data is fresh for 2 minutes
 * - gcTime: 10 * 60 * 1000 (10 minutes) - inactive data kept for 10 minutes
 *
 * For static data (rarely changes):
 * - staleTime: Infinity - never considered stale
 * - gcTime: 10 * 60 * 1000 (10 minutes)
 *
 * For real-time data (frequently updated):
 * - staleTime: 0 - always considered stale (refetch on every use)
 * - gcTime: 5 * 60 * 1000 (5 minutes)
 */
export const CacheConfig = {
  defaultStaleTime: 2 * 60 * 1000, // 2 minutes
  defaultGcTime: 10 * 60 * 1000, // 10 minutes
  staticStaleTime: Number.POSITIVE_INFINITY,
  realtimeStaleTime: 0,
} as const;
