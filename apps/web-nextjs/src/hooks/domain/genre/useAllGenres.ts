"use client";

import { Genre } from "@/domain/entities";
import { GenreAPI } from "@/services/api";
import { useQuery } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useEffect } from "react";

// Create logger for this hook
const logger = createLogger("useAllGenres");

/**
 * Hook for fetching all genres
 *
 * @returns List of all genres, loading state, and error
 */
export function useAllGenres() {
  // Fetch all genres
  const {
    data: genres,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["genres"],
    queryFn: () => {
      logger.info("Fetching all genres");
      return GenreAPI.getAllGenres();
    },
    staleTime: 10 * 60 * 1000, // 10 minutes - genres rarely change
  });

  // Log when genres data is received
  useEffect(() => {
    if (genres) {
      logger.info(`Loaded ${genres.length} genres`);
    }
  }, [genres]);

  // Log errors
  useEffect(() => {
    if (error) {
      logger.error("Error fetching all genres:", error);
    }
  }, [error]);

  return {
    genres,
    isLoading,
    error,
  };
}

export default useAllGenres;
