/**
 * Movie Card Components
 *
 * This module exports all the components related to movie card functionality,
 * including the main card component, rating indicators, and supporting utilities.
 */

// Types
export type {
  ComponentSize,
  MovieCardOrientation,
  MovieUpdateCallback,
  ToggleableMovieAttribute,
  MovieInteractionEndpoint,
  MovieCardBaseProps,
  MovieInteractionProps,
  MovieCardProps,
  MovieCardContainerProps,
  MovieRatingIndicatorProps,
  CardToggleIconButtonProps,
  CopyToClipboardButtonProps,
} from "./types";

// Main card components
export { default as MovieCard } from "./MovieCard";
export { default as MovieCardContainer } from "./MovieCardContainer";
export { default as MovieCardSkeleton } from "./MovieCardSkeleton";

// Reusable sub-components
export { default as MovieRatingIndicator } from "./MovieRatingIndicator";
export { default as CardToggleIconButton } from "./CardToggleIconButton";

// Utility components
export { default as CopyToClipBoardButton } from "./CopyToClipBoardButton";

// Internal components (not exported - used only within this module)
// - MovieQuickAction (internal to MovieCard)
