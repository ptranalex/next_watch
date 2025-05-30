/**
 * BFF API - Backend for Frontend Integration
 *
 * This module provides all API services through the BFF layer,
 * offering better performance, security, and user experience.
 */

// Export types
export * from "./types";

// Export API services
export { BFFMoviesAPI } from "./movies-api";
export { BFFAuthAPI } from "./auth-api";

// Create default export for easy importing
import { BFFMoviesAPI } from "./movies-api";
import { BFFAuthAPI } from "./auth-api";

/**
 * Combined BFF API object with all services
 */
export const BFFAPI = {
  movies: BFFMoviesAPI,
  auth: BFFAuthAPI,
};

export default BFFAPI;
