import { useQuery } from "@tanstack/react-query";
import { SearchAPI } from "../services/movies-api";

/**
 * Hook to fetch search suggestions based on a query string
 *
 * @param query The search term to get suggestions for
 * @returns Query result with suggestions
 */
const useSearchSuggestions = (query: string) => {
  return useQuery({
    queryKey: ["search_suggestions", query],
    queryFn: () => SearchAPI.getSuggestions(query),
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export default useSearchSuggestions;
