import React from "react";
import {
  Box,
  Flex,
  Skeleton,
  SkeletonText,
  SimpleGrid,
  GridItem,
  Stack,
  useBreakpointValue,
  useColorModeValue,
} from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieDetailSkeleton");

/**
 * MovieDetailSkeleton component
 *
 * Mobile-optimized skeleton loading state for movie details
 * Responsive design that adapts between mobile/desktop layouts
 */
const MovieDetailSkeleton: React.FC = () => {
  // Use responsive state
  const isDesktop = useBreakpointValue({ base: false, md: true });

  // Dark mode support
  const startColor = useColorModeValue("gray.100", "gray.600");
  const endColor = useColorModeValue("gray.300", "gray.800");

  logger.debug(`Rendering MovieDetailSkeleton - isDesktop: ${isDesktop}`);

  return (
    <SimpleGrid
      columns={{ base: 1, md: 3 }}
      spacing={5}
      paddingY={5}
      pb={isDesktop ? 5 : 20}
    >
      {/* Poster image skeleton - only on desktop */}
      {isDesktop && (
        <GridItem display="flex" justifyContent="flex-end">
          <Box maxWidth={280}>
            <Stack alignItems="flex-end">
              <Skeleton
                height="400px"
                width="280px"
                borderRadius="md"
                startColor={startColor}
                endColor={endColor}
              />

              {/* Actors gallery skeleton */}
              <Flex mt={4} flexWrap="wrap" gap={2} justify="flex-end">
                {Array(4)
                  .fill(0)
                  .map((_, i) => (
                    <Skeleton
                      key={i}
                      height="50px"
                      width="50px"
                      borderRadius="full"
                      startColor="gray.600"
                      endColor="gray.700"
                    />
                  ))}
              </Flex>
            </Stack>
          </Box>
        </GridItem>
      )}

      {/* Main content area */}
      <GridItem colSpan={{ base: 1, md: 2 }}>
        {/* Trailer skeleton */}
        <Box
          marginBottom={5}
          marginRight={{ base: -5, md: "auto" }}
          marginLeft={{ base: -5, md: "auto" }}
        >
          <Skeleton
            height={isDesktop ? "400px" : "220px"}
            width="100%"
            startColor="gray.600"
            endColor="gray.800"
          />
        </Box>

        {/* Title skeleton */}
        <SkeletonText
          mt={2}
          noOfLines={1}
          skeletonHeight={8}
          width="80%"
          startColor="gray.500"
          endColor="gray.700"
        />

        {/* Basic info skeleton */}
        <SkeletonText
          mt={4}
          noOfLines={1}
          skeletonHeight={4}
          width="60%"
          startColor="gray.600"
          endColor="gray.700"
        />

        <SkeletonText
          mt={2}
          noOfLines={1}
          skeletonHeight={4}
          width="40%"
          startColor="gray.600"
          endColor="gray.700"
        />

        {/* Ratings skeleton */}
        <Flex mt={6} mb={6} gap={4}>
          {Array(3)
            .fill(0)
            .map((_, i) => (
              <Skeleton
                key={i}
                height="60px"
                width="60px"
                borderRadius="md"
                startColor="gray.600"
                endColor="gray.700"
              />
            ))}
        </Flex>

        {/* Action buttons - desktop only */}
        {isDesktop && (
          <Flex mt={4} mb={6} gap={4}>
            {Array(3)
              .fill(0)
              .map((_, i) => (
                <Skeleton
                  key={i}
                  height="40px"
                  width="120px"
                  borderRadius="md"
                  startColor="gray.600"
                  endColor="gray.700"
                />
              ))}
          </Flex>
        )}

        {/* Overview skeleton */}
        <SkeletonText
          mt={4}
          noOfLines={4}
          spacing={4}
          skeletonHeight={4}
          startColor="gray.600"
          endColor="gray.700"
        />

        {/* Actors gallery - mobile only */}
        {!isDesktop && (
          <Flex mt={6} flexWrap="wrap" gap={3}>
            {Array(6)
              .fill(0)
              .map((_, i) => (
                <Skeleton
                  key={i}
                  height="60px"
                  width="60px"
                  borderRadius="full"
                  startColor="gray.600"
                  endColor="gray.700"
                />
              ))}
          </Flex>
        )}

        {/* Movie attributes */}
        <Box mt={8}>
          {Array(3)
            .fill(0)
            .map((_, i) => (
              <Flex key={i} mt={4} justify="space-between">
                <Skeleton
                  height="20px"
                  width="100px"
                  startColor="gray.600"
                  endColor="gray.700"
                />
                <Skeleton
                  height="20px"
                  width="200px"
                  startColor="gray.600"
                  endColor="gray.700"
                />
              </Flex>
            ))}
        </Box>

        {/* Similar movies skeleton */}
        <SkeletonText
          mt={8}
          noOfLines={1}
          skeletonHeight={6}
          width="60%"
          startColor="gray.500"
          endColor="gray.700"
        />

        <Box
          mt={4}
          display="grid"
          gridTemplateColumns={{
            base: "repeat(2, 1fr)",
            sm: "repeat(3, 1fr)",
            md: "repeat(3, 1fr)",
          }}
          gap={4}
        >
          {Array(6)
            .fill(0)
            .map((_, i) => (
              <Skeleton
                key={i}
                height="180px"
                borderRadius="md"
                startColor="gray.600"
                endColor="gray.700"
              />
            ))}
        </Box>
      </GridItem>

      {/* Bottom action bar for mobile */}
      {!isDesktop && (
        <Flex
          position="fixed"
          bottom={0}
          left={0}
          right={0}
          height="64px"
          bg="gray.800"
          borderTop="1px"
          borderColor="gray.700"
          zIndex={10}
          justify="space-around"
          align="center"
          px={4}
        >
          {Array(4)
            .fill(0)
            .map((_, i) => (
              <Flex key={i} direction="column" align="center" justify="center">
                <Skeleton
                  height="24px"
                  width="24px"
                  borderRadius="md"
                  startColor="gray.600"
                  endColor="gray.700"
                  mb={1}
                />
                <Skeleton
                  height="12px"
                  width="40px"
                  startColor="gray.600"
                  endColor="gray.700"
                />
              </Flex>
            ))}
        </Flex>
      )}
    </SimpleGrid>
  );
};

export default MovieDetailSkeleton;
