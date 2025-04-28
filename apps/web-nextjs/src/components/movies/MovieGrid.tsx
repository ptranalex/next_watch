"use client";

import { SimpleGrid, Box, Text, Center, Button } from "@chakra-ui/react";
import MovieCard from "./MovieCard";
import MovieCardSkeleton from "./MovieCardSkeleton";

interface Movie {
  id: string;
  title: string;
  poster_path: string;
  vote_average: number;
  release_date: string;
  genres?: string[];
}

interface MovieGridProps {
  movies: Movie[];
  isLoading?: boolean;
  error?: Error | null;
  onFavoriteToggle?: (movieId: string) => void;
  onWatchlistToggle?: (movieId: string) => void;
  onWatchedToggle?: (movieId: string) => void;
  favorites?: Set<string>;
  watchlist?: Set<string>;
  watched?: Set<string>;
  onLoadMore?: () => void;
  hasMoreMovies?: boolean;
  isLoadingMore?: boolean;
  skeletonCount?: number;
}

export default function MovieGrid({
  movies,
  isLoading = false,
  error = null,
  onFavoriteToggle,
  onWatchlistToggle,
  onWatchedToggle,
  favorites = new Set(),
  watchlist = new Set(),
  watched = new Set(),
  onLoadMore,
  hasMoreMovies = false,
  isLoadingMore = false,
  skeletonCount = 12,
}: MovieGridProps) {
  if (error) {
    return (
      <Center py={10}>
        <Text color="red.500">Error loading movies: {error.message}</Text>
      </Center>
    );
  }

  if (isLoading) {
    return (
      <SimpleGrid columns={{ base: 2, md: 3, lg: 4, xl: 6 }} spacing={4} my={4}>
        {Array(skeletonCount)
          .fill(0)
          .map((_, index) => (
            <MovieCardSkeleton key={index} />
          ))}
      </SimpleGrid>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <Center py={10}>
        <Text>No movies found</Text>
      </Center>
    );
  }

  return (
    <Box>
      <SimpleGrid columns={{ base: 2, md: 3, lg: 4, xl: 6 }} spacing={4} my={4}>
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onFavoriteToggle={onFavoriteToggle}
            onWatchlistToggle={onWatchlistToggle}
            onWatchedToggle={onWatchedToggle}
            isFavorite={favorites.has(movie.id)}
            isWatchlist={watchlist.has(movie.id)}
            isWatched={watched.has(movie.id)}
          />
        ))}
      </SimpleGrid>

      {onLoadMore && hasMoreMovies && (
        <Center py={8}>
          <Button
            onClick={onLoadMore}
            isLoading={isLoadingMore}
            loadingText="Loading more"
            colorScheme="blue"
            variant="outline"
          >
            Load More
          </Button>
        </Center>
      )}
    </Box>
  );
}
