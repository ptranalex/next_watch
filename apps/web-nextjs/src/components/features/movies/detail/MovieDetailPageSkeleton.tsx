"use client";

import {
  Box,
  GridItem,
  SimpleGrid,
  Skeleton,
  SkeletonText,
  VStack,
  HStack,
  Stack,
  useColorModeValue,
} from "@chakra-ui/react";
import React, { memo } from "react";
import { useResponsive } from "@/providers";
import {
  MovieCardContainer,
  MovieCardSkeleton,
} from "@/components/features/movies/card";

/**
 * MovieDetailPageSkeleton - Industry standard skeleton loading UI for Movie Detail pages
 *
 * Matches the EXACT structure of MovieDetailPage:
 *
 * DESKTOP (SimpleGrid columns={{ base: 1, md: 3 }}):
 * - Column 1: Movie poster + ActorsGallery
 * - Columns 2-3: TrailerCard + title/metadata + ratings + actions + overview + attributes + similar movies
 *
 * MOBILE (Single column):
 * - TrailerCard at top
 * - Title/metadata + ratings + overview + actors + attributes + similar movies
 * - Fixed bottom action controls
 *
 * Now properly supports dark mode with theme-aware colors and backgrounds.
 * Uses hydration-safe color mode values to prevent light->dark flashing.
 */
const MovieDetailPageSkeleton = memo(() => {
  const { isMobile } = useResponsive();
  const bgColor = useColorModeValue("white", "gray.900");

  if (isMobile) {
    return <MobileMovieDetailSkeleton />;
  }

  return (
    <Box bg={bgColor} minH="100vh" w="100%">
      <DesktopMovieDetailSkeleton />
    </Box>
  );
});

/**
 * Desktop Movie Detail Skeleton - Matches DesktopMovieDetailView structure
 */
const DesktopMovieDetailSkeleton = memo(() => {
  const startColor = useColorModeValue("gray.100", "gray.600");
  const endColor = useColorModeValue("gray.300", "gray.800");
  return (
    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5} paddingY={5}>
      {/* Column 1: Poster + ActorsGallery */}
      <GridItem display="flex" justifyContent="flex-end">
        <Box maxWidth={280}>
          <Stack alignItems="flex-end">
            <Skeleton
              width="280px"
              height="420px"
              borderRadius="md"
              marginBottom={4}
              startColor={startColor}
              endColor={endColor}
            />
            {/* ActorsGallery skeleton */}
            <VStack align="stretch" spacing={3} width="100%">
              <Skeleton
                height="20px"
                width="60px"
                borderRadius="sm"
                startColor={startColor}
                endColor={endColor}
              />
              <VStack spacing={2}>
                {Array.from({ length: 3 }, (_, i) => (
                  <HStack key={i} spacing={3}>
                    <Skeleton
                      width="40px"
                      height="40px"
                      borderRadius="full"
                      startColor={startColor}
                      endColor={endColor}
                    />
                    <VStack align="start" spacing={1} flex={1}>
                      <Skeleton
                        height="14px"
                        width="80px"
                        borderRadius="sm"
                        startColor={startColor}
                        endColor={endColor}
                      />
                      <Skeleton
                        height="12px"
                        width="60px"
                        borderRadius="sm"
                        startColor={startColor}
                        endColor={endColor}
                      />
                    </VStack>
                  </HStack>
                ))}
              </VStack>
            </VStack>
          </Stack>
        </Box>
      </GridItem>
      {/* Columns 2-3: Main content area */}
      <GridItem colSpan={{ base: 1, md: 2 }}>
        {/* TrailerCard skeleton */}
        <Box
          marginBottom={5}
          marginRight={{ base: -5, md: "auto" }}
          marginLeft={{ base: -5, md: "auto" }}
        >
          <Skeleton
            width="100%"
            height="300px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
        </Box>
        {/* Title */}
        <Skeleton
          height="32px"
          width="70%"
          marginBottom={2}
          borderRadius="md"
          startColor={startColor}
          endColor={endColor}
        />
        {/* Release year • Rated • Runtime */}
        <Skeleton
          height="16px"
          width="250px"
          marginBottom={1}
          borderRadius="sm"
          startColor={startColor}
          endColor={endColor}
        />
        {/* Genres */}
        <Skeleton
          height="16px"
          width="200px"
          marginBottom={5}
          borderRadius="sm"
          startColor={startColor}
          endColor={endColor}
        />
        {/* Ratings */}
        <HStack spacing={4} marginBottom={5}>
          <Skeleton
            height="40px"
            width="80px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="40px"
            width="80px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="40px"
            width="80px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
        </HStack>
        {/* User actions (only shown when signed in) */}
        <HStack spacing={4} marginBottom={5}>
          <Skeleton
            height="40px"
            width="100px"
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
          <Skeleton
            height="40px"
            width="120px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
        </HStack>
        {/* Movie overview (ExpandableText) */}
        <SkeletonText
          noOfLines={4}
          spacing="3"
          marginBottom={5}
          startColor={startColor}
          endColor={endColor}
        />
        {/* Movie attributes */}
        <VStack align="stretch" spacing={3} marginBottom={8}>
          {Array.from({ length: 4 }, (_, i) => (
            <HStack key={i} spacing={4}>
              <Skeleton
                height="16px"
                width="80px"
                borderRadius="sm"
                startColor={startColor}
                endColor={endColor}
              />
              <Skeleton
                height="16px"
                width="150px"
                borderRadius="sm"
                startColor={startColor}
                endColor={endColor}
              />
            </HStack>
          ))}
        </VStack>
        {/* Similar movies section */}
        <Box>
          {/* "More Like This" title */}
          <Skeleton
            height="28px"
            width="150px"
            marginBottom={4}
            marginTop={8}
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          {/* Similar movies grid */}
          <SimpleGrid columns={{ base: 2, sm: 3, md: 3, lg: 4 }} spacing={4}>
            {Array.from({ length: 4 }, (_, index) => (
              <SimilarMovieCardSkeleton key={`similar-movie-${index}`} />
            ))}
          </SimpleGrid>
        </Box>
      </GridItem>
    </SimpleGrid>
  );
});

/**
 * Mobile Movie Detail Skeleton - Matches MobileMovieDetailView structure
 */
const MobileMovieDetailSkeleton = memo(() => {
  const startColor = useColorModeValue("gray.100", "gray.600");
  const endColor = useColorModeValue("gray.300", "gray.800");
  const bgColor = useColorModeValue("white", "gray.900");

  return (
    <Box bg={bgColor} minH="100vh" paddingX={4} paddingY={4}>
      {/* Mobile poster and basic info */}
      <VStack spacing={4} align="stretch">
        {/* Poster */}
        <Box alignSelf="center">
          <Skeleton
            width="200px"
            height="300px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
        </Box>

        {/* Title and basic info */}
        <VStack spacing={2} align="center">
          <Skeleton
            height="24px"
            width="80%"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="16px"
            width="60%"
            borderRadius="sm"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="16px"
            width="50%"
            borderRadius="sm"
            startColor={startColor}
            endColor={endColor}
          />
        </VStack>

        {/* Ratings row */}
        <HStack spacing={3} justifyContent="center">
          <Skeleton
            height="32px"
            width="60px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="32px"
            width="60px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="32px"
            width="60px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
        </HStack>

        {/* Action buttons */}
        <HStack spacing={3} justifyContent="center">
          <Skeleton
            height="36px"
            width="80px"
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
          <Skeleton
            height="36px"
            width="100px"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
        </HStack>

        {/* Overview */}
        <Box>
          <Skeleton
            height="20px"
            width="100px"
            marginBottom={2}
            borderRadius="sm"
            startColor={startColor}
            endColor={endColor}
          />
          <SkeletonText
            noOfLines={3}
            spacing="2"
            startColor={startColor}
            endColor={endColor}
          />
        </Box>

        {/* Movie details */}
        <VStack align="stretch" spacing={2}>
          {Array.from({ length: 3 }, (_, i) => (
            <HStack key={i} spacing={3}>
              <Skeleton
                height="14px"
                width="60px"
                borderRadius="sm"
                startColor={startColor}
                endColor={endColor}
              />
              <Skeleton
                height="14px"
                width="120px"
                borderRadius="sm"
                startColor={startColor}
                endColor={endColor}
              />
            </HStack>
          ))}
        </VStack>

        {/* Similar movies section */}
        <Box marginTop={6}>
          <Skeleton
            height="24px"
            width="120px"
            marginBottom={4}
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          <SimpleGrid columns={2} spacing={3}>
            {Array.from({ length: 4 }, (_, index) => (
              <SimilarMovieCardSkeleton key={`mobile-similar-${index}`} />
            ))}
          </SimpleGrid>
        </Box>
      </VStack>
    </Box>
  );
});

/**
 * Similar Movie Card Skeleton - Matches MovieGrid card structure
 */
const SimilarMovieCardSkeleton = memo(() => {
  const startColor = useColorModeValue("gray.100", "gray.600");
  const endColor = useColorModeValue("gray.300", "gray.800");
  return (
    <MovieCardContainer>
      <MovieCardSkeleton />
      <VStack spacing={2} align="start" width="100%" marginTop={3}>
        <Skeleton
          height="16px"
          width="90%"
          borderRadius="sm"
          startColor={startColor}
          endColor={endColor}
        />
        <Skeleton
          height="14px"
          width="60%"
          borderRadius="sm"
          startColor={startColor}
          endColor={endColor}
        />
      </VStack>
    </MovieCardContainer>
  );
});

// Compact skeleton for faster loads
export const MovieDetailCompactSkeleton = memo(() => {
  const startColor = useColorModeValue("gray.100", "gray.600");
  const endColor = useColorModeValue("gray.300", "gray.800");

  return (
    <Box paddingY={5}>
      <HStack spacing={5} alignItems="flex-start">
        <Skeleton
          width="200px"
          height="300px"
          borderRadius="md"
          startColor={startColor}
          endColor={endColor}
        />
        <VStack align="stretch" spacing={3} flex={1}>
          <Skeleton
            height="32px"
            width="70%"
            borderRadius="md"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="16px"
            width="200px"
            borderRadius="sm"
            startColor={startColor}
            endColor={endColor}
          />
          <SkeletonText
            noOfLines={3}
            spacing="2"
            startColor={startColor}
            endColor={endColor}
          />
        </VStack>
      </HStack>
    </Box>
  );
});

// Export all components
export {
  SimilarMovieCardSkeleton,
  MobileMovieDetailSkeleton,
  DesktopMovieDetailSkeleton,
};

MovieDetailPageSkeleton.displayName = "MovieDetailPageSkeleton";
DesktopMovieDetailSkeleton.displayName = "DesktopMovieDetailSkeleton";
MobileMovieDetailSkeleton.displayName = "MobileMovieDetailSkeleton";
SimilarMovieCardSkeleton.displayName = "SimilarMovieCardSkeleton";
MovieDetailCompactSkeleton.displayName = "MovieDetailCompactSkeleton";

export default MovieDetailPageSkeleton;
