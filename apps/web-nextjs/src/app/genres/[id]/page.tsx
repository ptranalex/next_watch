"use client";

import {
  Box,
  Grid,
  GridItem,
  Heading,
  Show,
  Skeleton,
  SkeletonText,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";
import MovieGrid from "@/components/home/MovieGrid";
import LeftNavBar from "@/components/layout/LeftNavBar";
import SortSelector from "@/components/layout/SortSelector";
import { useParams } from "next/navigation";

const GenrePage = () => {
  const params = useParams();
  const genreId = Number(params.id);

  const { data: movies, isLoading } = useQuery({
    queryKey: ["movies", "genre", genreId],
    queryFn: () => MovieAPI.getMovies({ genre_id: genreId }),
    staleTime: 1 * 60 * 1000, // 1 minute
  });

  // Get the genre name, with fallback for loading state
  const genreName = isLoading
    ? null // We'll handle this with a skeleton
    : movies?.movies[0]?.genres?.find((g) => g.id === genreId)?.name ||
      "Movies";

  return (
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
        <GridItem area="main">
          <Box
            marginBottom={5}
            marginRight={{ base: -5, md: "auto" }}
            marginLeft={{ base: -5, md: "auto" }}
          >
            {isLoading ? (
              <Box marginY={5}>
                <Skeleton height="40px" width="200px" />
              </Box>
            ) : (
              <Heading as="h1" marginY={5}>
                {genreName}
              </Heading>
            )}
            <Box marginBottom={5}>
              <SortSelector />
            </Box>
          </Box>

          {isLoading ? (
            <Box>
              <SkeletonText
                mt="4"
                noOfLines={1}
                spacing="4"
                skeletonHeight="2"
              />
              <Grid
                templateColumns={{
                  base: "repeat(3, 1fr)",
                  sm: "repeat(3, 1fr)",
                  md: "repeat(4, 1fr)",
                  lg: "repeat(6, 1fr)",
                }}
                gap={3}
                mt={6}
              >
                {Array.from({ length: 12 }).map((_, i) => (
                  <Skeleton key={i} height="300px" borderRadius="md" />
                ))}
              </Grid>
            </Box>
          ) : movies && movies.movies.length > 0 ? (
            <MovieGrid
              columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
              source="movie_listing"
              genre_id={genreId}
            />
          ) : (
            <Box>No movies found for this genre</Box>
          )}
        </GridItem>
      </Grid>
    </Box>
  );
};

export default GenrePage;
