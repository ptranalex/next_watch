/**
 * Genre Feature Components
 *
 * This module exports all genre-related components and types.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  GenrePageProps,
  GenreDetailProps,
  GenreGalleryProps,
  GenreCardProps,
} from "./types";

// ============================================================================
// Components
// ============================================================================

export { default as GenrePage } from "./GenrePage";
export { default as GenrePageSkeleton } from "./GenrePageSkeleton";
export {
  GenrePageCompactSkeleton,
  MovieCardSkeleton,
  ShimmerSkeleton,
} from "./GenrePageSkeleton";

// TODO: Export additional genre components when they are created
// export { default as GenreCard } from "./GenreCard";
// export { default as GenreDetail } from "./GenreDetail";
// export { default as GenreGallery } from "./GenreGallery";
