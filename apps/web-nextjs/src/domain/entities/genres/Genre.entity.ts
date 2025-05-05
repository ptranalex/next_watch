import { Genre as ServiceGenre } from "@/services/api/common/types";

/**
 * UI-friendly Genre entity extending the API service type.
 * Used for categorizing movies in the UI.
 *
 * This type:
 * 1. Directly extends the service type
 * 2. Adds UI-specific helper properties
 *
 * @interface Genre
 * @extends {ServiceGenre}
 */
export interface Genre extends ServiceGenre {
  /**
   * UI display color for the genre (e.g., for tags or categories)
   * @type {string}
   * @memberof Genre
   */
  color?: string;

  /**
   * Icon identifier for the genre
   * @type {string}
   * @memberof Genre
   */
  icon?: string;

  /**
   * UI state: whether the genre is selected in filters or lists
   * @type {boolean}
   * @memberof Genre
   */
  isSelected?: boolean;
}

/**
 * Helper function to convert a service genre to a UI entity
 *
 * @param {ServiceGenre} serviceGenre - The API service genre object
 * @returns {Genre} A UI-friendly genre entity
 */
export function toGenreEntity(serviceGenre: ServiceGenre): Genre {
  return {
    ...serviceGenre,
  };
}

/**
 * Helper function to convert a UI entity back to a service genre
 *
 * @param {Genre} genre - The UI genre entity
 * @returns {ServiceGenre} A service-compatible genre object
 */
export function toServiceGenre(genre: Genre): ServiceGenre {
  const { color, icon, isSelected, ...serviceProps } = genre;
  return serviceProps;
}
