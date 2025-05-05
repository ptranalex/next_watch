"use client";

import {
  Box,
  Grid,
  GridItem,
  Heading,
  Show,
  SimpleGrid,
  Spinner,
  Stack,
  Text,
  useMediaQuery,
  Skeleton,
  SkeletonText,
  HStack,
  Circle,
} from "@chakra-ui/react";
import LeftNavBar from "@/components/layout/LeftNavBar";
import { useAuth, useMovie } from "@/hooks";
import { Movie } from "@/domain/entities";
import MovieDetailView from "@/components/movieDetails/MovieDetailView";

// Shared layout component to ensure consistency between loading and loaded states
const MovieLayout = ({ children }: { children: React.ReactNode }) => (
  <Box px={{ base: 0, xl: 32 }} maxW="1600px" mx="auto">
    <Grid
      templateAreas={{
        base: `"main"`,
        lg: `"aside main"`,
      }}
      templateColumns={{ base: "1fr", lg: "200px 1fr" }}
    >
      <Show above="lg">
        <GridItem area="aside" paddingX={5}>
          <LeftNavBar />
        </GridItem>
      </Show>
      <GridItem area="main" px={{ base: 2, md: 4 }}>
        {children}
      </GridItem>
    </Grid>
  </Box>
);

const MovieDetailPage = ({ params }: { params: { id: string } }) => {
  const { isAuthenticated } = useAuth();
  const [isSmallerScreen] = useMediaQuery("(max-width: 600px)");

  const {
    movie,
    isLoading,
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist,
  } = useMovie(Number(params.id));

  // Function to update movie from UI interactions
  const updateMovie = (updatedMovie: Movie) => {
    if (!movie) return;

    if (updatedMovie.watched !== movie.watched) {
      toggleWatched();
    } else if (updatedMovie.liked !== movie.liked) {
      toggleLiked();
    } else if (updatedMovie.in_watchlist !== movie.in_watchlist) {
      toggleWatchlist();
    }
  };

  if (isLoading) {
    return (
      <MovieLayout>
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5}>
          {!isSmallerScreen && (
            <GridItem display="flex" justifyContent="flex-end">
              <Box maxWidth={280}>
                <Stack alignItems="flex-end">
                  <Skeleton height="400px" width="100%" />
                </Stack>
              </Box>
            </GridItem>
          )}
          <GridItem colSpan={2}>
            <Box
              marginBottom={5}
              marginRight={{ base: -5, md: "auto" }}
              marginLeft={{ base: -5, md: "auto" }}
            >
              <Skeleton height="300px" width="100%" />
            </Box>

            {/* Movie Title */}
            <Skeleton height="60px" width="50%" marginBottom={2} />

            {/* Year & Runtime */}
            <HStack spacing={3} marginBottom={3}>
              <Skeleton height="20px" width="50px" />
              <Skeleton height="20px" width="10px" />
              <Skeleton height="20px" width="40px" />
            </HStack>

            {/* Genre */}
            <Skeleton height="20px" width="100px" marginBottom={4} />

            {/* Rating Circles */}
            <HStack spacing={4} marginBottom={5}>
              <Skeleton>
                <Circle size="60px" />
              </Skeleton>
              <Skeleton>
                <Circle size="60px" />
              </Skeleton>
              <Skeleton>
                <Circle size="60px" />
              </Skeleton>
            </HStack>

            {/* Movie Description */}
            <SkeletonText noOfLines={4} spacing={2} marginBottom={7} />

            {/* Details Section */}
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} marginY={8}>
              <Box>
                <Skeleton height="20px" width="80px" marginBottom={2} />
                <Skeleton height="20px" width="120px" marginBottom={5} />

                <Skeleton height="20px" width="80px" marginBottom={2} />
                <Skeleton height="20px" width="60px" marginBottom={5} />

                <Skeleton height="20px" width="80px" marginBottom={2} />
                <Skeleton height="20px" width="150px" marginBottom={5} />
              </Box>

              <Box>
                <Skeleton height="20px" width="80px" marginBottom={2} />
                <Skeleton height="20px" width="120px" marginBottom={5} />

                <Skeleton height="20px" width="80px" marginBottom={2} />
                <Skeleton height="20px" width="180px" marginBottom={5} />

                <Skeleton height="20px" width="80px" marginBottom={2} />
                <Skeleton height="20px" width="100px" />
              </Box>
            </SimpleGrid>

            {/* More Like This Section */}
            <Skeleton height="30px" width="40%" marginY={5} />
            <SimpleGrid
              columns={{ base: 3, md: 3, lg: 4 }}
              spacing={3}
              padding={1}
            >
              {[...Array(8)].map((_, i) => (
                <Skeleton key={i} height="200px" width="100%" />
              ))}
            </SimpleGrid>
          </GridItem>
        </SimpleGrid>
      </MovieLayout>
    );
  }

  if (error) {
    console.error("Error loading movie:", error);
    return (
      <MovieLayout>
        <Box textAlign="center" py={10}>
          <Heading size="md">Error Loading Movie</Heading>
          <Text mt={4}>
            Sorry, we couldn't load this movie. Please try again later.
          </Text>
        </Box>
      </MovieLayout>
    );
  }

  if (!movie) {
    return (
      <MovieLayout>
        <Box textAlign="center" py={10}>
          <Heading size="md">Movie Not Found</Heading>
          <Text mt={4}>We couldn't find the movie you're looking for.</Text>
        </Box>
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
