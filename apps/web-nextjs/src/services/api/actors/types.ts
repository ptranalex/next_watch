/**
 * Types for Actor API
 */
import { Actor } from "../common/types";

export type { Actor };

export interface ActorResponse {
  actors: Actor[];
  total: number;
  page?: number;
  page_size?: number;
}

export interface ActorScreenData {
  data: {
    id: number;
    name: string;
    profile_path: string | null;
    biography: string | null;
    tmdb_id: number;
  };
  related: {
    movies: {
      total: number;
      page: number;
      per_page: number;
      total_pages: number;
      has_next: boolean;
      has_prev: boolean;
      results: Array<{
        id: number;
        tmdb_id: number;
        title: string;
        overview: string;
        release_date: string;
        poster_url: string | null;
        backdrop_url: string | null;
        vote_average: number;
        imdb_rating: number | null;
        imdb_id: string | null;
        runtime: number | null;
        director: string | null;
        writer: string | null;
        genres: Array<{
          id: number;
          name: string;
          tmdb_id: number;
        }>;
        metacritic_rating: number | null;
        rotten_tomatoes_rating: number | null;
        awards: string;
        original_language: string;
        created_at: string;
        updated_at: string;
        liked: boolean;
        watched: boolean;
        in_watchlist: boolean;
        user_interactions: {
          in_watchlist: boolean;
          is_favorite: boolean;
          user_rating: number | null;
          watch_progress: number;
          is_watched: boolean;
        };
      }>;
    };
  };
  context: {
    pagination: {
      page: number;
      limit: number;
      total_movies: number;
    };
    personalized: boolean;
  };
  metadata: {
    service_info: {
      aggregated_from: string[];
      user_authenticated: boolean;
    };
    api_version: string;
    response_pattern: string;
    actor_context: {
      actor_id: number;
    };
  };
}
