"use client";

import { Actor } from "@/domain/entities";
import { ActorAPI } from "@/services/api";
import { useQuery } from "@tanstack/react-query";

/**
 * Hook for fetching and managing a single actor
 * @param id - Actor ID to fetch
 * @returns Actor data, loading state, error, and related information
 */
export function useActor(id: number) {
  // Fetch actor data
  const {
    data: actor,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["actor", id],
    queryFn: () => ActorAPI.getById(id),
    enabled: !!id,
  });

  // Get actor name with fallback
  const actorName = actor?.name || "Actor";

  // Fetch movies featuring this actor
  const moviesQuery = useQuery({
    queryKey: ["actorMovies", id],
    queryFn: () => ActorAPI.getActorMovies(id),
    enabled: !!id,
  });

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
