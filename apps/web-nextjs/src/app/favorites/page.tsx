"use client";

import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";
import MovieGrid from "@/components/home/MovieGrid";
import PageHeading from "@/components/common/PageHeading";
import { memo } from "react";

// Memoize components for better performance
const MemoizedMovieGrid = memo(MovieGrid);

/**
 * FavoritesPage component - Shows the user's favorite movies
 *
 * Uses the shared MovieBrowseLayout for consistent UI with other pages
 * MovieGrid cards handle prefetching on hover automatically
 */
export default function FavoritesPage() {
  const title = <PageHeading>Your Favorites</PageHeading>;

  return (
    <MovieBrowseLayout title={title}>
      <MemoizedMovieGrid
        columns={{ base: 2, sm: 3, md: 4, lg: 6 }}
        source="favorites"
      />
    </MovieBrowseLayout>
  );
}
