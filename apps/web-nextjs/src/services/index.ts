/**
 * Services module re-exports
 */

// Re-export API modules
export * from "./api";

// Legacy compatibility re-exports
// These will be removed in a future version
export {
  MovieAPI as MovieService,
  GenreAPI as GenreService,
  ActorAPI as ActorService,
} from "./api";

// Re-export API client utilities for backward compatibility
/**
 * @deprecated Import from "@/services/api" instead. This will be removed in the next version.
 */
export { APIClient, fetchData, postData, putData, deleteData } from "./api";

// Export the default client for backward compatibility
import apiClient from "./api";
export { apiClient as default };
