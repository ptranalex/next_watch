"use client";

import React, { memo } from "react";
import MovieBrowseLayoutSkeleton from "@/components/ui/layout/MovieBrowseLayoutSkeleton";

/**
 * ActorPageSkeleton - Industry standard skeleton loading UI for Actor pages
 *
 * Uses the shared MovieBrowseLayoutSkeleton to ensure consistency across
 * all pages that adopt the MovieBrowseLayout pattern.
 *
 * Matches the exact structure of ActorPage:
 * - Header with actor title (e.g., "Movies featuring Tom Hanks")
 * - Sort/filter controls
 * - MovieGrid with columns: { base: 3, sm: 3, md: 4, lg: 6 }
 */
const ActorPageSkeleton = memo(() => {
  // Use the same grid columns as ActorPage
  const gridColumns = {
    base: 3,
    sm: 3,
    md: 4,
    lg: 6,
  };

  return (
    <MovieBrowseLayoutSkeleton
      titleWidth="350px" // Wide enough for "Movies featuring [Actor Name]"
      columns={gridColumns}
      movieCount={12}
      showControls={true}
      showSidebar={false}
    />
  );
});

// Compact skeleton for faster loads
export const ActorPageCompactSkeleton = memo(() => {
  const gridColumns = {
    base: 3,
    sm: 3,
    md: 4,
    lg: 6,
  };

  return (
    <MovieBrowseLayoutSkeleton
      titleWidth="300px"
      columns={gridColumns}
      movieCount={6}
      showControls={false}
      showSidebar={false}
    />
  );
});

// Re-export the shared MovieGrid skeleton for individual cards
export { default as MovieCardSkeleton } from "@/components/features/movies/card/MovieCardSkeleton";

ActorPageSkeleton.displayName = "ActorPageSkeleton";
ActorPageCompactSkeleton.displayName = "ActorPageCompactSkeleton";

export default ActorPageSkeleton;
