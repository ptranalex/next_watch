import React, { useState } from "react";
import {
  Box,
  Heading,
  Text,
  Flex,
  Image,
  VStack,
  HStack,
  Divider,
  Spinner,
  Badge,
} from "@chakra-ui/react";
import { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import {
  dehydrate,
  QueryClient,
  useQuery,
  useInfiniteQuery,
} from "@tanstack/react-query";
import {
  getActorById,
  getMoviesByActor,
  Actor,
  MoviesQueryParams,
  MovieListResponse,
} from "../../services/movie-service";
import MovieGrid from "../../components/movies/MovieGrid";

interface ActorPageProps {
  actorId: number;
  initialParams: MoviesQueryParams;
}

const ActorPage: NextPage<ActorPageProps> = ({ actorId, initialParams }) => {
  const [pageSize] = useState(20);

  // Fetch actor details
  const {
    data: actor,
    isLoading: isLoadingActor,
    error: actorError,
  } = useQuery({
    queryKey: ["actor", actorId],
    queryFn: () => getActorById(actorId),
    staleTime: 1000 * 60 * 10, // 10 minutes
    refetchOnWindowFocus: false,
  });

  // Fetch movies by actor using infinite query
  const {
    data,
    isLoading: isLoadingMovies,
    error: moviesError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["movies-by-actor-infinite", actorId, pageSize],
    queryFn: ({ pageParam = 1 }) =>
      getMoviesByActor(actorId, pageParam, pageSize),
    getNextPageParam: (lastPage: MovieListResponse) => {
      if (lastPage.page < Math.ceil(lastPage.total / lastPage.page_size)) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });

  // Extract all movies from all pages
  const allMovies = data?.pages.flatMap((page) => page.movies) || [];
  const totalMovies = data?.pages[0]?.total || 0;

  const handleLoadMore = () => {
    if (!isFetchingNextPage) {
      fetchNextPage();
    }
  };

  // Handle loading state
  if (isLoadingActor && !actor) {
    return (
      <Box p={8} textAlign="center">
        <Spinner size="xl" color="blue.400" />
        <Text mt={4}>Loading actor information...</Text>
      </Box>
    );
  }

  // Handle error state
  if (actorError) {
    return (
      <Box p={8} textAlign="center">
        <Heading size="lg" mb={4}>
          Error Loading Actor
        </Heading>
        <Text color="red.400">
          {(actorError as Error).message || "Failed to load actor details"}
        </Text>
      </Box>
    );
  }

  // Format date if available
  const formatDate = (dateString?: string) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <>
      <Head>
        <title>{actor?.name || "Actor"} | Next Watch</title>
        <meta
          name="description"
          content={`View movies featuring ${actor?.name || "the actor"}`}
        />
      </Head>

      <Box p={4}>
        {/* Actor details section */}
        <Flex
          direction={{ base: "column", md: "row" }}
          gap={8}
          mb={10}
          alignItems={{ base: "center", md: "flex-start" }}
        >
          {/* Actor profile image */}
          <Box
            minWidth={{ base: "100%", md: "250px" }}
            maxWidth={{ base: "300px", md: "250px" }}
          >
            {actor?.profile_path ? (
              <Image
                src={`https://image.tmdb.org/t/p/w500${actor.profile_path}`}
                alt={actor.name}
                borderRadius="md"
                objectFit="cover"
                width="100%"
              />
            ) : (
              <Box
                height="375px"
                width="100%"
                bg="gray.700"
                borderRadius="md"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <Text color="gray.400">No Image Available</Text>
              </Box>
            )}
          </Box>

          {/* Actor details */}
          <VStack align="stretch" flex={1} spacing={4}>
            <Heading size="xl">{actor?.name}</Heading>

            {actor?.known_for_department && (
              <Badge colorScheme="blue" alignSelf="flex-start">
                {actor.known_for_department}
              </Badge>
            )}

            <HStack spacing={10} flexWrap="wrap">
              {actor?.birthday && (
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.400">
                    Birthday
                  </Text>
                  <Text>{formatDate(actor.birthday)}</Text>
                </Box>
              )}

              {actor?.place_of_birth && (
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.400">
                    Place of Birth
                  </Text>
                  <Text>{actor.place_of_birth}</Text>
                </Box>
              )}

              {actor?.popularity && (
                <Box>
                  <Text fontWeight="bold" fontSize="sm" color="gray.400">
                    Popularity
                  </Text>
                  <Text>{actor.popularity.toFixed(1)}</Text>
                </Box>
              )}
            </HStack>

            {actor?.biography && (
              <Box>
                <Text fontWeight="bold" fontSize="sm" color="gray.400" mb={1}>
                  Biography
                </Text>
                <Text noOfLines={{ base: 5, md: 10 }}>{actor.biography}</Text>
              </Box>
            )}

            {actor?.also_known_as && actor.also_known_as.length > 0 && (
              <Box>
                <Text fontWeight="bold" fontSize="sm" color="gray.400" mb={1}>
                  Also Known As
                </Text>
                <Text>{actor.also_known_as.join(", ")}</Text>
              </Box>
            )}
          </VStack>
        </Flex>

        <Divider my={6} />

        {/* Movies section */}
        <Box mb={4}>
          <Heading size="lg" mb={6}>
            Movies with {actor?.name} ({totalMovies})
          </Heading>

          {moviesError ? (
            <Text color="red.400">
              Error loading movies: {(moviesError as Error).message}
            </Text>
          ) : (
            <MovieGrid
              movies={allMovies}
              isLoading={isLoadingMovies || isFetchingNextPage}
              hasMore={hasNextPage}
              onLoadMore={handleLoadMore}
            />
          )}
        </Box>
      </Box>
    </>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { id } = context.params || {};
  const actorId = parseInt(String(id), 10);

  // Return 404 for invalid IDs
  if (isNaN(actorId)) {
    return {
      notFound: true,
    };
  }

  const queryClient = new QueryClient();
  const pageSize = 20; // Match the pageSize used in the component

  try {
    // Prefetch actor details (actorId is now the TMDB person ID)
    await queryClient.prefetchQuery({
      queryKey: ["actor", actorId],
      queryFn: () => getActorById(actorId),
    });

    // Prefetch first page of movies for initial render (using TMDB person ID)
    try {
      const moviesData = await getMoviesByActor(actorId, 1, pageSize);

      // Manually set the infinite query data structure
      queryClient.setQueryData(
        ["movies-by-actor-infinite", actorId, pageSize],
        {
          pages: [moviesData],
          pageParams: [1],
        }
      );
    } catch (err) {
      console.error(`Error fetching movies for actor ${actorId}:`, err);
      // Continue despite movie fetch error - the page will handle it
    }

    return {
      props: {
        actorId,
        initialParams: { actor_id: actorId, page: 1, pageSize },
        dehydratedState: dehydrate(queryClient),
      },
    };
  } catch (error) {
    console.error(`Error in getServerSideProps for actor ${actorId}:`, error);
    return {
      props: {
        actorId,
        initialParams: { actor_id: actorId, page: 1, pageSize },
      },
    };
  }
};

export default ActorPage;
