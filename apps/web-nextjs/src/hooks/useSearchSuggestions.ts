import { useQuery } from "@tanstack/react-query";
import { Movie, Genre } from "../services/movie-service";

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
      const response = await fetch(
        `http://localhost:8000/search/suggestions?q=${encodeURIComponent(
          query
        )}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch search suggestions");
      }

      const data = await response.json();
      return data.suggestions as Suggestion[];
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export default useSearchSuggestions;
