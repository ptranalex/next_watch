"use client";

import { memo, useEffect } from "react";
import MovieGrid from "@/components/home/MovieGrid";
import MovieHeading from "@/components/home/MovieHeading";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";
import { useFilterParams } from "@/hooks/useUrlParams";
import { useSearchParams } from "next/navigation";

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

// Memoize components
const MemoizedMovieGrid = memo(MovieGrid);

/**
 * AllTimeTopMoviesPage component - Shows all-time top movies
 *
 * Route: /top/all
 * Displays top-rated movies of all time sorted by IMDb rating
 */
const AllTimeTopMoviesPage: React.FC = () => {
  const { setFilters } = useFilterParams({
    defaults: {
      sort: "imdb_rating",
      order: "desc",
    },
  });
  const searchParams = useSearchParams();

  // Set the URL parameters for sorting when the component mounts
  useEffect(() => {
    setFilters({ sort: "imdb_rating", order: "desc" });
  }, [setFilters]);

  // Track search params for hydration
  useEffect(() => {
    // This forces React to include searchParams in hydration
    if (searchParams) {
      // Just accessing searchParams is enough to make React track it
    }
  }, [searchParams]);

  const title = "All-Time Top Movies";

  return (
    <MovieBrowseLayout title={<MovieHeading title={title} />}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="movie_listing"
        // This page shows all movies (no year filter) sorted by IMDb rating
      />
    </MovieBrowseLayout>
  );
};

export default AllTimeTopMoviesPage;
