"use client";

import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { memo, useEffect, useMemo, useCallback } from "react";
import MovieBrowseLayout from "@/components/ui/layout/MovieBrowseLayout";
import { useActorPage } from "@/services/hooks/pages/useActorPage";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("ActorPage");

// Actor page props interface
export interface ActorPageProps {
  /** Actor ID to display movies for */
  actorId: number;
}

/**
 * ActorPage component - Displays movies filtered by actor
 *
 * Uses the shared MovieBrowseLayout for consistent UI with other pages.
 * This is a feature-level component that contains all the business logic
 * for displaying an actor's movies with filtering and pagination.
 *
 * @param props - Component props
 * @param props.actorId - The ID of the actor to display movies for
 */
const ActorPage = memo(({ actorId }: ActorPageProps) => {
  // Log component initialization
  logger.debug("ActorPage initializing", { actorId });

  // Memoize actor ID validation
  const isValidActorId = useMemo(() => {
    return actorId > 0 && !isNaN(actorId);
  }, [actorId]);

  // Use the actor page hook to get all data with pagination support and filtering
  const {
    actor,
    actorName,
    movies,
    totalMovies,
    isLoading,
    isFetchingNextPage,
    error,
    hasNextPage,
    loadMore,
    // activeFilters, // TODO: Will be used when filter UI is added
    // hasActiveFilters, // TODO: Will be used when filter UI is added
  } = useActorPage(actorId);

  // Handle loading more movies with pagination
  const handleLoadMore = useCallback(() => {
    logger.info(`Loading more movies for actor: ${actorName}`);
    loadMore();
  }, [loadMore, actorName]);

  // Log the extracted actor ID
  useEffect(() => {
    if (actorId) {
      logger.info(`Rendering actor page for actor ID: ${actorId}`);
    }
  }, [actorId]);

  // Log when actor data changes
  useEffect(() => {
    if (actor) {
      logger.info(`Actor data loaded: ${actorName} (ID: ${actorId})`);
    }
  }, [actor, actorName, actorId]);

  // Memoize static UI elements to prevent unnecessary re-renders
  const loadingTitle = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        Loading Actor...
      </Heading>
    ),
    []
  );

  const invalidTitle = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        Invalid Actor
      </Heading>
    ),
    []
  );

  const actorTitle = useMemo(
    () => (
      <Heading as="h1" marginY={5}>
        {actor ? `Movies featuring ${actorName}` : "Actor"}
      </Heading>
    ),
    [actor, actorName]
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

  // Validate actor ID
  if (!isValidActorId) {
    return (
      <MovieBrowseLayout title={invalidTitle}>
        <div className="text-center py-10">
          <p>Invalid actor ID. Please select a valid actor.</p>
        </div>
      </MovieBrowseLayout>
    );
  }

  // Show loading state during initial data fetch
  if (isLoading && !actor) {
    return (
      <MovieBrowseLayout title={loadingTitle}>
        <div className="text-center py-10">
          <p>Loading actor information...</p>
        </div>
      </MovieBrowseLayout>
    );
  }

  return (
    <MovieBrowseLayout title={actorTitle}>
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
        source="by_actor"
        emptyMessage={`No movies found for ${actorName}`}
      />
    </MovieBrowseLayout>
  );
});

ActorPage.displayName = "ActorPage";

export default ActorPage;
