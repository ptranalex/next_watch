/**
 * Analytics Module
 *
 * Barrel export for Google Analytics utilities and tracking functions.
 * Provides a clean import interface for analytics-related functionality.
 *
 * @example
 * ```typescript
 * import {
 *   trackMovieEvent,
 *   trackSearchEvent,
 *   analyticsDevUtils
 * } from '@/services/analytics';
 *
 * // Track movie interaction
 * trackMovieEvent('like', 123, 'The Matrix');
 *
 * // Track search
 * trackSearchEvent('action movies', 25, { genre: 'action' });
 * ```
 */

// Core tracking functions
export {
  trackMovieEvent,
  trackSearchEvent,
  trackNavigationEvent,
  trackAuthEvent,
  trackFeatureEvent,
  trackPerformanceEvent,
  trackErrorEvent,
  trackPageView,
  analyticsDevUtils,
} from "./analytics";

// Import functions for internal use
import {
  trackMovieEvent,
  trackSearchEvent,
  trackNavigationEvent,
  trackAuthEvent,
  trackFeatureEvent,
  trackPerformanceEvent,
  trackErrorEvent,
  trackPageView,
  analyticsDevUtils,
} from "./analytics";

// Re-export for convenience - commonly used tracking functions
export const analytics = {
  movie: trackMovieEvent,
  search: trackSearchEvent,
  navigation: trackNavigationEvent,
  auth: trackAuthEvent,
  feature: trackFeatureEvent,
  performance: trackPerformanceEvent,
  error: trackErrorEvent,
  pageView: trackPageView,
} as const;

// Type definitions for analytics events
export type MovieAction =
  | "view"
  | "like"
  | "unlike"
  | "add_to_watchlist"
  | "remove_from_watchlist"
  | "mark_watched"
  | "unmark_watched";

export type AuthAction = "login" | "logout" | "signup";
export type AuthMethod = "google" | "email";

export type SearchFilters = {
  genre?: string;
  year?: number;
  sortBy?: string;
};

/**
 * Analytics utilities organized by category for easy access
 */
export const Analytics = {
  /**
   * Movie-related tracking
   */
  movie: {
    view: (movieId: number, movieTitle?: string) =>
      trackMovieEvent("view", movieId, movieTitle),
    like: (movieId: number, movieTitle?: string) =>
      trackMovieEvent("like", movieId, movieTitle),
    unlike: (movieId: number, movieTitle?: string) =>
      trackMovieEvent("unlike", movieId, movieTitle),
    addToWatchlist: (movieId: number, movieTitle?: string) =>
      trackMovieEvent("add_to_watchlist", movieId, movieTitle),
    removeFromWatchlist: (movieId: number, movieTitle?: string) =>
      trackMovieEvent("remove_from_watchlist", movieId, movieTitle),
    markWatched: (movieId: number, movieTitle?: string) =>
      trackMovieEvent("mark_watched", movieId, movieTitle),
    unmarkWatched: (movieId: number, movieTitle?: string) =>
      trackMovieEvent("unmark_watched", movieId, movieTitle),
  },

  /**
   * Search-related tracking
   */
  search: {
    query: (query: string, resultsCount: number, filters?: SearchFilters) =>
      trackSearchEvent(query, resultsCount, filters),
  },

  /**
   * Navigation tracking
   */
  navigation: {
    navigate: (destination: string, source?: string) =>
      trackNavigationEvent(destination, source),
  },

  /**
   * Authentication tracking
   */
  auth: {
    login: (method?: AuthMethod) => trackAuthEvent("login", method),
    logout: (method?: AuthMethod) => trackAuthEvent("logout", method),
    signup: (method?: AuthMethod) => trackAuthEvent("signup", method),
  },

  /**
   * Feature usage tracking
   */
  feature: {
    use: (feature: string, action: string, value?: string | number) =>
      trackFeatureEvent(feature, action, value),
  },

  /**
   * Performance tracking
   */
  performance: {
    metric: (metric: string, value: number, unit?: string) =>
      trackPerformanceEvent(metric, value, unit),
  },

  /**
   * Error tracking
   */
  error: {
    track: (errorType: string, errorMessage: string, errorLocation?: string) =>
      trackErrorEvent(errorType, errorMessage, errorLocation),
  },

  /**
   * Page view tracking
   */
  page: {
    view: (pagePath: string, pageTitle?: string) =>
      trackPageView(pagePath, pageTitle),
  },

  /**
   * Development utilities
   */
  dev: analyticsDevUtils,
} as const;

// Default export for convenience
export default Analytics;
