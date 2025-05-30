/**
 * Services Module
 *
 * This module provides access to all API services in the application.
 * Prefer importing from '@/services/api' directly for new code.
 */

// =============================================================================
// Current API exports - use these for new code
// =============================================================================

// Re-export all API modules
export * from "./api";

// Re-export default API client
import { APIClient } from "./api";
export { APIClient as default };

// =============================================================================
// Legacy compatibility exports - these will be removed in future versions
// =============================================================================

/**
 * @deprecated Service aliases maintained for backward compatibility.
 * Import from '@/services/api' instead.
 */
export {
  // Service aliases
  MovieAPI as MovieService,
  GenreAPI as GenreService,
  ActorAPI as ActorService,

  // Auth service backward compatibility
  AuthAPI as authService,

  // Core utilities
  APIClient,
  fetchData,
  postData,
  putData,
  deleteData,
} from "./api";
