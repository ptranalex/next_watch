"use client";

import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { memo, useEffect, useMemo, useCallback } from "react";
import MovieBrowseLayout from "@/components/ui/layout/MovieBrowseLayout";
import { useGenrePage } from "@/services/hooks/pages/useGenrePage";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("GenrePage");

// Genre page props interface
export interface GenrePageProps {
  /** Genre ID to display movies for */
  genreId: number;
}

/**
 * GenrePage component - Displays movies filtered by genre
 *
 * Uses the shared MovieBrowseLayout for consistent UI with other pages.
 * This is a feature-level component that contains all the business logic
 * for displaying a genre's movies with filtering and pagination.
 *
 * @param props - Component props
 * @param props.genreId - The ID of the genre to display movies for
 */
const GenrePage = memo(({ genreId }: GenrePageProps) => {
  // Log component initialization
  logger.debug("GenrePage initializing", { genreId });

  // Memoize genre ID validation
  const isValidGenreId = useMemo(() => {
    return genreId > 0 && !isNaN(genreId);
  }, [genreId]);

  // Use the genre page hook to get all data with pagination support and filtering
  const {
    genre,
    genreName,
    movies,
    totalMovies,
    isLoading,
    isFetchingNextPage,
    error,
    hasNextPage,
    loadMore,
    // activeFilters, // TODO: Will be used when filter UI is added
    // hasActiveFilters, // TODO: Will be used when filter UI is added
  } = useGenrePage(genreId);

  // Handle loading more movies with pagination
  const handleLoadMore = useCallback(() => {
    logger.info(`Loading more movies for genre: ${genreName}`);
    loadMore();
  }, [loadMore, genreName]);

  // Log the extracted genre ID
  useEffect(() => {
    if (genreId) {
      logger.info(`Rendering genre page for genre ID: ${genreId}`);
    }
  }, [genreId]);

  // Log when genre data changes
  useEffect(() => {
    if (genre) {
      logger.info(`Genre data loaded: ${genreName} (ID: ${genreId})`);
    }
  }, [genre, genreName, genreId]);

  // Memoize static UI elements to prevent unnecessary re-renders
  const loadingTitle = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        Loading Genre...
      </Heading>
    ),
    []
  );

  const invalidTitle = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        Invalid Genre
      </Heading>
    ),
    []
  );

  const genreTitle = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        {genre ? `${genreName} Movies` : "Genre"}
      </Heading>
    ),
    [genre, genreName]
  );

  // Memoize the grid columns configuration
  const gridColumns = useMemo(
    () => ({
      base: 2,
      sm: 3,
      md: 4,
      lg: 6,
    }),
    []
  );

  // Validate genre ID
  if (!isValidGenreId) {
    return (
      <MovieBrowseLayout title={invalidTitle}>
        <div className="text-center py-10">
          <p>Invalid genre ID. Please select a valid genre.</p>
        </div>
      </MovieBrowseLayout>
    );
  }

  // Show loading state during initial data fetch
  if (isLoading && !genre) {
    return (
      <MovieBrowseLayout title={loadingTitle}>
        <div className="text-center py-10">
          <p>Loading genre information...</p>
        </div>
      </MovieBrowseLayout>
    );
  }

  return (
    <MovieBrowseLayout title={genreTitle}>
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
        source="by_genre"
        emptyMessage={`No movies found in ${genreName}`}
      />
    </MovieBrowseLayout>
  );
});

GenrePage.displayName = "GenrePage";

export default GenrePage;
