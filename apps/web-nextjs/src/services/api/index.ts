/**
 * API Domain re-exports
 */

// Movie-related exports
export * from "./movies/types";
export * from "./movies/movie-api";

// Genre-related exports
export * from "./genres/types";
export * from "./genres/genre-api";

// Actor-related exports
export * from "./actors/types";
export * from "./actors/actor-api";

// Search-related exports
export * from "./search/types";
export * from "./search/search-api";

// Auth-related exports
export * from "./auth/types";
export * from "./auth/auth-api";

// User interaction exports
export * from "./user/types";
export {
  default as userInteractionAPI,
  mapApiInteractionToUi,
  mapUiInteractionToApi,
} from "./user/user-interaction-api";

// Core API utilities
export {
  APIClient,
  fetchData,
  postData,
  putData,
  deleteData,
} from "./core/api-client";
export * from "./core/errors";

// Export the API client as default
import apiClient from "./core/api-client";
export default apiClient;
