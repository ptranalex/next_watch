/**
 * Actor Feature Components
 *
 * This module exports all actor-related components and types.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  ActorPageProps,
  ActorDetailProps,
  ActorGalleryProps,
  ActorCardProps,
} from "./types";

// ============================================================================
// Components
// ============================================================================

export { default as ActorPage } from "./ActorPage";
export { default as ActorPageSkeleton } from "./ActorPageSkeleton";
export {
  ActorPageCompactSkeleton,
  MovieCardSkeleton,
} from "./ActorPageSkeleton";

// TODO: Export additional actor components when they are created
// export { default as ActorCard } from "./ActorCard";
// export { default as ActorDetail } from "./ActorDetail";
// export { default as ActorGallery } from "./ActorGallery";
