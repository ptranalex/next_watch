/**
 * BFF API Types - matches the standardized pagination format
 */

// Import base types from existing modules
import { Movie } from "../movies/types";
import { Genre } from "../common/types";

/**
 * Standardized pagination response format used by BFF API
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
 * Movie list response from BFF API
 */
export type BFFMovieListResponse = PaginatedResponse<Movie>;

/**
 * Enhanced movie with user interactions for movie detail screen
 */
export interface MovieDetailData {
  movie: Movie;
  cast: Actor[];
  trailers: Trailer[];
  similar_movies: Movie[];
  user_interactions: UserInteractions;
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
