/**
 * Movie Feature Components
 *
 * This module exports all movie-related components and types including
 * cards, details, filters, and shared movie functionality.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  // Domain types
  MovieUpdateCallback,
  MovieInteractionEndpoint,
  ToggleableMovieAttribute,
  MovieCardOrientation,
  MovieGridView,
  MovieSortOption,

  // Shared component props
  MovieFilterProps,
  MovieCardBaseProps,
  MovieGridProps,
  MovieInteractionProps,
} from "./types";

// Note: Component-specific types are now exported from their respective subdirectories:
// - MovieDetailViewProps, MovieSkeletonProps -> "./detail"
// - MovieQuickActionProps, MovieRatingIndicatorProps -> "./card"

// ============================================================================
// Re-exports from subdirectories
// ============================================================================

// Movie cards
export * from "./card";

// Movie details
export * from "./detail";

// Movie filters
export * from "./filter";
