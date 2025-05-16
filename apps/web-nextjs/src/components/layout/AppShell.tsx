"use client";

import React, { memo } from "react";
import NavBar from "./NavBar";
import SideBar from "./SideBar";
import { Box, Grid, GridItem, Show } from "@chakra-ui/react";
import { useSyncFiltersToUrl } from "@/hooks/filter/useSyncFilterToUrl";
import { useFilterResetOnRouteChange } from "@/hooks/filter/useFilterResetOnRouteChange";
import { useMovieFilterRehydration } from "@/hooks/filter/useMovieFilterRehydration";

// Memoize child components to prevent unnecessary re-renders
const MemoizedNavBar = memo(NavBar);
const MemoizedSideBar = memo(SideBar);

/**
 * AppShell component
 * Responsible for the UI shell of the application
 * Memoized client component that provides the main layout structure
 */
function AppShell({ children }: { children: React.ReactNode }) {
  useFilterResetOnRouteChange();
  useMovieFilterRehydration();
  useSyncFiltersToUrl();

  return (
    <>
      <MemoizedNavBar />

      <Box px={{ base: 0, xl: 32 }} maxW="1600px" mx="auto" paddingX={5}>
        <Grid
          templateAreas={{
            base: `"main"`,
            lg: `"aside main"`,
          }}
          templateColumns={{ base: "1fr", lg: "200px 1fr" }}
        >
          <Show above="lg">
            <GridItem area="aside" paddingRight={5}>
              <MemoizedSideBar />
            </GridItem>
          </Show>
          <GridItem area="main">{children}</GridItem>
        </Grid>
      </Box>
    </>
  );
}

// Export the memoized component to prevent unnecessary re-renders
export default memo(AppShell);
