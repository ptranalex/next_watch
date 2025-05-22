"use client";

import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { memo, useEffect } from "react";
import MovieBrowseLayout from "@/components/ui/templates/MovieBrowseLayout";
import { useParams } from "@/hooks";
import { useActor } from "@/hooks/domain/actor/useActor";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("ActorPage");

// Memoize components for better performance
const MemoizedMovieGrid = memo(MovieGrid);

// Actor page props interface
interface ActorPageProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * ActorPage component - Displays movies filtered by actor
 *
 * Uses the shared MovieBrowseLayout for consistent UI with other pages
 */
const ActorPage = ({ params: paramsPromise }: ActorPageProps) => {
  // Log component initialization
  logger.debug("ActorPage initializing");

  // Safely unwrap params and extract actor ID
  const params = useParams(paramsPromise);
  const actorId = params?.id ? Number(params.id) : 0;

  // Log the extracted actor ID
  useEffect(() => {
    logger.info(`Rendering actor page for actor ID: ${actorId}`);
  }, [actorId]);

  // Use the domain hook to access actor data
  const { actor, actorName } = useActor(actorId);

  // Log when actor data changes
  useEffect(() => {
    if (actor) {
      logger.info(`Actor data loaded: ${actorName} (ID: ${actorId})`);
    }
  }, [actor, actorName, actorId]);

  const actorTitle = (
    <Heading as="h1" marginY={5}>
      {actor ? `Movies featuring ${actorName}` : "Actor"}
    </Heading>
  );

  return (
    <MovieBrowseLayout title={actorTitle}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="movie_listing"
        actor_id={actorId}
      />
    </MovieBrowseLayout>
  );
};

export default ActorPage;
