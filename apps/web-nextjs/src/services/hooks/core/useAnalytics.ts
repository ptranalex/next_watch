/**
 * Analytics Hook
 *
 * Provides a React hook interface for tracking analytics events
 * throughout the application using Google Analytics.
 *
 * This is a thin wrapper around the centralized analytics utilities
 * that provides a React-friendly interface with useCallback optimization.
 */

import { useCallback } from "react";
import { createLogger } from "@/utils/logging";
import {
  trackMovieEvent,
  trackSearchEvent,
  trackNavigationEvent,
  trackAuthEvent,
  trackFeatureEvent,
  trackPerformanceEvent,
  trackErrorEvent,
  trackPageView,
} from "@/services/analytics/analytics";

const logger = createLogger("useAnalytics");

/**
 * Hook for analytics tracking
 *
 * Provides methods for tracking various types of events in the application.
 * All tracking is done through the centralized analytics utilities.
 *
 * @example
 * ```tsx
 * const analytics = useAnalytics();
 *
 * // Track movie interaction
 * analytics.trackMovie("like", 123, "The Matrix");
 *
 * // Track search
 * analytics.trackSearch("batman", 25, { genre: "action" });
 *
 * // Track navigation
 * analytics.trackNavigation("/movies/123", "home");
 * ```
 */
export const useAnalytics = () => {
  /**
   * Track movie-related interactions
   */
  const trackMovie = useCallback(
    (
      action:
        | "view"
        | "like"
        | "unlike"
        | "add_to_watchlist"
        | "remove_from_watchlist"
        | "mark_watched"
        | "unmark_watched",
      movieId: number,
      movieTitle?: string
    ) => {
      return trackMovieEvent(action, movieId, movieTitle);
    },
    []
  );

  /**
   * Track search events
   */
  const trackSearch = useCallback(
    (
      query: string,
      resultsCount: number,
      filters?: {
        genre?: string;
        year?: number;
        sortBy?: string;
      }
    ) => {
      return trackSearchEvent(query, resultsCount, filters);
    },
    []
  );

  /**
   * Track navigation events
   */
  const trackNavigation = useCallback(
    (destination: string, source?: string) => {
      return trackNavigationEvent(destination, source);
    },
    []
  );

  /**
   * Track authentication events
   */
  const trackAuth = useCallback(
    (action: "login" | "logout" | "signup", method?: "google" | "email") => {
      return trackAuthEvent(action, method);
    },
    []
  );

  /**
   * Track feature usage
   */
  const trackFeature = useCallback(
    (feature: string, action: string, value?: string | number) => {
      return trackFeatureEvent(feature, action, value);
    },
    []
  );

  /**
   * Track performance metrics
   */
  const trackPerformance = useCallback(
    (metric: string, value: number, unit?: string) => {
      return trackPerformanceEvent(metric, value, unit);
    },
    []
  );

  /**
   * Track errors
   */
  const trackError = useCallback(
    (errorType: string, errorMessage: string, errorLocation?: string) => {
      return trackErrorEvent(errorType, errorMessage, errorLocation);
    },
    []
  );

  /**
   * Track custom page views (for SPA navigation)
   */
  const trackPage = useCallback((pagePath: string, pageTitle?: string) => {
    return trackPageView(pagePath, pageTitle);
  }, []);

  // Log hook initialization
  logger.debug("useAnalytics hook initialized");

  return {
    trackMovie,
    trackSearch,
    trackNavigation,
    trackAuth,
    trackFeature,
    trackPerformance,
    trackError,
    trackPage,
  };
};
