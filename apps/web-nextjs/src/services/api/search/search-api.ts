import { fetchData } from "../core/api-client";
import { SuggestionsResponse, TextSuggestionsResponse } from "./types";

/**
 * Search API with specialized search-related methods
 */
export const SearchAPI = {
  /**
   * Get search suggestions based on a query string (legacy/standard endpoint)
   */
  getSuggestions: async (
    query: string,
    limit: number = 10
  ): Promise<SuggestionsResponse> => {
    return fetchData<SuggestionsResponse>(
      `/api/v1/search/suggestions?query=${encodeURIComponent(
        query
      )}&limit=${limit}`
    );
  },

  /**
   * Get enhanced text-based search suggestions with rich metadata
   * This uses the improved text suggestions endpoint with deduplication and ranking.
   */
  getTextSuggestions: async (
    query: string,
    limit: number = 10
  ): Promise<TextSuggestionsResponse> => {
    return fetchData<TextSuggestionsResponse>(
      `/api/v1/search/suggestions/text?query=${encodeURIComponent(
        query
      )}&limit=${limit}`
    );
  },

  /**
   * Search across all entities (movies, actors, genres)
   */
  search: async (params: {
    query: string;
    types?: string[];
    page?: number;
    pageSize?: number;
    sortBy?: string;
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
    if (params.pageSize)
      queryParams.append("limit", params.pageSize.toString());
    if (params.sortBy) queryParams.append("sort_by", params.sortBy);
    if (params.sort_desc !== undefined)
      queryParams.append("sort_desc", params.sort_desc.toString());

    return fetchData<SuggestionsResponse>(
      `/api/v1/search?${queryParams.toString()}`
    );
  },
};
