"use client";

import { toActorEntity } from "@/domain/entities";
import { ActorAPI, MovieListResponse } from "@/services/api";
import { useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * Hook for fetching and managing a single actor
 * @param id - Actor ID to fetch
 * @returns Actor data, loading state, error, and related information
 */
export function useActor(id: number) {
  const queryClient = useQueryClient();

  // Fetch actor data
  const {
    data: serviceActor,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["actor", id],
    queryFn: () => ActorAPI.getById(id),
    enabled: !!id,
  });

  // Convert service actor to entity
  const actor = serviceActor ? toActorEntity(serviceActor) : undefined;

  // Fetch movies featuring this actor
  const moviesQuery = useQuery<MovieListResponse>({
    queryKey: ["actorMovies", id],
    queryFn: () => ActorAPI.getActorMovies(id),
    enabled: !!id,
  });

  return {
    actor,
    isLoading,
    error,
    movies: moviesQuery.data?.movies || [],
    totalMovies: moviesQuery.data?.total || 0,
  };
}
