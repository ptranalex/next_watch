"use client";

import { Actor } from "@/domain/entities";
import { ActorAPI } from "@/services/api";
import { useQuery } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useEffect } from "react";

// Create logger for this hook
const logger = createLogger("useActor");

/**
 * Hook for fetching and managing a single actor
 * @param id - Actor ID to fetch
 * @returns Actor data, loading state, error, and related information
 */
export function useActor(id: number) {
  // Log hook initialization
  logger.debug(`useActor initialized with id: ${id}`);

  // Fetch actor data
  const {
    data: actor,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["actor", id],
    queryFn: () => {
      logger.info(`Fetching actor data for id: ${id}`);
      return ActorAPI.getById(id);
    },
    enabled: !!id,
  });

  // Get actor name with fallback
  const actorName = actor?.name || "Actor";

  // Fetch movies featuring this actor
  const moviesQuery = useQuery({
    queryKey: ["actorMovies", id],
    queryFn: () => {
      logger.info(`Fetching movies for actor id: ${id}`);
      return ActorAPI.getActorMovies(id);
    },
    enabled: !!id,
    onSuccess: (data) => {
      logger.info(
        `Fetched ${data?.movies?.length || 0} movies for actor: ${actorName}`
      );
    },
  });

  // Log errors
  useEffect(() => {
    if (error) {
      logger.error(`Error fetching actor data for id ${id}:`, error);
    }
    if (moviesQuery.error) {
      logger.error(
        `Error fetching actor movies for id ${id}:`,
        moviesQuery.error
      );
    }
  }, [error, moviesQuery.error, id, actorName]);

  return {
    actor,
    actorName,
    isLoading,
    error,
    movies: moviesQuery.data?.movies || [],
    totalMovies: moviesQuery.data?.total || 0,
  };
}

export default useActor;
