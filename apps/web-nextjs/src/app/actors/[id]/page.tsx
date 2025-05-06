"use client";

import { Box, Heading, Spinner } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";
import MovieGrid from "@/components/home/MovieGrid";
import { useParams } from "next/navigation";
import { memo } from "react";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";

// Memoize components for better performance
const MemoizedMovieGrid = memo(MovieGrid);

const ActorPage = () => {
  const params = useParams();
  const actorId = Number(params.id);

  const { data: movies, isLoading } = useQuery({
    queryKey: ["movies", "actor", actorId],
    queryFn: () => MovieAPI.getMovies({ actor_id: actorId }),
    staleTime: 5 * 60 * 1000, // 5 minutes caching for performance
  });

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
