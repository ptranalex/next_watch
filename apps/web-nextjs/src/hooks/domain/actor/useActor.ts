"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ActorAPI } from "@/services/api";
import { Actor, toActorEntity } from "@/domain/entities";
import { MovieListResponse } from "@/services/api";

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
