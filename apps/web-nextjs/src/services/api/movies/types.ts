/**
 * Types for Movie API domain
 */
import { Genre, Actor } from "../common/types";
import { Trailer } from "../bff/types";

export interface Movie {
  id: number;
  title: string;
  overview?: string;
  poster_path?: string;
  backdrop_path?: string;
  poster_url?: string;
  backdrop_url?: string;
  vote_average?: number;
  release_date?: string;
  genres?: Genre[];
  runtime?: number;
  rated?: string;
  trailer_link?: string;
  actors?: Actor[];

  // User interaction properties - standardized naming
  is_liked: boolean;
  is_watched: boolean;
  to_watch: boolean;
  is_recommended: boolean;

  // Rating properties with specific types
  imdb_rating?: number;
  rotten_tomatoes_rating?: number;
  metacritic_rating?: number;

  // Additional fields for movie attributes display
  imdb_id?: string;
  tmdb_id?: number;
  original_title?: string;
  budget?: number;
  revenue?: number;
  original_language?: string;
  status?: string;
  production_countries?: ProductionCountry[];
  production_companies?: ProductionCompany[];
  vote_count?: number;
  popularity?: number;
  tagline?: string;
  homepage?: string;
  fshare_link?: string;
  director?: string;
  writer?: string;
  awards?: string;
  origin_country?: string;

  // Index signature for dynamic properties
  [key: string]: MovieProperty;
}

// Specific types for movie properties
export type MovieProperty =
  | string
  | number
  | boolean
  | Genre[]
  | ProductionCountry[]
  | ProductionCompany[]
  | Trailer[]
  | undefined;

export interface ProductionCountry {
  iso_3166_1: string;
  name: string;
}

export interface ProductionCompany {
  id: number;
  name: string;
  logo_path?: string;
}

export interface MovieListResponse {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  results: Movie[];
}

export interface MoviesQueryParams {
  page?: number;
  pageSize?: number;
  limit?: number;
  genre_id?: number;
  actor_id?: number;
  search?: string;
  sort_by?: string;
  sort_desc?: boolean;
  year?: number;
  imdb_rating?: number;
  rotten_tomatoes_rating?: number;
  metacritic_rating?: number;
}

/**
 * Streaming source interface representing a video source for a movie
 */
export interface StreamingSource {
  id: string;
  title: string;
  quality: string;
  url: string;
  provider: string;
  type: "trailer" | "full" | "clip";
}

/**
 * Movie streaming sources response
 */
export interface MovieStreamingResponse {
  movie_id: number;
  title: string;
  sources: StreamingSource[];
}

/**
 * Movie cast response
 */
export interface MovieCastResponse {
  cast: {
    id: number;
    actor_id: number;
    name: string;
    character?: string;
    profile_path?: string;
    order?: number;
  }[];
  movie_id: number;
}
