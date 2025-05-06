"use client";

import { useMediaQuery } from "@chakra-ui/react";
import React, { useCallback } from "react";
import { useAuth, useMovie, useParams } from "@/hooks";
import { Movie } from "@/domain/entities";
import MovieDetailView from "@/components/movieDetails/MovieDetailView";
import MovieLayout from "@/components/layout/MovieLayout";
import MovieSkeleton from "@/components/movieDetails/MovieSkeleton";
import MovieErrorState from "@/components/movieDetails/MovieErrorState";
import MovieNotFoundState from "@/components/movieDetails/MovieNotFoundState";
import MovieInitialLoading from "@/components/movieDetails/MovieInitialLoading";

// Handle movie id parameter in a way compatible with Next.js 15
interface MovieDetailPageProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * Movie detail page component
 * Displays a movie's details, with states for loading, error, and not found
 */
const MovieDetailPage = ({ params }: MovieDetailPageProps) => {
  // Use our custom hook to handle params unwrapping
  const { id } = useParams(params);
  const movieId = id ? Number(id) : null;

  const { isAuthenticated } = useAuth();
  const [isSmallerScreen] = useMediaQuery("(max-width: 600px)");

  const {
    movie,
    isLoading,
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist,
  } = useMovie(movieId || 0);

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

  // Render different states based on loading/error conditions
  if (movieId === null) {
    return (
      <MovieLayout>
        <MovieInitialLoading />
      </MovieLayout>
    );
  }

  if (isLoading) {
    return (
      <MovieLayout>
        <MovieSkeleton isSmallerScreen={isSmallerScreen} />
      </MovieLayout>
    );
  }

  if (error) {
    return (
      <MovieLayout>
        <MovieErrorState error={error as string} />
      </MovieLayout>
    );
  }

  if (!movie) {
    return (
      <MovieLayout>
        <MovieNotFoundState />
      </MovieLayout>
    );
  }

  return (
    <MovieLayout>
      <MovieDetailView
        movie={movie}
        isSignedIn={isAuthenticated}
        isSmallerScreen={isSmallerScreen}
        onUpdateMovie={updateMovie}
      />
    </MovieLayout>
  );
};

export default MovieDetailPage;
