import { SearchAPI } from "@/services/api";
import { TextSuggestionsResponse } from "@/services/api/search/types";
import { useQuery } from "@tanstack/react-query";

/**
 * Hook to fetch enhanced search suggestions based on a query string
 *
 * @param query The search term to get suggestions for
 * @param limit Maximum number of suggestions to return
 * @returns Query result with rich suggestions including metadata
 */
export const useSearchSuggestions = (query: string, limit: number = 10) => {
  return useQuery<TextSuggestionsResponse>({
    queryKey: ["search_suggestions", query, limit],
    queryFn: () => SearchAPI.getTextSuggestions(query, limit),
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};
