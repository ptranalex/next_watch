"use client";

import { Box, Grid, GridItem, Heading, Show, Divider } from "@chakra-ui/react";
import RatingSliderGroup from "@/src/components/movies/filter/MovieFilter";
import MovieGrid from "@/src/components/movies/grid/MovieGrid";
import MovieHeading from "@/src/components/movies/grid/MovieHeading";
import LeftNavBar from "@/src/components/layout/LeftNavBar";
import SortSelector from "@/src/components/layout/SortSelector";
import TopMovies from "@/src/components/movies/TopMovies";
import { useSlugLogic } from "@/src/hooks/useSlugLogic";

export default function HomePage() {
  const title = useSlugLogic();

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
            <Heading fontSize="2xl" marginTop={9} marginBottom={3}>
              Filter by
            </Heading>
            <RatingSliderGroup />
          </GridItem>
        </Show>
        <GridItem area="main">
          <Box paddingLeft={0}>
            <MovieHeading title={title} />
            <Box marginBottom={5}>
              <SortSelector />
            </Box>
          </Box>
          <MovieGrid
            columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
            source="movie_listing"
          />

          {/* Top Movies Sections */}
          <Divider my={10} />

          {/* This Year's Top Movies */}
          <TopMovies
            title={`Top Movies of ${new Date().getFullYear()}`}
            showYearSelector={false}
            isAllTime={false}
            limit={12}
          />

          {/* All-Time Top Movies */}
          <Divider my={10} />
          <TopMovies
            title="All-Time Classics"
            isAllTime={true}
            showYearSelector={false}
            limit={12}
          />
        </GridItem>
      </Grid>
    </Box>
  );
}
