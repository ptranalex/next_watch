"use client";

import { memo, useEffect } from "react";
import MovieGrid from "@/components/home/MovieGrid";
import MovieHeading from "@/components/home/MovieHeading";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";
import { useParams, useSearchParams } from "next/navigation";
import { useFilterParams } from "@/hooks/useUrlParams";

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

// Memoize components
const MemoizedMovieGrid = memo(MovieGrid);

/**
 * TopMoviesByYearPage component - Shows top movies for a specific year
 *
 * Route: /top/[year]
 * Displays movies from the specified year sorted by IMDb rating
 */
const TopMoviesByYearPage: React.FC = () => {
  const params = useParams<{ year: string }>();
  const year = params?.year
    ? parseInt(params.year, 10)
    : new Date().getFullYear();
  const searchParams = useSearchParams();

  const { setFilters } = useFilterParams({
    defaults: {
      sort: "imdb_rating",
      order: "desc",
    },
  });

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

  const title = `Top Movies of ${year}`;

  return (
    <MovieBrowseLayout title={<MovieHeading title={title} />}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="movie_listing"
        // MovieGrid already handles year from URL path (/top/[year])
        // and will use the sort parameters we've set in the URL
      />
    </MovieBrowseLayout>
  );
};

export default TopMoviesByYearPage;
