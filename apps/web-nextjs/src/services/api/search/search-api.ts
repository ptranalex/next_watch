import { fetchData } from "../core/api-client";
import { SuggestionsResponse, TextSuggestionsResponse } from "./types";
import { Movie } from "@/domain/entities/movies/Movie.entity";

/**
 * Movie search response from BFF API
 */
export interface MovieSearchResponse {
  query: string;
  results: Movie[];
  total_count: number;
  page: number;
  has_next: boolean;
}

/**
 * Search API with specialized search-related methods
 * Routes through BFF API for consistent authentication and caching
 */
export const SearchAPI = {
  /**
   * Get search suggestions based on a query string (legacy/standard endpoint)
   * Routes through BFF API
   */
  getSuggestions: async (
    query: string,
    limit: number = 10
  ): Promise<SuggestionsResponse> => {
    return fetchData<SuggestionsResponse>(
      `/bff/v1/search/suggestions?query=${encodeURIComponent(
        query
      )}&limit=${limit}`
    );
  },

  /**
   * Get enhanced text-based search suggestions with rich metadata
   * This uses the improved text suggestions endpoint with deduplication and ranking.
   * Routes through BFF API
   */
  getTextSuggestions: async (
    query: string,
    limit: number = 10
  ): Promise<TextSuggestionsResponse> => {
    return fetchData<TextSuggestionsResponse>(
      `/bff/v1/search/suggestions/text?query=${encodeURIComponent(
        query
      )}&limit=${limit}`
    );
  },

  /**
   * Search movies by title with comprehensive filtering options
   * Routes through BFF API for optimized movie search
   */
  searchMovies: async (params: {
    q: string;
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
    user_id?: number;
  }): Promise<MovieSearchResponse> => {
    const queryParams = new URLSearchParams();

    queryParams.append("q", params.q);

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.genre_id)
      queryParams.append("genre_id", params.genre_id.toString());
    if (params.actor_id)
      queryParams.append("actor_id", params.actor_id.toString());
    if (params.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params.sort_desc !== undefined)
      queryParams.append("sort_desc", params.sort_desc.toString());
    if (params.imdb_rating)
      queryParams.append("imdb_rating", params.imdb_rating.toString());
    if (params.rotten_tomatoes_rating)
      queryParams.append(
        "rotten_tomatoes_rating",
        params.rotten_tomatoes_rating.toString()
      );
    if (params.metacritic_rating)
      queryParams.append(
        "metacritic_rating",
        params.metacritic_rating.toString()
      );
    if (params.year) queryParams.append("year", params.year.toString());
    if (params.start_year)
      queryParams.append("start_year", params.start_year.toString());
    if (params.end_year)
      queryParams.append("end_year", params.end_year.toString());
    if (params.user_id)
      queryParams.append("user_id", params.user_id.toString());

    return fetchData<MovieSearchResponse>(
      `/bff/v1/search?${queryParams.toString()}`
    );
  },

  /**
   * Search across all entities (movies, actors, genres)
   * Routes through BFF API
   */
  searchAll: async (params: {
    query: string;
    types?: string[];
    page?: number;
    limit?: number;
    sort_by?: string;
    sort_desc?: boolean;
  }): Promise<SuggestionsResponse> => {
    const queryParams = new URLSearchParams();

    queryParams.append("query", params.query);

    if (params.types && params.types.length > 0) {
      params.types.forEach((type) => {
        queryParams.append("types", type);
      });
    }

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params.sort_desc !== undefined)
      queryParams.append("sort_desc", params.sort_desc.toString());

    return fetchData<SuggestionsResponse>(
      `/bff/v1/search/all?${queryParams.toString()}`
    );
  },
};
