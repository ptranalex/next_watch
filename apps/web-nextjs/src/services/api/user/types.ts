import { Movie } from "@/domain/entities";

/**
 * Response from the user interaction API endpoints
 */
export interface UserMovieInteractionResponse {
  id: number;
  user_id: number;
  movie_id: number;
  liked: boolean;
  watched: boolean;
  in_watchlist: boolean;
  rating?: number;
  created_at: string;
  updated_at: string;
}

/**
 * User movie interaction with movie details
 */
export interface UserMovieInteractionWithMovie
  extends Omit<
    UserMovieInteractionResponse,
    "liked" | "watched" | "in_watchlist"
  > {
  movie: Movie;
  is_liked: boolean;
  is_watched: boolean;
  to_watch: boolean;
}

/**
 * User movie detail (optimized response)
 */
export interface UserMovieDetail {
  interaction_id: number | null;
  movie_id: number;
  title: string;
  poster_url: string | null;
  release_date: string | null;
  watched: boolean;
  liked: boolean;
  in_watchlist: boolean;
  imdb_rating: number | null;
}

/**
 * User model from API
 */
export interface User {
  id: number;
  email: string;
  username?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Import results for Netflix history
 */
export interface NetflixImportResult {
  total_entries: number;
  matched_movies: number;
  already_marked_watched: number;
  newly_marked_watched: number;
  unmatched_titles: string[];
}
