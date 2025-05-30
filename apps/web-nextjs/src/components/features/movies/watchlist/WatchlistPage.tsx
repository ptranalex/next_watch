"use client";

import { Heading } from "@chakra-ui/react";
import MovieBrowseLayout from "@/components/ui/layout/MovieBrowseLayout";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { useWatchlistPage } from "@/services/hooks/pages/useWatchlistPage";
import { memo, useCallback, useMemo, useEffect } from "react";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("WatchlistPage");

// Memoize components for better performance
const MemoizedMovieGrid = memo(MovieGrid);

/**
 * WatchlistPage component - Displays user's watchlist movies
 *
 * This is a feature-level component that contains all the business logic
 * for displaying watchlist movies, handling pagination, and managing state.
 *
 * Uses the shared MovieBrowseLayout for consistent UI with other pages
 */
const WatchlistPage = memo(() => {
  // Log component initialization
  logger.debug("WatchlistPage feature component initializing");

  // Memoize the title component
  const title = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        Your Watchlist
      </Heading>
    ),
    []
  );

  const {
    movies,
    totalMovies,
    fetchedMoviesCount,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    loadMore,
    error,
  } = useWatchlistPage();

  // Handle loading more movies with pagination
  const handleLoadMore = useCallback(() => {
    logger.info(`Loading more watchlist movies`);
    loadMore();
  }, [loadMore]);

  // Log when watchlist data changes
  useEffect(() => {
    if (movies) {
      logger.info(`Watchlist data loaded: ${movies.length} movies`);
    }
  }, [movies]);

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
    <MovieBrowseLayout title={title}>
      <MemoizedMovieGrid
        columns={gridColumns}
        source="watchlist"
        movies={movies}
        totalMovies={totalMovies}
        fetchedMoviesCount={fetchedMoviesCount}
        isLoading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        hasNextPage={hasNextPage}
        onLoadMore={handleLoadMore}
        error={error as Error | null}
        emptyMessage="Your watchlist is empty. Add some movies to watch later!"
      />
    </MovieBrowseLayout>
  );
});

WatchlistPage.displayName = "WatchlistPage";

export default WatchlistPage;
