import {
  Box,
  Circle,
  GridItem,
  HStack,
  SimpleGrid,
  Skeleton,
  SkeletonText,
  Stack,
} from "@chakra-ui/react";
import React from "react";

interface MovieSkeletonProps {
  isSmallerScreen: boolean;
}

/**
 * Skeleton loading state for movie details
 */
const MovieSkeleton: React.FC<MovieSkeletonProps> = ({ isSmallerScreen }) => {
  return (
    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5}>
      {!isSmallerScreen && (
        <GridItem display="flex" justifyContent="flex-end">
          <Box maxWidth={280}>
            <Stack alignItems="flex-end">
              <Skeleton height="400px" width="100%" />
            </Stack>
          </Box>
        </GridItem>
      )}
      <GridItem colSpan={2}>
        <Box
          marginBottom={5}
          marginRight={{ base: -5, md: "auto" }}
          marginLeft={{ base: -5, md: "auto" }}
        >
          <Skeleton height="300px" width="100%" />
        </Box>

        {/* Movie Title */}
        <Skeleton height="60px" width="50%" marginBottom={2} />

        {/* Year & Runtime */}
        <HStack spacing={3} marginBottom={3}>
          <Skeleton height="20px" width="50px" />
          <Skeleton height="20px" width="10px" />
          <Skeleton height="20px" width="40px" />
        </HStack>

        {/* Genre */}
        <Skeleton height="20px" width="100px" marginBottom={4} />

        {/* Rating Circles */}
        <HStack spacing={4} marginBottom={5}>
          <Skeleton>
            <Circle size="60px" />
          </Skeleton>
          <Skeleton>
            <Circle size="60px" />
          </Skeleton>
          <Skeleton>
            <Circle size="60px" />
          </Skeleton>
        </HStack>

        {/* Movie Description */}
        <SkeletonText noOfLines={4} spacing={2} marginBottom={7} />

        {/* Details Section */}
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} marginY={8}>
          <Box>
            <Skeleton height="20px" width="80px" marginBottom={2} />
            <Skeleton height="20px" width="120px" marginBottom={5} />

            <Skeleton height="20px" width="80px" marginBottom={2} />
            <Skeleton height="20px" width="60px" marginBottom={5} />

            <Skeleton height="20px" width="80px" marginBottom={2} />
            <Skeleton height="20px" width="150px" marginBottom={5} />
          </Box>

          <Box>
            <Skeleton height="20px" width="80px" marginBottom={2} />
            <Skeleton height="20px" width="120px" marginBottom={5} />

            <Skeleton height="20px" width="80px" marginBottom={2} />
            <Skeleton height="20px" width="180px" marginBottom={5} />

            <Skeleton height="20px" width="80px" marginBottom={2} />
            <Skeleton height="20px" width="100px" />
          </Box>
        </SimpleGrid>

        {/* More Like This Section */}
        <Skeleton height="30px" width="40%" marginY={5} />
        <SimpleGrid columns={{ base: 3, md: 3, lg: 4 }} spacing={3} padding={1}>
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} height="200px" width="100%" />
          ))}
        </SimpleGrid>
      </GridItem>
    </SimpleGrid>
  );
};

export default React.memo(MovieSkeleton);
