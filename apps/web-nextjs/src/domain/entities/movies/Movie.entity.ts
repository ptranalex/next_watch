import { Movie as ServiceMovie } from "@/services/api/movies/types";
import { Actor, Trailer } from "@/services/api/bff/types";

/**
 * UI-friendly Movie entity extending the API service type.
 * Primarily used in components and UI state management.
 *
 * This type:
 * 1. Makes all required API properties optional for UI flexibility
 * 2. Adds UI-specific helper properties
 * 3. Provides type safety for the application domain
 *
 * Property naming follows API convention:
 * - liked: Whether the user has liked the movie
 * - watched: Whether the user has watched the movie
 * - in_watchlist: Whether the movie is in the user's watchlist
 *
 * @interface Movie
 * @extends {Omit<ServiceMovie, "is_liked" | "is_watched" | "to_watch" | "is_recommended">}
 */
export interface Movie
  extends Omit<
    ServiceMovie,
    "is_liked" | "is_watched" | "to_watch" | "is_recommended"
  > {
  /**
   * Whether the user has liked the movie
   * @type {boolean}
   * @memberof Movie
   */
  liked?: boolean;

  /**
   * Whether the user has watched the movie
   * @type {boolean}
   * @memberof Movie
   */
  watched?: boolean;

  /**
   * Whether the movie is in the user's watchlist
   * @type {boolean}
   * @memberof Movie
   */
  in_watchlist?: boolean;

  /**
   * Whether the movie is recommended to the user
   * @type {boolean}
   * @memberof Movie
   */
  is_recommended?: boolean; // Keeping this name as is for now

  /**
   * UI state: whether the movie is selected in a list/grid view
   * @type {boolean}
   * @memberof Movie
   */
  isSelected?: boolean;

  /**
   * UI state: display order for sorting in lists
   * @type {number}
   * @memberof Movie
   */
  displayOrder?: number;

  /**
   * Cast members for the movie
   * @type {Actor[]}
   * @memberof Movie
   */
  cast?: Actor[];

  /**
   * Trailers for the movie
   * @type {Trailer[]}
   * @memberof Movie
   */
  trailers?: Trailer[];
}

/**
 * Helper function to convert a service movie to a UI entity
 *
 * @param {ServiceMovie} serviceMovie - The API service movie object
 * @returns {Movie} A UI-friendly movie entity
 */
export function toMovieEntity(serviceMovie: ServiceMovie): Movie {
  const { is_liked, is_watched, to_watch, ...rest } = serviceMovie;

  return {
    ...rest,
    // Map service movie properties to API naming convention
    liked: is_liked,
    watched: is_watched,
    in_watchlist: to_watch,
  };
}

/**
 * Helper function to convert a UI entity back to a service movie
 * Useful when sending updates to the API
 *
 * @param {Movie} movie - The UI movie entity
 * @returns {Partial<ServiceMovie>} A service-compatible movie object
 */
export function toServiceMovie(movie: Movie): Partial<ServiceMovie> {
  // Only map the properties that the service expects
  return {
    ...Object.fromEntries(
      Object.entries(movie).filter(
        ([key]) =>
          ![
            "liked",
            "watched",
            "in_watchlist",
            "cast",
            "trailers",
            "isSelected",
            "displayOrder",
          ].includes(key)
      )
    ),
    // Map UI naming to service properties
    is_liked: movie.liked ?? false,
    is_watched: movie.watched ?? false,
    to_watch: movie.in_watchlist ?? false,
    is_recommended: movie.is_recommended ?? false,
  };
}
