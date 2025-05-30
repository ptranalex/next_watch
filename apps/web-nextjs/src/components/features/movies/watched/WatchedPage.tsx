"use client";

import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { memo, useEffect, useMemo, useCallback } from "react";
import MovieBrowseLayout from "@/components/ui/layout/MovieBrowseLayout";
import { useWatchedPage } from "@/services/hooks/pages/useWatchedPage";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("WatchedPage");

/**
 * WatchedPage component - Displays user's watched movies
 *
 * This is a feature-level component that contains all the business logic
 * for displaying watched movies, handling pagination, and managing state.
 *
 * Uses the shared MovieBrowseLayout for consistent UI with other pages
 */
const WatchedPage = memo(() => {
  // Log component initialization
  logger.debug("WatchedPage feature component initializing");

  // Use the watched page hook to get all data with pagination support and filtering
  const {
    movies,
    totalMovies,
    isLoading,
    isFetchingNextPage,
    error,
    hasNextPage,
    loadMore,
    // activeFilters, // TODO: Will be used when filter UI is added
    // hasActiveFilters, // TODO: Will be used when filter UI is added
  } = useWatchedPage();

  // Handle loading more movies with pagination
  const handleLoadMore = useCallback(() => {
    logger.info(`Loading more watched movies`);
    loadMore();
  }, [loadMore]);

  // Log when watched data changes
  useEffect(() => {
    if (movies) {
      logger.info(`Watched data loaded: ${movies.length} movies`);
    }
  }, [movies]);

  // Memoize static UI elements to prevent unnecessary re-renders
  const pageTitle = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        Watched Movies
      </Heading>
    ),
    []
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

  return (
    <MovieBrowseLayout title={pageTitle}>
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
        source="watched"
        emptyMessage="No watched movies found. Start watching some movies to see them here!"
      />
    </MovieBrowseLayout>
  );
});

WatchedPage.displayName = "WatchedPage";

export default WatchedPage;
