import React, { useEffect } from "react";
import { SimpleGrid, Box, Text, Spinner, Center } from "@chakra-ui/react";
import { Movie } from "../../services/movie-service";
import MovieCard from "./MovieCard";
import useIntersectionObserver from "../../hooks/useIntersectionObserver";

interface MovieGridProps {
  movies: Movie[];
  isLoading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  columns?: { base: number; sm: number; md: number; lg: number; xl?: number };
}

const MovieGrid: React.FC<MovieGridProps> = ({
  movies,
  isLoading = false,
  hasMore = false,
  onLoadMore,
  columns = { base: 2, sm: 2, md: 3, lg: 4, xl: 5 },
}) => {
  // Use intersection observer for infinite scrolling
  const [loaderRef, isIntersecting] = useIntersectionObserver<HTMLDivElement>({
    rootMargin: "300px",
  });

  // Trigger load more when the loader element is visible
  useEffect(() => {
    if (isIntersecting && hasMore && onLoadMore && !isLoading) {
      console.log("Loading more movies...");
      onLoadMore();
    }
  }, [isIntersecting, hasMore, onLoadMore, isLoading]);

  // Log when the component receives new props
  useEffect(() => {
    console.log(
      `MovieGrid: ${movies.length} movies, hasMore=${hasMore}, isLoading=${isLoading}`
    );
  }, [movies.length, hasMore, isLoading]);

  if (isLoading && (!movies || movies.length === 0)) {
    return (
      <Center py={12}>
        <Spinner size="xl" color="blue.400" />
      </Center>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <Center py={12}>
        <Text>No movies found</Text>
      </Center>
    );
  }

  return (
    <Box>
      <SimpleGrid columns={columns} spacing={6} py={4} justifyItems="center">
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </SimpleGrid>

      {/* Infinite scroll loading indicator */}
      {(hasMore || isLoading) && (
        <Center py={8} ref={loaderRef}>
          {isLoading && <Spinner size="md" color="blue.400" />}
        </Center>
      )}
    </Box>
  );
};

export default MovieGrid;
