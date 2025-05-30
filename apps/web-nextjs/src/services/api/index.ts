/**
 * API Services
 *
 * This module exports all API-related services and utilities.
 * We've consolidated our API clients to use a single client that
 * communicates with the BFF API.
 */

// Re-export the core API client and utilities
export {
  apiClient,
  fetchData,
  postData,
  putData,
  deleteData,
  uploadFormData,
  APIClient,
  isTokenValid,
} from "./core/api-client";

// Export error types
export {
  APIError,
  NetworkError,
  ValidationError,
  AuthError,
  CacheHitError,
} from "./core/errors";

// Export domain-specific APIs
export { AuthAPI } from "./auth/auth-api";
export { default as UserAPI } from "./user/user-api";
export { default as userInteractionAPI } from "./user/user-interaction-api";
export { MovieAPI } from "./movies/movie-api";
export { MoviesAPI } from "./movies/movies-api";
export { GenreAPI } from "./genres/genre-api";
export { ActorAPI } from "./actors/actor-api";
export { SearchAPI } from "./search/search-api";

// Re-export BFF API for backward compatibility (deprecated)
export {
  bffFetchData,
  bffPostData,
  bffPutData,
  bffDeleteData,
  bffUploadFormData,
  createBFFClient,
} from "./core/api-client";

// Export types
export type { Actor } from "./common/types";
export type { Movie, MovieListResponse } from "./movies/types";
export type { ActorResponse, ActorScreenData } from "./actors/types";
export type { Genre, GenreResponse, GenreScreenData } from "./genres/types";
export type { User, UserMovieInteractionResponse } from "./user/types";
export type {
  SuggestionsResponse,
  TextSuggestionsResponse,
  MovieSearchResponse,
} from "./search/types";
export type {
  LoginCredentials,
  RegisterData,
  AuthTokens,
  UserData,
} from "./auth/types";
