/**
 * Centralized configuration for the Next.js application
 * This module exports configuration values sourced from environment variables.
 */

// Environment detection
export const isDevelopment = process.env.NODE_ENV === "development";
export const isProduction = process.env.NODE_ENV === "production";
export const isTest = process.env.NODE_ENV === "test";

// API Configuration
export const API_CONFIG = {
  /**
   * Base URL for the API
   * In browser contexts, this must be prefixed with NEXT_PUBLIC_
   */
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",

  /**
   * API version
   */
  version: process.env.NEXT_PUBLIC_API_VERSION || "v1",

  /**
   * Timeout for API requests in milliseconds
   */
  timeout: Number(process.env.NEXT_PUBLIC_API_TIMEOUT || 10000),
};

// Feature Flags
export const FEATURES = {
  /**
   * Enable/disable related movies section
   */
  enableRelatedMovies:
    process.env.NEXT_PUBLIC_ENABLE_RELATED_MOVIES !== "false",

  /**
   * Enable/disable movie recommendations
   */
  enableRecommendations:
    process.env.NEXT_PUBLIC_ENABLE_RECOMMENDATIONS !== "false",

  /**
   * Enable/disable movie cast display
   */
  enableCast: process.env.NEXT_PUBLIC_ENABLE_CAST !== "false",

  /**
   * Enable/disable search functionality
   */
  enableSearch: process.env.NEXT_PUBLIC_ENABLE_SEARCH !== "false",

  /**
   * Enable/disable movie trailers
   */
  enableTrailers: process.env.NEXT_PUBLIC_ENABLE_TRAILERS !== "false",

  /**
   * Enable/disable Fshare links
   */
  enableFshare: process.env.NEXT_PUBLIC_ENABLE_FSHARE !== "false",

  /**
   * Enable/disable detailed attributes
   */
  enableDetailedAttributes:
    process.env.NEXT_PUBLIC_ENABLE_DETAILED_ATTRIBUTES !== "false",
};

// Authentication Configuration
export const AUTH_CONFIG = {
  /**
   * Auth token storage key in localStorage
   */
  tokenKey: process.env.NEXT_PUBLIC_AUTH_TOKEN_KEY || "auth_token",

  /**
   * Token expiration time in seconds
   */
  tokenExpiration: Number(process.env.NEXT_PUBLIC_TOKEN_EXPIRATION || 86400), // 24 hours

  /**
   * Google OAuth client ID
   */
  googleClientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "",

  /**
   * Default expiration time for login sessions (in seconds)
   */
  sessionExpiration: 60 * 60 * 24 * 7, // 7 days
};

// Analytics Configuration (server-side only)
export const ANALYTICS_CONFIG = {
  /**
   * Google Analytics ID
   */
  gaTrackingId: process.env.GA_TRACKING_ID || "",

  /**
   * Enable/disable analytics in development
   */
  enableInDev: process.env.ENABLE_ANALYTICS_IN_DEV === "true",
};

// Content Delivery Network configuration
export const CDN_CONFIG = {
  /**
   * Images CDN base URL
   */
  imagesCdnUrl:
    process.env.NEXT_PUBLIC_IMAGES_CDN_URL || "https://image.tmdb.org/t/p",

  /**
   * Default image width for posters
   */
  posterSize: process.env.NEXT_PUBLIC_POSTER_SIZE || "w500",

  /**
   * Default image width for backdrops
   */
  backdropSize: process.env.NEXT_PUBLIC_BACKDROP_SIZE || "original",

  /**
   * Default image width for profiles
   */
  profileSize: process.env.NEXT_PUBLIC_PROFILE_SIZE || "w185",
};

// This is used to validate essential configuration during build/startup
export const validateConfig = (): string[] => {
  const issues: string[] = [];

  // Add checks for critical config values
  if (!API_CONFIG.baseUrl) {
    issues.push("API_URL is not configured");
  }

  // Return all issues found
  return issues;
};

// Export a default config object that combines all config sections
const config = {
  api: API_CONFIG,
  features: FEATURES,
  auth: AUTH_CONFIG,
  analytics: ANALYTICS_CONFIG,
  cdn: CDN_CONFIG,
  isDevelopment,
  isProduction,
  isTest,
};

export default config;
