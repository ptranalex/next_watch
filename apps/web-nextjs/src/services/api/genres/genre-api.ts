import { APIClient, fetchData } from "../core/api-client";
import { GenreResponse } from "./types";
import { Genre } from "../common/types";

/**
 * Client for genre-related API operations
 */
export const genresClient = new APIClient<Genre>("/api/v1/genres");

/**
 * Enhanced Genre API with specialized methods beyond basic CRUD
 */
export const GenreAPI = {
  /**
   * Get all movie genres
   */
  getAllGenres: async (): Promise<Genre[]> => {
    const response = await fetchData<GenreResponse>("/api/v1/genres");
    return response.genres;
  },

  /**
   * Get details for a single genre by ID
   */
  getById: async (id: number): Promise<Genre> => {
    return genresClient.getById(id);
  },

  /**
   * Get popular genres
   */
  getPopularGenres: async (limit: number = 10): Promise<Genre[]> => {
    const response = await fetchData<GenreResponse>(
      `/api/v1/genres/popular?limit=${limit}`
    );
    return response.genres;
  },
};
