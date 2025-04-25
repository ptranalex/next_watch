import { useQuery } from "@tanstack/react-query";
import { Movie, Genre } from "../services/movie-service";
import { fetchData } from "../services/api-client";

// Type for actor which will need to be added to movie-service later
interface Actor {
  id: number;
  name: string;
  profile_path?: string;
  popularity?: number;
}

// Combined suggestion interface
export interface Suggestion {
  type: "movie" | "actor" | "genre";
  info: Movie | Actor | Genre;
}

interface SuggestionsResponse {
  suggestions: Suggestion[];
}

/**
 * Hook to fetch search suggestions based on a query string
 *
 * @param query The search term to get suggestions for
 * @returns Query result with suggestions
 */
const useSearchSuggestions = (query: string) => {
  return useQuery({
    queryKey: ["search_suggestions", query],
    queryFn: async () => {
      // If query is empty, return empty array
      if (!query || query.length < 2) return [];

      // Fetch from API
      const data = await fetchData<SuggestionsResponse>(
        `/search/suggestions?q=${encodeURIComponent(query)}`
      );

      return data.suggestions;
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export default useSearchSuggestions;
