"use client";

import { Box, Grid, GridItem, Heading, Show, Spinner } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";
import MovieGrid from "@/components/home/MovieGrid";
import LeftNavBar from "@/components/layout/LeftNavBar";
import SortSelector from "@/components/layout/SortSelector";
import { useParams } from "next/navigation";

const ActorPage = () => {
  const params = useParams();
  const actorId = Number(params.id);

  const { data: movies, isLoading } = useQuery({
    queryKey: ["movies", "actor", actorId],
    queryFn: () => MovieAPI.getMovies({ actor_id: actorId }),
  });

  if (isLoading) {
    return <Spinner />;
  }

  if (!movies || movies.movies.length === 0) {
    return <Box>No movies found for this actor</Box>;
  }

  // Get actor name from the first movie's cast
  const actorName =
    movies.movies[0].actors?.find((a) => a.actor_id === actorId)?.name ||
    "Actor";

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
            <Heading as="h1" marginY={5}>
              Movies featuring {actorName}
            </Heading>
            <Box marginBottom={5}>
              <SortSelector />
            </Box>
          </Box>
          <MovieGrid
            columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
            source="movie_listing"
            actor_id={actorId}
          />
        </GridItem>
      </Grid>
    </Box>
  );
};

export default ActorPage;
