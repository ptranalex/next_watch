"use client";

import { memo, useEffect, useMemo, useCallback } from "react";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import MovieBrowseLayout from "@/components/ui/layout/MovieBrowseLayout";
import { useSearchParams } from "next/navigation";
import { Heading } from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";
import { useTopMoviesByYear } from "@/services/hooks/pages/useTopMoviesByYear";

// Create a logger for this component
const logger = createLogger("TopMoviesPage");

// Top movies page props interface
export interface TopMoviesPageProps {
  /** Year parameter from the route */
  yearParam: string;
}

/**
 * TopMoviesPage component - Shows top movies for a specific year
 *
 * This is a feature-level component that contains all the business logic
 * for displaying top movies by year, handling pagination, and managing state.
 *
 * Route: /top/[year]
 * Displays movies from the specified year sorted by IMDb rating
 * Special cases:
 * - top/current-year: Uses the current year and locks it
 * - top/all-time: Shows all years, no year filter is locked
 *
 * @param props - Component props
 * @param props.yearParam - The year parameter from the route
 */
const TopMoviesPage: React.FC<TopMoviesPageProps> = memo(({ yearParam }) => {
  // Log component initialization
  logger.debug("TopMoviesPage feature component initializing", { yearParam });

  const searchParams = useSearchParams();

  // Use the hook to fetch movies and manage filters
  const {
    movies,
    totalMovies,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    loadMore,
    error,
    titleText,
  } = useTopMoviesByYear({ yearParam });

  // Memoize the load more callback to prevent unnecessary re-renders
  const handleLoadMore = useCallback(() => {
    logger.info(`Loading more top movies for year: ${yearParam}`);
    loadMore();
  }, [loadMore, yearParam]);

  // Track search params for hydration
  useEffect(() => {
    // This forces React to include searchParams in hydration
    if (searchParams) {
      // Just accessing searchParams is enough to make React track it
      logger.debugOnce("Including searchParams in hydration");
    }
  }, [searchParams]);

  // Log when movies data changes
  useEffect(() => {
    if (movies && movies.length > 0) {
      logger.info(
        `Top movies data loaded: ${movies.length} movies for year: ${yearParam}`
      );
    }
  }, [movies, yearParam]);

  // Memoize the title component
  const title = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        {titleText}
      </Heading>
    ),
    [titleText]
  );

  // Memoize the grid columns configuration
  const gridColumns = useMemo(
    () => ({
      base: 3,
      sm: 3,
      md: 4,
      lg: 6,
    }),
    []
  );

  logger.debug(`Rendering page with title: ${titleText}`);

  return (
    <MovieBrowseLayout title={title}>
      <MovieGrid
        movies={movies}
        totalMovies={totalMovies}
        fetchedMoviesCount={movies.length}
        isLoading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        hasNextPage={hasNextPage}
        onLoadMore={handleLoadMore}
        error={error as Error | null}
        columns={gridColumns}
        source="movie_listing"
      />
    </MovieBrowseLayout>
  );
});

TopMoviesPage.displayName = "TopMoviesPage";

export default TopMoviesPage;
