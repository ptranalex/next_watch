"use client";

import React, { memo } from "react";
import MovieBrowseLayoutSkeleton from "@/components/ui/layout/MovieBrowseLayoutSkeleton";

/**
 * GenrePageSkeleton - Industry standard skeleton loading UI for Genre pages
 *
 * Uses the shared MovieBrowseLayoutSkeleton to ensure consistency across
 * all pages that adopt the MovieBrowseLayout pattern.
 *
 * Matches the exact structure of GenrePage:
 * - Header with genre title (e.g., "Action Movies")
 * - Sort/filter controls
 * - MovieGrid with columns: { base: 2, sm: 3, md: 4, lg: 6 }
 */
const GenrePageSkeleton = memo(() => {
  // Use the same grid columns as GenrePage
  const gridColumns = {
    base: 2,
    sm: 3,
    md: 4,
    lg: 6,
  };

  return (
    <MovieBrowseLayoutSkeleton
      titleWidth="250px" // Wide enough for "Action Movies", "Science Fiction Movies", etc.
      columns={gridColumns}
      movieCount={12}
      showControls={true}
      showSidebar={false}
    />
  );
});

// Compact skeleton for faster loads
export const GenrePageCompactSkeleton = memo(() => {
  const gridColumns = {
    base: 2,
    sm: 3,
    md: 4,
    lg: 6,
  };

  return (
    <MovieBrowseLayoutSkeleton
      titleWidth="200px"
      columns={gridColumns}
      movieCount={6}
      showControls={false}
      showSidebar={false}
    />
  );
});

// Re-export the shared MovieGrid skeleton for individual cards
export { default as MovieCardSkeleton } from "@/components/features/movies/card/MovieCardSkeleton";

// Legacy exports for backward compatibility
export const ShimmerSkeleton = memo(() => null);
ShimmerSkeleton.displayName = "ShimmerSkeleton";

GenrePageSkeleton.displayName = "GenrePageSkeleton";
GenrePageCompactSkeleton.displayName = "GenrePageCompactSkeleton";

export default GenrePageSkeleton;
