"use client";

import { Box, Heading, Alert, AlertIcon, Spinner } from "@chakra-ui/react";
import useRelatedMovies from "@/src/hooks/useRelatedMovies";
import MovieGrid from "../MovieGrid";
import { useState } from "react";
import config from "@/src/config";

// Match the Movie type expected by MovieGrid
interface Movie {
  id: string;
  title: string;
  poster_path: string;
  vote_average: number;
  release_date: string;
  genres?: string[];
}

interface RelatedMoviesProps {
  movieId: string;
  title?: string;
}

export default function RelatedMovies({
  movieId,
  title = "Related Movies",
}: RelatedMoviesProps) {
  const [isEnabled] = useState(() => !!config.features.enableRelatedMovies);

  const { data, isLoading, error } = useRelatedMovies(movieId, isEnabled);

  // If feature is disabled, don't render anything
  if (!isEnabled) {
    return null;
  }

  // Loading state
  if (isLoading) {
    return (
      <Box textAlign="center" py={6}>
        <Spinner size="lg" />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert status="error" my={4}>
        <AlertIcon />
        Error loading related movies:{" "}
        {error instanceof Error ? error.message : "Unknown error"}
      </Alert>
    );
  }

  // Empty state
  if (!data || !data.movies || data.movies.length === 0) {
    return (
      <Box my={6}>
        <Heading as="h3" size="md" mb={4}>
          {title}
        </Heading>
        <Alert status="info">
          <AlertIcon />
          No related movies found.
        </Alert>
      </Box>
    );
  }

  // Format the movie data for MovieGrid component with proper type handling
  const formattedMovies: Movie[] = data.movies.map((movie) => ({
    id: movie.id.toString(),
    title: movie.title,
    // Ensure poster_path is always a string with fallback
    poster_path: movie.poster_path || "/placeholder-poster.jpg",
    vote_average: movie.vote_average || 0,
    release_date: movie.release_date || "",
    genres: movie.genres ? movie.genres.map((g) => g.name) : [],
  }));

  return (
    <Box my={6}>
      <Heading as="h3" size="md" mb={4}>
        {title}
      </Heading>
      <MovieGrid
        movies={formattedMovies}
        isLoading={false}
        hasMoreMovies={false}
        onLoadMore={() => {}}
      />
    </Box>
  );
}
