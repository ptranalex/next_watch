"use client";

import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/home/MovieGrid";
import { memo } from "react";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";
import { useParams } from "@/hooks";
import { useActor } from "@/hooks/domain/actor/useActor";

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
  // Safely unwrap params and extract actor ID
  const params = useParams(paramsPromise);
  const actorId = params?.id ? Number(params.id) : 0;

  // Use the domain hook to access actor data
  const { actor, actorName } = useActor(actorId);

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
