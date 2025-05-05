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

// Types for search suggestions (legacy format)
export interface Suggestion {
  type: "movie" | "actor" | "genre";
  info: any; // Will be Movie | Actor | Genre
}

// Legacy suggestion response format
export interface SuggestionsResponse {
  suggestions: Suggestion[];
}

// New enhanced text suggestions format
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
    type?: string;
    vote_average?: number;
    original_title_format?: string;
    [key: string]: any;
  };
}

export interface TextSuggestionsResponse {
  suggestions: TextSuggestion[];
  total: number;
}
