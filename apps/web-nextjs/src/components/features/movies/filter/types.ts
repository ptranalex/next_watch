import { BaseModalProps, ComponentSize } from "../../../ui/types";

/**
 * Movie Filter Component Types
 *
 * Types specific to movie filtering functionality including filter buttons,
 * modals, sliders, and genre selection components.
 */

// ============================================================================
// Filter Component Props
// ============================================================================

/** Filter button props */
export interface FilterButtonProps {
  activeFilters?: number;
  onFilterOpen?: () => void;
  size?: ComponentSize;
  variant?: "solid" | "outline" | "ghost";
}

/** Movie filter modal props - currently same as BaseModal, room for future enhancement */
export type MovieFilterModalProps = BaseModalProps;

/** Rating slider props - single value implementation */
export interface RatingSliderProps {
  step: number;
  max: number;
  min: number;
  value?: number;
  setValue: (val: number) => void;
  icon: React.ElementType;
  isLocked?: boolean;
}

/** Genre filter props */
export interface GenreFilterProps {
  selectedGenres: string[];
  onGenreChange: (genres: string[]) => void;
  maxSelections?: number;
  layout?: "grid" | "list";
}
