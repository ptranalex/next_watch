"use client";

import { Box, Heading, Spinner } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";
import MovieGrid from "@/components/home/MovieGrid";
import { memo } from "react";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";

// Export dynamic to ensure server-side rendering works correctly
export const dynamic = "force-dynamic";

// Memoize components for better performance
const MemoizedMovieGrid = memo(MovieGrid);

// Actor page props interface
interface ActorPageProps {
  params: { id: string };
}

const ActorPage = ({ params }: ActorPageProps) => {
  // Safely extract actor ID from params
  const actorId = params?.id ? Number(params.id) : null;

  const { data: movies, isLoading } = useQuery({
    queryKey: ["movies", "actor", actorId],
    queryFn: () => MovieAPI.getMovies({ actor_id: actorId || undefined }),
    staleTime: 5 * 60 * 1000, // 5 minutes caching for performance
    enabled: !!actorId, // Only run query when we have a valid actorId
  });

  if (!actorId) {
    return (
      <MovieBrowseLayout title={<Heading>Actor Not Found</Heading>}>
        <Box p={5} textAlign="center">
          Invalid actor ID
        </Box>
      </MovieBrowseLayout>
    );
  }

  if (isLoading) {
    return (
      <MovieBrowseLayout title={<Spinner size="lg" my={10} />}>
        <Box textAlign="center" py={10}>
          <Spinner size="xl" />
          <Box mt={4}>Loading actor&apos;s movies...</Box>
        </Box>
      </MovieBrowseLayout>
    );
  }

  if (!movies || movies.movies.length === 0) {
    return (
      <MovieBrowseLayout title={<Heading>Actor</Heading>}>
        <Box p={5} textAlign="center">
          No movies found for this actor
        </Box>
      </MovieBrowseLayout>
    );
  }

  // Get actor name from the first movie's cast
  const actorName =
    movies.movies[0].actors?.find((a) => a.actor_id === actorId)?.name ||
    "Actor";

  return (
    <MovieBrowseLayout
      title={
        <Heading as="h1" marginY={5}>
          Movies featuring {actorName}
        </Heading>
      }
    >
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="movie_listing"
        actor_id={actorId}
      />
    </MovieBrowseLayout>
  );
};

export default ActorPage;
