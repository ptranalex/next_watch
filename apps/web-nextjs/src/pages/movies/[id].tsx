import React from "react";
import { Box, Heading, Text, Flex, Center, Spinner } from "@chakra-ui/react";
import { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import { dehydrate, QueryClient, useQuery } from "@tanstack/react-query";
import { getMovieById, Movie } from "../../services/movie-service";
import useMovieCast from "../../hooks/useMovieCast";
import useRelatedMovies from "../../hooks/useRelatedMovies";
import {
  getPosterUrl,
  getBackdropUrl,
  getProfileUrl,
} from "../../utils/image-urls";
import { fetchData } from "../../services/api-client";
import config from "../../config";

// Import modular components
import MovieHero from "../../components/movies/detail/MovieHero";
import MoviePoster from "../../components/movies/detail/MoviePoster";
import MovieDetails from "../../components/movies/detail/MovieDetails";
import MovieCast from "../../components/movies/detail/MovieCast";
import RelatedMovies from "../../components/movies/detail/RelatedMovies";

// Types
interface MovieDetailPageProps {
  id: number;
}

const MovieDetailPage: NextPage<MovieDetailPageProps> = ({ id }) => {
  // Use React Query to fetch movie details
  const {
    data: movie,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["movie", id],
    queryFn: () => getMovieById(id),
    enabled: !!id,
  });

  // Fetch movie cast
  const { data: castData, isLoading: isLoadingCast } = useMovieCast(id);

  // Fetch related movies only if the feature is enabled
  const { data: relatedMoviesData, isLoading: isLoadingRelated } =
    useRelatedMovies(id, config.features.enableRelatedMovies);

  // Show loading state if still fetching data
  if (isLoading) {
    return (
      <Center minH="50vh">
        <Spinner size="xl" color="blue.400" />
      </Center>
    );
  }

  // Show error state if query failed
  if (error || !movie) {
    return (
      <Center minH="50vh">
        <Box textAlign="center">
          <Heading as="h2" size="lg" mb={4}>
            Error Loading Movie
          </Heading>
          <Text>{(error as Error)?.message || "Movie not found"}</Text>
        </Box>
      </Center>
    );
  }

  // Get release year if available
  const releaseYear = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : null;

  // Get poster and backdrop URLs using the utilities
  const posterUrl = getPosterUrl(
    movie.poster_path || (movie as any).poster_url
  );
  const backdropUrl = getBackdropUrl(
    movie.backdrop_path || (movie as any).backdrop_url
  );

  return (
    <>
      <Head>
        <title>{movie.title} | Next Watch</title>
        <meta name="description" content={movie.overview?.substring(0, 160)} />
      </Head>

      {/* Hero section with backdrop */}
      <MovieHero
        title={movie.title}
        backdropUrl={backdropUrl}
        releaseYear={releaseYear}
      />

      <Box p={4}>
        {!backdropUrl && <Heading mb={4}>{movie.title}</Heading>}

        <Flex direction={{ base: "column", md: "row" }} gap={8} mb={8}>
          {/* Movie poster */}
          <MoviePoster title={movie.title} posterUrl={posterUrl} />

          {/* Movie details */}
          <MovieDetails
            title={movie.title}
            overview={movie.overview || ""}
            voteAverage={movie.vote_average}
            releaseYear={releaseYear}
            genres={movie.genres}
          />
        </Flex>

        {/* Cast Section */}
        {config.features.enableCast && (
          <MovieCast
            cast={castData?.cast}
            isLoading={isLoadingCast}
            profileUrlFn={getProfileUrl}
          />
        )}

        {/* Related Movies Section */}
        {config.features.enableRelatedMovies && (
          <RelatedMovies
            movies={relatedMoviesData?.movies}
            isLoading={isLoadingRelated}
          />
        )}
      </Box>
    </>
  );
};

export const getServerSideProps: GetServerSideProps<
  MovieDetailPageProps
> = async (context) => {
  const { id } = context.params || {};
  const movieId = Number(id);

  if (isNaN(movieId) || movieId <= 0) {
    return {
      notFound: true, // Returns 404 page
    };
  }

  const queryClient = new QueryClient();

  try {
    // Prefetch movie for initial render
    await queryClient.fetchQuery({
      queryKey: ["movie", movieId],
      queryFn: () => getMovieById(movieId),
    });

    // Prefetch cast only if enabled
    const prefetchPromises = [];

    if (config.features.enableCast) {
      prefetchPromises.push(
        queryClient.prefetchQuery({
          queryKey: ["movie-cast", movieId],
          queryFn: async () => {
            return fetchData(`/movies/${movieId}/cast`);
          },
        })
      );
    }

    // Prefetch related movies only if enabled
    if (config.features.enableRelatedMovies) {
      prefetchPromises.push(
        queryClient.prefetchQuery({
          queryKey: ["related-movies", movieId],
          queryFn: async () => {
            return fetchData(`/movies/${movieId}/related`);
          },
        })
      );
    }

    if (prefetchPromises.length > 0) {
      await Promise.allSettled(prefetchPromises);
    }

    return {
      props: {
        id: movieId,
        dehydratedState: dehydrate(queryClient),
      },
    };
  } catch (error) {
    console.error(`Error fetching movie with ID ${id}:`, error);
    // We still return the ID so the client can attempt to fetch
    return {
      props: {
        id: movieId,
      },
    };
  }
};

export default MovieDetailPage;
