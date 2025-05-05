import { APIClient, fetchData, postData, deleteData } from "../core/api-client";
import { Movie } from "@/domain/entities";
import { UserMovieInteractionResponse } from "./types";

/**
 * Helper function to convert API interaction format to UI format
 * This ensures consistent property name mapping throughout the application
 *
 * @param apiInteraction The raw API interaction response
 * @returns An object with renamed properties matching UI conventions
 */
export const mapApiInteractionToUi = (
  apiInteraction: UserMovieInteractionResponse | null
) => {
  if (!apiInteraction) return null;

  return {
    ...apiInteraction,
    // Map API property names to UI property names
    is_liked: apiInteraction.liked,
    is_watched: apiInteraction.watched,
    to_watch: apiInteraction.in_watchlist,
  };
};

/**
 * Helper function to convert UI format back to API format
 * Used when sending updates to the API
 *
 * @param uiInteraction UI-formatted interaction data
 * @returns API-formatted interaction data
 */
export const mapUiInteractionToApi = (uiInteraction: {
  id?: number;
  user_id?: number;
  movie_id: number;
  is_liked?: boolean;
  is_watched?: boolean;
  to_watch?: boolean;
  created_at?: string;
  updated_at?: string;
  [key: string]: any;
}): UserMovieInteractionResponse => {
  return {
    id: uiInteraction.id || 0,
    user_id: uiInteraction.user_id || 0,
    movie_id: uiInteraction.movie_id,
    liked: uiInteraction.is_liked || false,
    watched: uiInteraction.is_watched || false,
    in_watchlist: uiInteraction.to_watch || false,
    created_at: uiInteraction.created_at || new Date().toISOString(),
    updated_at: uiInteraction.updated_at || new Date().toISOString(),
  };
};

/**
 * User Interaction API Client
 *
 * Provides methods to interact with the user-movie interactions API endpoints.
 * This includes adding/removing movies to/from watchlist, liked, and watched lists.
 */
class UserInteractionAPI extends APIClient<UserMovieInteractionResponse> {
  constructor() {
    super("/api/v1/user/movies");
  }

  /**
   * Get user's interaction with a specific movie
   */
  getMovieInteraction = (
    movieId: number
  ): Promise<UserMovieInteractionResponse | null> => {
    return fetchData<UserMovieInteractionResponse | null>(
      `${this.endpoint}/${movieId}/interaction`
    );
  };

  /**
   * Toggle movie in user's watchlist
   */
  toggleWatchlist = async (
    movieId: number
  ): Promise<UserMovieInteractionResponse> => {
    return postData<UserMovieInteractionResponse>(
      `${this.endpoint}/${movieId}/watchlist`,
      {}
    );
  };

  /**
   * Toggle movie in user's watched list
   */
  toggleWatched = async (
    movieId: number
  ): Promise<UserMovieInteractionResponse> => {
    return postData<UserMovieInteractionResponse>(
      `${this.endpoint}/${movieId}/watched`,
      {}
    );
  };

  /**
   * Toggle movie in user's liked list
   */
  toggleLiked = async (
    movieId: number
  ): Promise<UserMovieInteractionResponse> => {
    return postData<UserMovieInteractionResponse>(
      `${this.endpoint}/${movieId}/liked`,
      {}
    );
  };

  /**
   * Delete all interactions with a movie
   */
  deleteInteraction = async (movieId: number): Promise<void> => {
    return deleteData<void>(`${this.endpoint}/${movieId}/interaction`);
  };

  /**
   * Get user's watchlist
   */
  getWatchlist = async (
    limit: number = 20,
    offset: number = 0
  ): Promise<UserMovieInteractionResponse[]> => {
    return fetchData<UserMovieInteractionResponse[]>(
      `${this.endpoint}/watchlist?limit=${limit}&offset=${offset}`
    );
  };

  /**
   * Get user's watched movies
   */
  getWatched = async (
    limit: number = 20,
    offset: number = 0
  ): Promise<UserMovieInteractionResponse[]> => {
    return fetchData<UserMovieInteractionResponse[]>(
      `${this.endpoint}/watched?limit=${limit}&offset=${offset}`
    );
  };

  /**
   * Get user's liked movies
   */
  getLiked = async (
    limit: number = 20,
    offset: number = 0
  ): Promise<UserMovieInteractionResponse[]> => {
    return fetchData<UserMovieInteractionResponse[]>(
      `${this.endpoint}/liked?limit=${limit}&offset=${offset}`
    );
  };

  /**
   * Get user's watchlist with detailed movie information
   */
  getWatchlistWithDetails = async (
    limit: number = 20,
    offset: number = 0
  ): Promise<UserMovieInteractionResponse[]> => {
    return fetchData<UserMovieInteractionResponse[]>(
      `${this.endpoint}/watchlist/details?limit=${limit}&offset=${offset}`
    );
  };

  /**
   * Get user's watched movies with detailed movie information
   */
  getWatchedWithDetails = async (
    limit: number = 20,
    offset: number = 0
  ): Promise<UserMovieInteractionResponse[]> => {
    return fetchData<UserMovieInteractionResponse[]>(
      `${this.endpoint}/watched/details?limit=${limit}&offset=${offset}`
    );
  };

  /**
   * Get user's liked movies with detailed movie information
   */
  getLikedWithDetails = async (
    limit: number = 20,
    offset: number = 0
  ): Promise<UserMovieInteractionResponse[]> => {
    return fetchData<UserMovieInteractionResponse[]>(
      `${this.endpoint}/liked/details?limit=${limit}&offset=${offset}`
    );
  };
}

// Create and export a singleton instance
const userInteractionAPI = new UserInteractionAPI();
export default userInteractionAPI;
