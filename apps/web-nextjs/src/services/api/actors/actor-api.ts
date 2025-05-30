import { APIClient } from "../core/api-client";
import { ActorResponse, ActorScreenData } from "./types";
import { MovieListResponse } from "../movies/types";
import { MovieAPI } from "../movies/movie-api";
import { Actor } from "../common/types";
import { fetchData } from "../core/api-client";

/**
 * Client for actor-related API operations
 */
export const actorsClient = new APIClient<Actor>("/api/v1/actors");

/**
 * Enhanced Actor API with specialized methods beyond basic CRUD
 */
export const ActorAPI = {
  /**
   * Get actors with pagination and filters
   */
  getActors: async (params: {
    page?: number;
    pageSize?: number;
    search?: string;
    sortBy?: string;
    sort_desc?: boolean;
  }): Promise<ActorResponse> => {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.pageSize)
      queryParams.append("limit", params.pageSize.toString());
    if (params.search) queryParams.append("search", params.search);
    if (params.sortBy) queryParams.append("sort_by", params.sortBy);
    if (params.sort_desc !== undefined)
      queryParams.append("sort_desc", params.sort_desc.toString());

    return fetchData<ActorResponse>(`/bff/v1/actors?${queryParams.toString()}`);
  },

  /**
   * Get a single actor by ID with their movies
   */
  getById: async (id: number): Promise<ActorScreenData> => {
    return fetchData<ActorScreenData>(`/bff/v1/actors/${id}`);
  },

  /**
   * Get popular actors
   */
  getPopularActors: async (limit: number = 10): Promise<Actor[]> => {
    const response = await fetchData<ActorResponse>(
      `/bff/v1/actors/popular?limit=${limit}`
    );
    return response.actors;
  },

  /**
   * Search actors by name
   */
  searchActors: async (
    query: string,
    params: {
      page?: number;
      pageSize?: number;
      sortBy?: string;
      sort_desc?: boolean;
    } = {}
  ): Promise<ActorResponse> => {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.pageSize)
      queryParams.append("limit", params.pageSize.toString());
    if (params.sortBy) queryParams.append("sort_by", params.sortBy);
    if (params.sort_desc !== undefined)
      queryParams.append("sort_desc", params.sort_desc.toString());

    queryParams.append("search", query);

    return fetchData<ActorResponse>(`/bff/v1/actors?${queryParams.toString()}`);
  },

  /**
   * Get movies featuring a specific actor
   */
  getActorMovies: async (
    actorId: number,
    params: {
      page?: number;
      pageSize?: number;
      sortBy?: string;
      sort_desc?: boolean;
    } = {}
  ): Promise<MovieListResponse> => {
    return MovieAPI.getMoviesByActor(actorId, params);
  },
};
