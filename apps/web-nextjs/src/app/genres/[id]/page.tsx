"use client";

import { Heading, Skeleton, SkeletonText, Box, Grid } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";
import MovieGrid from "@/components/home/MovieGrid";
import { useParams } from "next/navigation";
import { memo, useCallback } from "react";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";

// Memoize components to prevent unnecessary re-renders
const MemoizedMovieGrid = memo(MovieGrid);

const GenrePage = () => {
  const params = useParams();
  const genreId = Number(params.id);

  const { data: movies, isLoading } = useQuery({
    queryKey: ["movies", "genre", genreId],
    queryFn: () => MovieAPI.getMovies({ genre_id: genreId }),
    staleTime: 5 * 60 * 1000, // Increase to 5 minutes for better caching
  });

  // Get the genre name, with fallback for loading state
  const genreName = isLoading
    ? null // We'll handle this with a skeleton
    : movies?.movies[0]?.genres?.find((g) => g.id === genreId)?.name ||
      "Movies";

  // Memoize callback functions
  const renderMovieGrid = useCallback(() => {
    if (isLoading) {
      return (
        <Box>
          <SkeletonText mt="4" noOfLines={1} spacing="4" skeletonHeight="2" />
          <Grid
            templateColumns={{
              base: "repeat(3, 1fr)",
              sm: "repeat(3, 1fr)",
              md: "repeat(4, 1fr)",
              lg: "repeat(6, 1fr)",
            }}
            gap={3}
            mt={6}
          >
            {Array.from({ length: 12 }).map((_, i) => (
              <Skeleton key={i} height="300px" borderRadius="md" />
            ))}
          </Grid>
        </Box>
      );
    }

    if (movies && movies.movies.length > 0) {
      return (
        <MemoizedMovieGrid
          columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
          source="movie_listing"
          genre_id={genreId}
        />
      );
    }

    return <Box>No movies found for this genre</Box>;
  }, [isLoading, movies, genreId]);

  // Title component with loading state
  const genreTitle = isLoading ? (
    <Box marginY={5}>
      <Skeleton height="40px" width="200px" />
    </Box>
  ) : (
    <Heading as="h1" marginY={5}>
      {genreName}
    </Heading>
  );

  return (
    <MovieBrowseLayout title={genreTitle}>
      {renderMovieGrid()}
    </MovieBrowseLayout>
  );
};

export default GenrePage;
