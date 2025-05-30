/**
 * Movie Detail Components
 *
 * This module exports all components related to movie detail functionality,
 * including main views, reusable sub-components, and utility components.
 */

// Main detail view components
export { default as MovieDetailPage } from "./MovieDetailPage";
export { default as DesktopMovieDetailView } from "./DesktopMovieDetailView";

// Reusable sub-components
export { default as MovieAttributes } from "./MovieAttributes";
export { default as CriticScore } from "./CriticScore";
export { default as ActorsGallery } from "./ActorsGallery";
export { default as TrailerCard } from "./TrailerCard";
export { default as RatingGroup } from "./RatingGroup";
export { default as MovieQuickAction } from "./MovieQuickAction";

// Loading and state components
export { default as MovieSkeleton } from "./MovieSkeleton";
export { default as MovieErrorState } from "./MovieErrorState";
export { default as MovieNotFoundState } from "./MovieNotFoundState";

// Types
export * from "./types";

// Internal components (not exported - used only within this module)
// - MovieQuickAction (internal to detail views)
// - MovieInitialLoading (internal loading state)
