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
  id: number;
  title: string;
  overview?: string;
  poster_url?: string;
  backdrop_url?: string;
  release_date?: string;
  imdb_rating?: number;
  is_liked: boolean;
  is_watched: boolean;
  to_watch: boolean;
  interaction_created_at: string;
  interaction_updated_at: string;
}
