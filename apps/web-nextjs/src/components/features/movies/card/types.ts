import { Movie } from "@/domain/entities";

/**
 * Common types for movie card components
 */

// Common size variant used across card components
export type CardComponentSize = "sm" | "md" | "lg";

// Common orientation for card layouts
export type CardOrientation = "vertical" | "horizontal";

// Movie update callback - used by MovieCard, MovieQuickAction
export type MovieUpdateCallback = (updatedMovie: Movie) => void;

// Toggle callback - used by CardToggleIconButton and similar components
export type ToggleCallback = (isActive: boolean) => void;

// Movie attributes that can be toggled
export type ToggleableMovieAttribute = "watched" | "liked" | "in_watchlist";

// API endpoints for movie interactions
export type MovieInteractionEndpoint = "watched" | "liked" | "towatch";

// Props for movie card components that need movie and update callback
export interface MovieCardBaseProps {
  movie: Movie;
  onMovieUpdate: MovieUpdateCallback;
}

// Props for components that handle movie interactions
export interface MovieInteractionProps extends MovieCardBaseProps {
  size?: CardComponentSize;
  orientation?: CardOrientation;
}

// Props for toggle-based components
export interface ToggleComponentProps {
  movie: Movie;
  attribute: ToggleableMovieAttribute;
  endpoint: MovieInteractionEndpoint;
  onToggle: ToggleCallback;
  size?: CardComponentSize;
}
