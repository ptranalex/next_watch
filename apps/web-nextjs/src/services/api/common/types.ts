/**
 * Common types shared across domains
 */

export interface Genre {
  id: number;
  name: string;
}

export interface Actor {
  id: number; // Credit ID in some contexts, but generally actor_id/tmdb_person_id will be used as the primary identifier
  actor_id: number; // TMDB person ID - primary identifier across the app
  name: string;
  profile_path?: string;
  biography?: string;
  birthday?: string;
  place_of_birth?: string;
  popularity?: number;
  gender?: number;
  known_for_department?: string;
  also_known_as?: string[];
}

// Basic movie info for suggestions (to avoid circular imports)
export interface MovieInfo {
  id: number;
  title: string;
  overview?: string;
  poster_path?: string;
  release_date?: string;
  vote_average?: number;
}

// Basic suggestion item (used in search results)
export interface Suggestion {
  id: number;
  name: string;
  type: string; // "movie", "actor", "genre", etc.
  image_path?: string | null;
}

// Enhanced text suggestion item with rich metadata
export interface TextSuggestion {
  text: string;
  type: string; // "movie", "actor", "director", etc.
  id: number | null;
  image_path: string | null;
  year?: number | null;
  popularity?: number | null;
  is_partial: boolean;
  search_type: "exact" | "prefix" | "word" | "contains" | "unknown";
  additional_info?: {
    title?: string;
    name?: string;
    type?: string;
    vote_average?: number;
    original_title_format?: string;
    gender?: number | null;
    [key: string]: string | number | boolean | null | undefined;
  };
}

// Metadata structure from ResponseBuilder
export interface SearchMetadata {
  total: number;
  service_info: {
    aggregated_from: string[];
    user_authenticated: boolean;
  };
  api_version: string;
  response_pattern: string;
  search_context: {
    search_type: string;
    suggestion_type?: string;
    entity_types?: string[] | null;
  };
}

// Updated suggestion response format using ResponseBuilder search pattern
export interface SuggestionsResponse {
  query: string;
  results: Suggestion[];
  metadata: SearchMetadata;
}

// Updated text suggestions response format using ResponseBuilder search pattern
export interface TextSuggestionsResponse {
  query: string;
  results: TextSuggestion[];
  metadata: SearchMetadata;
}

// Movie search response type alias (uses existing ResponseBuilderPaginatedResponse from BFF types)
export type MovieSearchResponse =
  import("../bff/types").ResponseBuilderPaginatedResponse<
    import("../movies/types").Movie
  >;
