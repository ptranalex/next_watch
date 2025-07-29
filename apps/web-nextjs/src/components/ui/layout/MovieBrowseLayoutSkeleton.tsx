"use client";

import { Box, Flex, Skeleton, useColorModeValue } from "@chakra-ui/react";
import React, { memo } from "react";
import { useResponsive } from "@/providers";
import MovieGridSkeleton from "@/components/features/movies/grid/MovieGridSkeleton";

// Column breakpoints type (matches MovieGrid)
type ColumnBreakpoints =
  | {
      [key in "base" | "sm" | "md" | "lg" | "xl"]?: number;
    }
  | number
  | number[];

interface MovieBrowseLayoutSkeletonProps {
  titleWidth?: string;
  columns?: ColumnBreakpoints;
  movieCount?: number;
  showControls?: boolean;
  showSidebar?: boolean;
}

const MovieBrowseLayoutSkeleton = memo(
  ({
    titleWidth = "200px",
    columns = { base: 2, sm: 3, md: 4, lg: 5, xl: 6 },
    movieCount = 12,
    showControls = true,
    showSidebar = false,
  }: MovieBrowseLayoutSkeletonProps) => {
    const { isMobile, isHydrated } = useResponsive();
    const startColor = useColorModeValue("gray.100", "gray.600");
    const endColor = useColorModeValue("gray.300", "gray.800");
    const bgColor = useColorModeValue("white", "gray.900");

    if (!isHydrated || !isMobile) {
      return (
        <Box
          w="100%"
          className="desktop-movie-browse-layout-skeleton"
          bg={bgColor}
          minH="100vh"
        >
          {/* Header */}
          <Box marginY={5}>
            <Skeleton
              height="32px"
              width={titleWidth}
              marginBottom={5}
              borderRadius="md"
              startColor={startColor}
              endColor={endColor}
            />
            {/* Controls (search, sort, filter) */}
            {showControls && (
              <Box marginBottom={5}>
                <Flex alignItems="center" justifyContent="flex-end">
                  <Skeleton
                    height="40px"
                    width="200px"
                    marginRight={3}
                    borderRadius="md"
                    startColor={startColor}
                    endColor={endColor}
                  />
                  <Skeleton
                    height="40px"
                    width="120px"
                    marginRight={3}
                    borderRadius="md"
                    startColor={startColor}
                    endColor={endColor}
                  />
                  <Skeleton
                    height="40px"
                    width="100px"
                    borderRadius="md"
                    startColor={startColor}
                    endColor={endColor}
                  />
                </Flex>
              </Box>
            )}
          </Box>
          {/* Main content area */}
          <Flex>
            {showSidebar && (
              <Box
                marginRight={5}
                width="200px"
                display={{ base: "none", md: "block" }}
              >
                <Skeleton
                  height="300px"
                  width="100%"
                  borderRadius="md"
                  startColor={startColor}
                  endColor={endColor}
                />
              </Box>
            )}
            <Box flex="1">
              <MovieGridSkeleton columns={columns} count={movieCount} />
            </Box>
          </Flex>
          {/* Load more button */}
          <Box marginTop={8} textAlign="center">
            <Skeleton
              height="40px"
              width="200px"
              marginX="auto"
              borderRadius="md"
              startColor={startColor}
              endColor={endColor}
            />
          </Box>
        </Box>
      );
    }

    // Mobile layout (same structure, different responsive props)
    return (
      <Box
        w="100%"
        className="mobile-movie-browse-layout-skeleton"
        bg={bgColor}
        minH="100vh"
      >
        {/* Mobile Header */}
        <Box marginY={3}>
          <Skeleton
            height="28px"
            width={titleWidth}
            marginBottom={3}
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          {/* Mobile Controls */}
          {showControls && (
            <Box marginBottom={3}>
              <Flex alignItems="center" justifyContent="space-between">
                <Skeleton
                  height="36px"
                  width="150px"
                  borderRadius="md"
                  startColor={startColor}
                  endColor={endColor}
                />
                <Skeleton
                  height="36px"
                  width="80px"
                  borderRadius="md"
                  startColor={startColor}
                  endColor={endColor}
                />
              </Flex>
            </Box>
          )}
        </Box>
        {/* Mobile Grid */}
        <MovieGridSkeleton columns={2} count={movieCount} />
        {/* Mobile Load more button */}
        <Box marginTop={6} textAlign="center">
          <Skeleton
            height="40px"
            width="180px"
            marginX="auto"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
        </Box>
      </Box>
    );
  }
);

MovieBrowseLayoutSkeleton.displayName = "MovieBrowseLayoutSkeleton";

export default MovieBrowseLayoutSkeleton;
