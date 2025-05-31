/**
 * Google Analytics Utilities
 *
 * Provides utilities for tracking custom events and user interactions
 * using Google Analytics with direct gtag calls.
 */

import { createLogger } from "@/utils/logging";

const logger = createLogger("analytics");

/**
 * Development mode detection
 */
const isDevelopment = process.env.NODE_ENV === "development";

/**
 * Enhanced analytics event sender with logging and development features
 */
const sendAnalyticsEvent = (
  eventData: Record<string, string | number | boolean | undefined>
) => {
  try {
    // Always log in development, and log important events in production
    if (isDevelopment) {
      logger.info("📊 Analytics Event (DEV)", eventData);
      console.group("🔍 Google Analytics Event");
      console.log("Event Data:", eventData);
      console.log("Timestamp:", new Date().toISOString());
      console.log("Environment:", process.env.NODE_ENV);
      console.groupEnd();
    } else {
      logger.debug("Analytics event sent", eventData);
    }

    // Extract event name and parameters
    const { event, ...parameters } = eventData;
    const eventName = String(event || "unknown");

    // Use gtag directly (this works reliably)
    if (typeof window !== "undefined" && typeof window.gtag === "function") {
      window.gtag("event", eventName, parameters);
    } else {
      throw new Error("gtag is not available");
    }

    // Development verification
    if (isDevelopment) {
      // Add to window for debugging
      if (typeof window !== "undefined") {
        window.lastAnalyticsEvent = {
          ...eventData,
          event: eventName,
          timestamp: new Date().toISOString(),
        };
      }
    }

    return true;
  } catch (error) {
    logger.error("Failed to send analytics event", {
      eventData,
      error: error instanceof Error ? error.message : String(error),
    });

    if (isDevelopment) {
      console.error("❌ Analytics Error:", error);
    }

    return false;
  }
};

/**
 * Track movie interactions (view, like, watchlist, etc.)
 */
export const trackMovieEvent = (
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
  return sendAnalyticsEvent({
    event: "movie_interaction",
    movie_action: action,
    movie_id: movieId,
    movie_title: movieTitle,
  });
};

/**
 * Track search events
 */
export const trackSearchEvent = (
  query: string,
  resultsCount: number,
  filters?: {
    genre?: string;
    year?: number;
    sortBy?: string;
  }
) => {
  return sendAnalyticsEvent({
    event: "search",
    search_term: query,
    results_count: resultsCount,
    search_filters: filters ? JSON.stringify(filters) : undefined,
  });
};

/**
 * Track navigation events
 */
export const trackNavigationEvent = (destination: string, source?: string) => {
  return sendAnalyticsEvent({
    event: "navigation",
    destination,
    source,
  });
};

/**
 * Track user authentication events
 */
export const trackAuthEvent = (
  action: "login" | "logout" | "signup",
  method?: "google" | "email"
) => {
  return sendAnalyticsEvent({
    event: "auth",
    auth_action: action,
    auth_method: method,
  });
};

/**
 * Track feature usage
 */
export const trackFeatureEvent = (
  feature: string,
  action: string,
  value?: string | number
) => {
  return sendAnalyticsEvent({
    event: "feature_usage",
    feature_name: feature,
    feature_action: action,
    feature_value: value,
  });
};

/**
 * Track performance metrics
 */
export const trackPerformanceEvent = (
  metric: string,
  value: number,
  unit?: string
) => {
  return sendAnalyticsEvent({
    event: "performance",
    metric_name: metric,
    metric_value: value,
    metric_unit: unit,
  });
};

/**
 * Track errors
 */
export const trackErrorEvent = (
  errorType: string,
  errorMessage: string,
  errorLocation?: string
) => {
  return sendAnalyticsEvent({
    event: "error",
    error_type: errorType,
    error_message: errorMessage,
    error_location: errorLocation,
  });
};

/**
 * Track page views (for SPA navigation)
 * Note: This is automatically handled by the GoogleAnalytics component,
 * but can be used for custom page view tracking if needed
 */
export const trackPageView = (pagePath: string, pageTitle?: string) => {
  return sendAnalyticsEvent({
    event: "page_view",
    page_path: pagePath,
    page_title: pageTitle,
  });
};

/**
 * Development utilities for testing analytics
 */
export const analyticsDevUtils = {
  /**
   * Test all analytics functions with sample data
   */
  testAllEvents: () => {
    if (!isDevelopment) {
      console.warn("Analytics testing is only available in development mode");
      return;
    }

    console.group("🧪 Testing All Analytics Events");

    // Test movie event
    trackMovieEvent("like", 123, "Test Movie");

    // Test search event
    trackSearchEvent("test query", 5, { genre: "action", year: 2024 });

    // Test navigation event
    trackNavigationEvent("/test-page", "test-source");

    // Test auth event
    trackAuthEvent("login", "google");

    // Test feature event
    trackFeatureEvent("test-feature", "test-action", "test-value");

    // Test performance event
    trackPerformanceEvent("test-metric", 100, "ms");

    // Test error event
    trackErrorEvent("test-error", "Test error message", "test-location");

    // Test page view
    trackPageView("/test-page", "Test Page");

    console.log(
      "✅ All test events sent! Check console logs and GA Real-time reports."
    );
    console.groupEnd();
  },

  /**
   * Get the last analytics event (development only)
   */
  getLastEvent: () => {
    if (typeof window !== "undefined" && window.lastAnalyticsEvent) {
      return window.lastAnalyticsEvent;
    }
    return null;
  },

  /**
   * Check if Google Analytics is loaded
   */
  checkGAStatus: () => {
    if (typeof window !== "undefined") {
      const hasGtag = typeof window.gtag === "function";
      const hasDataLayer = Array.isArray(window.dataLayer);

      console.group("🔍 Google Analytics Status");
      console.log("gtag function available:", hasGtag);
      console.log("dataLayer available:", hasDataLayer);
      console.log("Environment:", process.env.NODE_ENV);
      console.log("Development mode:", isDevelopment);

      if (hasDataLayer && window.dataLayer) {
        console.log("dataLayer events:", window.dataLayer.length);
        console.log("Recent dataLayer events:", window.dataLayer.slice(-3));
      }

      console.groupEnd();

      return { hasGtag, hasDataLayer };
    }

    return { hasGtag: false, hasDataLayer: false };
  },

  /**
   * Send a test event directly to GA
   */
  sendTestEvent: () => {
    if (typeof window !== "undefined" && typeof window.gtag === "function") {
      console.log("🧪 Sending test event directly to GA...");
      window.gtag("event", "test_event", {
        test_parameter: "test_value",
        timestamp: new Date().toISOString(),
      });
      console.log("✅ Test event sent! Check GA Real-time reports.");
    } else {
      console.error("❌ gtag function not available");
    }
  },
};

// Add to window for easy access in development
if (isDevelopment && typeof window !== "undefined") {
  window.analyticsDevUtils = analyticsDevUtils;
  console.log("🔧 Analytics dev utils loaded:", window.analyticsDevUtils);
}

// Type declarations for development utilities
declare global {
  interface Window {
    lastAnalyticsEvent?: Record<
      string,
      string | number | boolean | undefined
    > & {
      event: string;
      timestamp: string;
    };
    analyticsDevUtils?: typeof analyticsDevUtils;
    gtag?: (...args: unknown[]) => void;
  }
}
