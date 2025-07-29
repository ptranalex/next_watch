"use client";

import React, { memo } from "react";
import MovieBrowseLayoutSkeleton from "@/components/ui/layout/MovieBrowseLayoutSkeleton";

/**
 * TopMoviesPageSkeleton - Industry standard skeleton loading UI for Top Movies pages
 *
 * Uses the shared MovieBrowseLayoutSkeleton to ensure consistency across
 * all pages that adopt the MovieBrowseLayout pattern.
 *
 * Matches the exact structure of TopMoviesPage:
 * - Header with year/title (e.g., "Top Movies 2023")
 * - Sort/filter controls
 * - MovieGrid with columns: { base: 3, sm: 3, md: 4, lg: 6 }
 */
const TopMoviesPageSkeleton = memo(() => {
  // Use the same grid columns as TopMoviesPage
  const gridColumns = {
    base: 3,
    sm: 3,
    md: 4,
    lg: 6,
  };

  return (
    <MovieBrowseLayoutSkeleton
      titleWidth="200px" // Wide enough for "Top Movies 2023", "Top Movies 2024", etc.
      columns={gridColumns}
      movieCount={12}
      showControls={true}
      showSidebar={false}
    />
  );
});

// Compact skeleton for faster loads
export const TopMoviesPageCompactSkeleton = memo(() => {
  const gridColumns = {
    base: 3,
    sm: 3,
    md: 4,
    lg: 6,
  };

  return (
    <MovieBrowseLayoutSkeleton
      titleWidth="180px"
      columns={gridColumns}
      movieCount={6}
      showControls={false}
      showSidebar={false}
    />
  );
});

// Re-export the shared MovieGrid skeleton for individual cards
export { default as TopMovieCardSkeleton } from "@/components/features/movies/card/MovieCardSkeleton";

TopMoviesPageSkeleton.displayName = "TopMoviesPageSkeleton";
TopMoviesPageCompactSkeleton.displayName = "TopMoviesPageCompactSkeleton";

export default TopMoviesPageSkeleton;
