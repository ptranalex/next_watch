import { Movie } from "@/domain/entities";
import { ComponentSize } from "@/components/ui/types";
import { AsyncStateProps } from "@/components/ui/molecules/types";
import { BaseToggleProps } from "@/components/ui/atoms/types";

/**
 * Movie Feature Types
 *
 * Types specific to movie components including cards, grids, interactions,
 * and movie-related UI components.
 */

// ============================================================================
// Movie Domain Types
// ============================================================================

/** Movie update callback - used across movie components */
export type MovieUpdateCallback = (updatedMovie: Movie) => void;

/** Movie interaction endpoints for API calls */
export type MovieInteractionEndpoint = "watched" | "liked" | "in_watchlist";

/** Movie toggleable attributes */
export type ToggleableMovieAttribute = "watched" | "liked" | "in_watchlist";

/** Movie card orientation */
export type MovieCardOrientation = "vertical" | "horizontal";

/** Movie grid view types */
export type MovieGridView = "grid" | "list" | "compact";

/** Movie sorting options */
export type MovieSortOption =
  | "title_asc"
  | "title_desc"
  | "rating_asc"
  | "rating_desc"
  | "release_date_asc"
  | "release_date_desc"
  | "added_date_asc"
  | "added_date_desc";

// ============================================================================
// Movie Component Props (Truly Shared Across Features)
// ============================================================================

/** Movie filter props - used across filtering components */
export interface MovieFilterProps {
  genres?: string[];
  ratings?: [number, number];
  releaseYears?: [number, number];
  sortBy?: MovieSortOption;
  viewType?: MovieGridView;
}

/** Movie card base props - foundation for all card types */
export interface MovieCardBaseProps {
  movie: Movie;
  onMovieUpdate?: MovieUpdateCallback;
  size?: ComponentSize;
  orientation?: MovieCardOrientation;
  showQuickActions?: boolean;
  isSelected?: boolean;
}

/** Movie grid props - used across different grid implementations */
export interface MovieGridProps extends AsyncStateProps {
  movies: Movie[];
  onMovieUpdate?: MovieUpdateCallback;
  view?: MovieGridView;
  columns?: number;
  gap?: string | number;
  onLoadMore?: () => void;
}

/** Movie interaction props for toggle buttons - shared across card and detail */
export interface MovieInteractionProps extends BaseToggleProps {
  movie: Movie;
  endpoint: MovieInteractionEndpoint;
  onMovieUpdate?: MovieUpdateCallback;
}

// =============================================================================
// Component-Specific Types (Moved to Local Files)
// =============================================================================
//
// The following interfaces were too specific and have been moved to their
// respective component directories for better maintainability:
//
// - MovieDetailViewProps -> movies/detail/types.ts
// - MovieQuickActionProps -> movies/card/types.ts or movies/detail/types.ts
// - MovieRatingIndicatorProps -> movies/card/types.ts (card-specific version)
// - MovieSkeletonProps -> movies/detail/types.ts (detail-specific version)
//
// This reduces centralization and keeps types closer to their usage.
