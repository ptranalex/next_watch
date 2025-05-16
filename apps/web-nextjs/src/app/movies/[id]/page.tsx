"use client";

import { useMediaQuery } from "@chakra-ui/react";
import React, { useCallback } from "react";
import { useAuth, useMovie, useParams } from "@/hooks";
import { Movie } from "@/domain/entities";
import MovieDetailView from "@/components/movieDetails/MovieDetailView";

// Force dynamic to ensure latest movie data is fetched
export const dynamic = "force-dynamic";

interface MovieDetailPageProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * Movie detail page component
 * Displays a movie's details, with states for error and not found
 */
const MovieDetailPage = ({ params }: MovieDetailPageProps) => {
  // Use our custom hook to handle params unwrapping
  const resolvedParams = useParams(params);
  const movieId = resolvedParams?.id ? Number(resolvedParams.id) : 0;

  const { isAuthenticated } = useAuth();
  const [isSmallerScreen] = useMediaQuery("(max-width: 600px)");

  const {
    movie,
    isLoading,
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist,
  } = useMovie(movieId);

  // Function to update movie from UI interactions (memoized)
  const updateMovie = useCallback(
    (updatedMovie: Movie) => {
      if (!movie) return;

      if (updatedMovie.watched !== movie.watched) {
        toggleWatched();
      } else if (updatedMovie.liked !== movie.liked) {
        toggleLiked();
      } else if (updatedMovie.in_watchlist !== movie.in_watchlist) {
        toggleWatchlist();
      }
    },
    [movie, toggleWatched, toggleLiked, toggleWatchlist]
  );

  // Render movie details (loading state handled by loading.tsx)
  return (
    <>
      {movie && (
        <MovieDetailView
          movie={movie}
          isSignedIn={isAuthenticated}
          isSmallerScreen={isSmallerScreen}
          onUpdateMovie={updateMovie}
        />
      )}
    </>
  );
};

export default MovieDetailPage;
