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
  Grid,
  GridItem,
  Divider,
  Avatar,
  SimpleGrid,
  Button,
  Icon,
} from "@chakra-ui/react";
import { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { dehydrate, QueryClient, useQuery } from "@tanstack/react-query";
import { getMovieById, Movie } from "../../services/movie-service";
import useMovieCast from "../../hooks/useMovieCast";
import useRelatedMovies from "../../hooks/useRelatedMovies";
import { StarIcon, TimeIcon, CalendarIcon } from "@chakra-ui/icons";
import { BiMovie } from "react-icons/bi";
import Link from "next/link";
import MovieCard from "../../components/movies/MovieCard";

// Types
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

  // Fetch movie cast
  const { data: castData, isLoading: isLoadingCast } = useMovieCast(id);

  // Fetch related movies
  const { data: relatedMoviesData, isLoading: isLoadingRelated } =
    useRelatedMovies(id);

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

  return (
    <>
      <Head>
        <title>{movie.title} | Next Watch</title>
        <meta name="description" content={movie.overview?.substring(0, 160)} />
      </Head>

      {/* Hero section with backdrop */}
      {movie.backdrop_path && (
        <Box position="relative" height={{ base: "200px", md: "400px" }} mb={6}>
          <Box
            position="absolute"
            top={0}
            left={0}
            right={0}
            bottom={0}
            backgroundImage={`url(https://image.tmdb.org/t/p/original${movie.backdrop_path})`}
            backgroundSize="cover"
            backgroundPosition="center"
            _after={{
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              bg: "rgba(0,0,0,0.6)",
            }}
          />
          <Box
            position="absolute"
            bottom={0}
            left={0}
            right={0}
            p={6}
            bg="linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0))"
          >
            <Heading color="white">{movie.title}</Heading>
            {releaseYear && (
              <HStack spacing={2} color="gray.300" mt={2}>
                <Icon as={CalendarIcon} />
                <Text>{releaseYear}</Text>
              </HStack>
            )}
          </Box>
        </Box>
      )}

      <Box p={4}>
        {!movie.backdrop_path && <Heading mb={4}>{movie.title}</Heading>}

        <Flex direction={{ base: "column", md: "row" }} gap={8} mb={8}>
          {/* Movie poster */}
          <Box flexShrink={0}>
            <Image
              src={
                movie.poster_path
                  ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
                  : "/placeholder-poster.png"
              }
              alt={movie.title}
              borderRadius="md"
              width={300}
              height={450}
              objectFit="cover"
              fallbackSrc="/placeholder-poster.png"
            />
          </Box>

          <VStack align="start" spacing={4} width="100%">
            {/* Movie metadata */}
            <Flex wrap="wrap" gap={3} width="100%" justify="flex-start">
              {movie.vote_average !== undefined && (
                <Badge
                  colorScheme={movie.vote_average > 7 ? "green" : "yellow"}
                  px={2}
                  py={1}
                  display="flex"
                  alignItems="center"
                >
                  <StarIcon mr={1} boxSize={3} />
                  {movie.vote_average.toFixed(1)}/10
                </Badge>
              )}

              {releaseYear && (
                <Badge
                  px={2}
                  py={1}
                  colorScheme="blue"
                  display="flex"
                  alignItems="center"
                >
                  <CalendarIcon mr={1} boxSize={3} />
                  {releaseYear}
                </Badge>
              )}
            </Flex>

            {/* Genres */}
            {movie.genres && movie.genres.length > 0 && (
              <HStack spacing={2} wrap="wrap">
                {movie.genres.map((genre) => (
                  <Link
                    href={`/genre/${genre.name.toLowerCase()}`}
                    key={genre.id}
                    passHref
                  >
                    <Badge
                      colorScheme="blue"
                      cursor="pointer"
                      _hover={{ bg: "blue.500", color: "white" }}
                    >
                      {genre.name}
                    </Badge>
                  </Link>
                ))}
              </HStack>
            )}

            {/* Movie overview */}
            <Box>
              <Heading size="md" mb={2}>
                Overview
              </Heading>
              <Text>{movie.overview || "No overview available."}</Text>
            </Box>
          </VStack>
        </Flex>

        {/* Cast Section */}
        <Box mb={8}>
          <Heading size="lg" mb={4}>
            Cast
          </Heading>
          {isLoadingCast ? (
            <Center py={8}>
              <Spinner />
            </Center>
          ) : castData?.cast && castData.cast.length > 0 ? (
            <SimpleGrid minChildWidth="120px" spacing={4}>
              {castData.cast.slice(0, 12).map((person) => (
                <Link key={person.id} href={`/actors/${person.id}`} passHref>
                  <VStack
                    spacing={2}
                    p={2}
                    borderRadius="md"
                    _hover={{ bg: "gray.700" }}
                    cursor="pointer"
                    align="center"
                  >
                    <Avatar
                      size="xl"
                      name={person.name}
                      src={
                        person.profile_path
                          ? `https://image.tmdb.org/t/p/w185${person.profile_path}`
                          : undefined
                      }
                    />
                    <Text fontWeight="bold" textAlign="center" noOfLines={1}>
                      {person.name}
                    </Text>
                    <Text
                      fontSize="sm"
                      color="gray.400"
                      textAlign="center"
                      noOfLines={1}
                    >
                      {person.character}
                    </Text>
                  </VStack>
                </Link>
              ))}
            </SimpleGrid>
          ) : (
            <Text color="gray.400">No cast information available.</Text>
          )}
        </Box>

        {/* Related Movies Section */}
        <Box mb={8}>
          <Heading size="lg" mb={4}>
            Related Movies
          </Heading>
          {isLoadingRelated ? (
            <Center py={8}>
              <Spinner />
            </Center>
          ) : relatedMoviesData?.movies &&
            relatedMoviesData.movies.length > 0 ? (
            <SimpleGrid columns={{ base: 2, sm: 3, md: 4, lg: 5 }} spacing={4}>
              {relatedMoviesData.movies.slice(0, 5).map((movie) => (
                <Box key={movie.id}>
                  <MovieCard movie={movie} size="sm" />
                </Box>
              ))}
            </SimpleGrid>
          ) : (
            <Text color="gray.400">No related movies found.</Text>
          )}
        </Box>
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

    // Prefetch cast and related movies
    await Promise.allSettled([
      queryClient.prefetchQuery({
        queryKey: ["movie-cast", movieId],
        queryFn: async () => {
          const response = await fetch(
            `http://localhost:8000/movies/${movieId}/cast`
          );
          if (!response.ok) return { cast: [] };
          return await response.json();
        },
      }),
      queryClient.prefetchQuery({
        queryKey: ["related-movies", movieId],
        queryFn: async () => {
          const response = await fetch(
            `http://localhost:8000/movies/${movieId}/related`
          );
          if (!response.ok) return { movies: [] };
          return await response.json();
        },
      }),
    ]);

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
