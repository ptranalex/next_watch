import React from "react";
import {
  Box,
  Flex,
  Skeleton,
  SkeletonText,
  useBreakpointValue,
  useColorModeValue,
} from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieSkeleton");

interface MovieSkeletonProps {
  count?: number;
  isGrid?: boolean;
}

/**
 * MovieSkeleton component
 *
 * Mobile-optimized skeleton loading state for movie cards
 * Responsive design that adapts to list view on mobile and grid on desktop
 */
const MovieSkeleton: React.FC<MovieSkeletonProps> = ({ count = 6, isGrid }) => {
  // Responsive adaptation
  const isDesktop = useBreakpointValue({ base: false, md: true });

  // Determine if we show in grid or list mode
  const displayAsGrid = isGrid ?? isDesktop;

  // Use semantic colors for skeletons
  const startColor = useColorModeValue("gray.100", "gray.600");
  const endColor = useColorModeValue("gray.300", "gray.800");
  const cardBg = useColorModeValue("bg.secondary", "bg.tertiary");
  const borderColor = useColorModeValue("border.subtle", "border.subtle");

  // Log component rendering
  logger.debug(
    `Rendering MovieSkeleton - count: ${count}, displayAsGrid: ${displayAsGrid}`
  );

  return (
    <>
      {displayAsGrid ? (
        // Grid layout for desktop
        <Box
          display="grid"
          gridTemplateColumns={{
            base: "repeat(2, 1fr)",
            sm: "repeat(3, 1fr)",
            lg: "repeat(4, 1fr)",
            xl: "repeat(5, 1fr)",
          }}
          gap={5}
        >
          {Array(count)
            .fill(0)
            .map((_, index) => (
              <Box key={index} borderRadius="lg" overflow="hidden" bg={cardBg}>
                {/* Movie poster skeleton */}
                <Skeleton
                  height="260px"
                  width="100%"
                  startColor={startColor}
                  endColor={endColor}
                  speed={1.2}
                />

                {/* Movie info skeleton */}
                <Box p={3}>
                  <SkeletonText
                    mt={1}
                    noOfLines={1}
                    spacing="2"
                    skeletonHeight="4"
                    startColor={startColor}
                    endColor={endColor}
                  />
                  <SkeletonText
                    mt={2}
                    noOfLines={1}
                    spacing="2"
                    skeletonHeight="3"
                    width="60%"
                    startColor={startColor}
                    endColor={endColor}
                  />
                </Box>
              </Box>
            ))}
        </Box>
      ) : (
        // List layout for mobile
        <Box>
          {Array(count)
            .fill(0)
            .map((_, index) => (
              <Box
                key={index}
                p={3}
                mb={2}
                borderWidth="1px"
                borderColor={borderColor}
                borderRadius="md"
                bg={cardBg}
              >
                <Flex>
                  {/* Movie poster skeleton */}
                  <Skeleton
                    width="80px"
                    height="120px"
                    borderRadius="md"
                    startColor={startColor}
                    endColor={endColor}
                    speed={1.2}
                  />

                  {/* Movie details skeleton */}
                  <Flex
                    direction="column"
                    ml={4}
                    flex={1}
                    justifyContent="space-between"
                  >
                    <Box>
                      <SkeletonText
                        noOfLines={1}
                        spacing="2"
                        skeletonHeight="4"
                        startColor={startColor}
                        endColor={endColor}
                      />
                      <SkeletonText
                        mt={2}
                        noOfLines={1}
                        spacing="2"
                        skeletonHeight="3"
                        width="30%"
                        startColor={startColor}
                        endColor={endColor}
                      />
                    </Box>

                    {/* Action buttons skeleton */}
                    <Flex mt={2} justify="space-between">
                      <Skeleton
                        height="8"
                        width="8"
                        startColor={startColor}
                        endColor={endColor}
                        borderRadius="md"
                      />
                      <Skeleton
                        height="8"
                        width="8"
                        startColor={startColor}
                        endColor={endColor}
                        borderRadius="md"
                      />
                      <Skeleton
                        height="8"
                        width="8"
                        startColor={startColor}
                        endColor={endColor}
                        borderRadius="md"
                      />
                    </Flex>
                  </Flex>
                </Flex>
              </Box>
            ))}
        </Box>
      )}
    </>
  );
};

export default MovieSkeleton;
