"use client";

import { Box, Grid, GridItem, Heading, Show } from "@chakra-ui/react";
import RatingSliderGroup from "@/components/home/MovieFilter";
import MovieGrid from "@/components/home/MovieGrid";
import MovieHeading from "@/components/home/MovieHeading";
import LeftNavBar from "@/components/layout/LeftNavBar";
import SortSelector from "@/components/layout/SortSelector";
import { useSlugLogic } from "@/hooks";

/**
 * HomePage component - Entry point for the application's main page
 *
 * This component is responsible for:
 * 1. Rendering the home page layout with filters and movie grid
 * 2. Leveraging shared components for consistency
 * 3. Implementing page-specific logic
 *
 * It relies on global state from providers, but doesn't set up providers itself.
 */

const HomePage: React.FC = () => {
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
          <Box
            marginBottom={5}
            marginRight={{ base: -5, md: "auto" }}
            marginLeft={{ base: -5, md: "auto" }}
          >
            <MovieHeading title={title} />
            <Box marginBottom={5}>
              <SortSelector />
            </Box>
          </Box>
          <MovieGrid
            columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
            source="movie_listing"
          />
        </GridItem>
      </Grid>
    </Box>
  );
};

export default HomePage;
