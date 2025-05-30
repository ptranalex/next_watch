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
  actor: {
    id: number;
    name: string;
    profile_path: string | null;
    biography: string | null;
    birthday: string | null;
    deathday: string | null;
    place_of_birth: string | null;
    popularity: number;
  };
  movies: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
    results: Array<{
      id: number;
      title: string;
      poster_path: string | null;
      release_date: string;
      vote_average: number;
      user_interactions: {
        in_watchlist: boolean;
        is_favorite: boolean;
        user_rating: number | null;
        watch_progress: number;
        is_watched: boolean;
      };
    }>;
  };
}
