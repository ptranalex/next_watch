/**
 * BFF API Types - matches the standardized pagination format
 */

// Import base types from existing modules
import { Movie } from "../movies/types";
import { Genre } from "../common/types";

/**
 * Standardized pagination response format used by BFF API (legacy format)
 */
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  results: T[];
}

/**
 * ResponseBuilder pagination info
 */
export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  total_pages?: number;
  has_next?: boolean;
  has_prev?: boolean;
}

/**
 * ResponseBuilder paginated response format
 */
export interface ResponseBuilderPaginatedResponse<T> {
  results: T[];
  pagination: PaginationInfo;
  metadata?: Record<string, unknown>;
}

/**
 * Movie list response from BFF API (legacy format)
 */
export type BFFMovieListResponse = PaginatedResponse<Movie>;

/**
 * Movie list response from BFF API (ResponseBuilder format)
 */
export type BFFMovieListResponseRB = ResponseBuilderPaginatedResponse<Movie>;

/**
 * Enhanced movie with user interactions for movie detail screen (legacy format)
 */
export interface MovieDetailData {
  movie: Movie;
  cast: Actor[];
  trailers: Trailer[];
  similar_movies: Movie[];
  user_interactions: UserInteractions;
}

/**
 * ResponseBuilder format for movie detail response
 */
export interface MovieDetailResponse {
  data: Movie;
  related: {
    cast: Actor[];
    trailers: Trailer[];
    similar_movies: SimilarMovie[];
  };
  context: {
    user_interactions: UserInteractions;
    personalized: boolean;
  };
  metadata: {
    service_info: Record<string, unknown>;
    api_version: string;
  };
}

/**
 * Similar movie with recommendation metadata
 */
export interface SimilarMovie extends Movie {
  similarity_score?: number;
  recommendation_reason?: string;
}

/**
 * User interaction data for a movie
 */
export interface UserInteractions {
  in_watchlist: boolean;
  is_favorite: boolean;
  user_rating?: number;
  watch_progress: number;
  is_watched: boolean;
}

/**
 * Actor information
 */
export interface Actor {
  id: number;
  name: string;
  character?: string;
  profile_path?: string;
  order?: number;
}

/**
 * Trailer information
 */
export interface Trailer {
  id: number;
  name: string;
  youtube_key: string;
  url_link: string;
  is_official: boolean;
  movie_id: number;
  created_at: string;
  updated_at: string;
}

/**
 * Home screen aggregated data
 */
export interface HomeScreenData {
  featured_movies: Movie[];
  popular_movies: Movie[];
  recent_releases: Movie[];
  user_recommendations: Movie[];
  genres: Genre[];
}

/**
 * Genre screen data with pagination
 */
export interface GenreScreenData {
  genre: Genre;
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  results: Movie[];
}

/**
 * Search results
 */
export interface SearchResults {
  query: string;
  results: Movie[];
  total_count: number;
  page: number;
  has_next: boolean;
}

/**
 * Query parameters for movie lists
 */
export interface BFFMovieQueryParams {
  page?: number;
  limit?: number;
  genre_id?: number;
  actor_id?: number;
  sort_by?: string;
  sort_desc?: boolean;
  imdb_rating?: number;
  rotten_tomatoes_rating?: number;
  metacritic_rating?: number;
  year?: number;
  start_year?: number;
  end_year?: number;
}

/**
 * Authentication data for requests
 */
export interface AuthRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    email: string;
    name?: string;
  };
}
