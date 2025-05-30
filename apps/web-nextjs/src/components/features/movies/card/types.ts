import {
  MovieUpdateCallback,
  MovieInteractionEndpoint,
  ToggleableMovieAttribute,
  MovieCardOrientation,
  MovieCardBaseProps,
  MovieInteractionProps,
} from "../types";
import { ComponentSize } from "../../../ui/types";
import { Movie } from "@/domain/entities";

/**
 * Movie Card Component Types
 *
 * Specific types for movie card components, extending shared feature types.
 */

// Re-export shared types for convenience
export type {
  MovieUpdateCallback,
  MovieInteractionEndpoint,
  ToggleableMovieAttribute,
  MovieCardOrientation,
  ComponentSize,
  MovieCardBaseProps,
  MovieInteractionProps,
};

// ============================================================================
// Card-Specific Component Props
// ============================================================================

/** Movie card component props */
export interface MovieCardProps {
  movie: Movie;
  onMovieUpdate: MovieUpdateCallback;
}

/** Movie card container props */
export interface MovieCardContainerProps {
  children: React.ReactNode;
}

/** Movie rating indicator props for cards */
export interface MovieRatingIndicatorProps {
  rating?: number | null;
  position?: {
    top?: string | number;
    left?: string | number;
    bottom?: string | number;
    right?: string | number;
  };
  iconSize?: number | string;
  zIndex?: number;
}

/** Card toggle icon button props */
export interface CardToggleIconButtonProps {
  movie: Movie;
  attribute: ToggleableMovieAttribute;
  onToggle: (variables?: unknown) => Promise<void>;
  icon: React.ReactElement;
  label: string;
  size?: ComponentSize;
  isEnabled: boolean;
  isLoading?: boolean;
}

/** Copy to clipboard button props for cards */
export interface CopyToClipboardButtonProps {
  textToCopy: string;
  label: string;
  size?: ComponentSize;
}

/** Movie quick action props for cards */
export interface MovieQuickActionProps {
  movie: Movie;
  onMovieUpdate: MovieUpdateCallback;
  size?: ComponentSize;
  orientation?: MovieCardOrientation;
  isHovered?: boolean;
}
