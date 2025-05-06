import { Box, Grid, GridItem, Show } from "@chakra-ui/react";
import LeftNavBar from "@/components/layout/LeftNavBar";
import React from "react";

interface MovieLayoutProps {
  children: React.ReactNode;
}

/**
 * Shared layout component to ensure consistency across movie pages
 */
const MovieLayout: React.FC<MovieLayoutProps> = ({ children }) => (
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

export default React.memo(MovieLayout);
