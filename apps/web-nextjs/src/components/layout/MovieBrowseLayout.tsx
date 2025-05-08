"use client";

import LeftNavBar from "@/components/layout/LeftNavBar";
import SortSelector from "@/components/layout/SortSelector";
import { Box, Grid, GridItem, Heading, Show, Skeleton } from "@chakra-ui/react";
import dynamic from "next/dynamic";
import React, { memo, ReactNode, Suspense } from "react";

// Memoize components to prevent unnecessary re-renders
const MemoizedLeftNavBar = memo(LeftNavBar);
const MemoizedSortSelector = memo(SortSelector);

// Dynamically import the filter component
const DynamicMovieFilter = dynamic(
  () => import("@/components/home/MovieFilter"),
  {
    ssr: false,
    loading: () => <Skeleton height="200px" width="100%" />,
  }
);

interface MovieBrowseLayoutProps {
  children: ReactNode;
  title: ReactNode;
  rightHeader?: ReactNode;
}

/**
 * Shared layout for movie browsing pages
 * Provides consistent structure for home, genre, and other browsing views
 */
const MovieBrowseLayout: React.FC<MovieBrowseLayoutProps> = ({
  children,
  title,
  rightHeader,
}) => {
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
            <MemoizedLeftNavBar />
            <Heading fontSize="2xl" marginTop={9} marginBottom={3}>
              Filter by
            </Heading>
            <Suspense fallback={<Skeleton height="200px" width="100%" />}>
              <DynamicMovieFilter />
            </Suspense>
          </GridItem>
        </Show>
        <GridItem area="main">
          <Box
            marginBottom={5}
            marginRight={{ base: -5, md: "auto" }}
            marginLeft={{ base: -5, md: "auto" }}
          >
            {title}
            <Box marginBottom={5}>
              {rightHeader || <MemoizedSortSelector />}
            </Box>
          </Box>
          {children}
        </GridItem>
      </Grid>
    </Box>
  );
};

export default memo(MovieBrowseLayout);
