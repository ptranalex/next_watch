import React from "react";
import {
  Box,
  Heading,
  Text,
  Image,
  Flex,
  Badge,
  VStack,
  HStack,
  Spinner,
  Center,
} from "@chakra-ui/react";
import { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { dehydrate, QueryClient, useQuery } from "@tanstack/react-query";
import { getMovieById, Movie } from "../../services/movie-service";

// Types
interface MovieDetail {
  id: number;
  title: string;
  overview: string;
  poster_path?: string;
  backdrop_path?: string;
  vote_average?: number;
  release_date?: string;
  genres?: { id: number; name: string }[];
}

interface MovieDetailPageProps {
  id: number;
}

const MovieDetailPage: NextPage<MovieDetailPageProps> = ({ id }) => {
  const router = useRouter();

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

  return (
    <>
      <Head>
        <title>{movie.title} | Next Watch</title>
        <meta name="description" content={movie.overview?.substring(0, 160)} />
      </Head>

      <Box p={4}>
        <Heading mb={4}>{movie.title}</Heading>
        {movie.release_date && (
          <Text mb={4} color="gray.500">
            Released: {new Date(movie.release_date).getFullYear()}
          </Text>
        )}

        <Flex direction={{ base: "column", md: "row" }} gap={8} mb={8}>
          {movie.poster_path && (
            <Box flexShrink={0}>
              <Image
                src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                alt={movie.title}
                borderRadius="md"
                width={300}
                height={450}
                objectFit="cover"
                fallbackSrc="/placeholder-poster.png"
              />
            </Box>
          )}

          <VStack align="start" spacing={4}>
            {movie.vote_average !== undefined && (
              <Badge
                colorScheme={movie.vote_average > 7 ? "green" : "yellow"}
                px={2}
                py={1}
              >
                Rating: {movie.vote_average.toFixed(1)}/10
              </Badge>
            )}

            {movie.genres && movie.genres.length > 0 && (
              <HStack spacing={2} wrap="wrap">
                {movie.genres.map((genre) => (
                  <Badge key={genre.id} colorScheme="blue">
                    {genre.name}
                  </Badge>
                ))}
              </HStack>
            )}

            <Text>{movie.overview}</Text>
          </VStack>
        </Flex>
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
