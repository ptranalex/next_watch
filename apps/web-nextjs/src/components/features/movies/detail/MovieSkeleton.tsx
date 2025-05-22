import {
  Box,
  Circle,
  GridItem,
  HStack,
  SimpleGrid,
  Skeleton,
  SkeletonText,
  Stack,
  useColorModeValue,
} from "@chakra-ui/react";
import React from "react";

interface MovieSkeletonProps {
  isSmallerScreen: boolean;
}

/**
 * Skeleton loading state for movie details
 */
const MovieSkeleton: React.FC<MovieSkeletonProps> = ({ isSmallerScreen }) => {
  const startColor = useColorModeValue("gray.100", "gray.700");
  const endColor = useColorModeValue("gray.400", "gray.900");

  return (
    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5}>
      {!isSmallerScreen && (
        <GridItem display="flex" justifyContent="flex-end">
          <Box maxWidth={280}>
            <Stack alignItems="flex-end">
              <Skeleton
                height="400px"
                width="100%"
                startColor={startColor}
                endColor={endColor}
              />
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
          <Skeleton
            height="300px"
            width="100%"
            startColor={startColor}
            endColor={endColor}
          />
        </Box>

        {/* Movie Title */}
        <Skeleton
          height="60px"
          width="50%"
          marginBottom={2}
          startColor={startColor}
          endColor={endColor}
        />

        {/* Year & Runtime */}
        <HStack spacing={3} marginBottom={3}>
          <Skeleton
            height="20px"
            width="50px"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="20px"
            width="10px"
            startColor={startColor}
            endColor={endColor}
          />
          <Skeleton
            height="20px"
            width="40px"
            startColor={startColor}
            endColor={endColor}
          />
        </HStack>

        {/* Genre */}
        <Skeleton
          height="20px"
          width="100px"
          marginBottom={4}
          startColor={startColor}
          endColor={endColor}
        />

        {/* Rating Circles */}
        <HStack spacing={4} marginBottom={5}>
          <Skeleton startColor={startColor} endColor={endColor}>
            <Circle size="60px" />
          </Skeleton>
          <Skeleton startColor={startColor} endColor={endColor}>
            <Circle size="60px" />
          </Skeleton>
          <Skeleton startColor={startColor} endColor={endColor}>
            <Circle size="60px" />
          </Skeleton>
        </HStack>

        {/* Movie Description */}
        <SkeletonText
          noOfLines={4}
          spacing={2}
          marginBottom={7}
          startColor={startColor}
          endColor={endColor}
        />

        {/* Details Section */}
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} marginY={8}>
          <Box>
            <Skeleton
              height="20px"
              width="80px"
              marginBottom={2}
              startColor={startColor}
              endColor={endColor}
            />
            <Skeleton
              height="20px"
              width="120px"
              marginBottom={5}
              startColor={startColor}
              endColor={endColor}
            />

            <Skeleton
              height="20px"
              width="80px"
              marginBottom={2}
              startColor={startColor}
              endColor={endColor}
            />
            <Skeleton
              height="20px"
              width="60px"
              marginBottom={5}
              startColor={startColor}
              endColor={endColor}
            />

            <Skeleton
              height="20px"
              width="80px"
              marginBottom={2}
              startColor={startColor}
              endColor={endColor}
            />
            <Skeleton
              height="20px"
              width="150px"
              marginBottom={5}
              startColor={startColor}
              endColor={endColor}
            />
          </Box>

          <Box>
            <Skeleton
              height="20px"
              width="80px"
              marginBottom={2}
              startColor={startColor}
              endColor={endColor}
            />
            <Skeleton
              height="20px"
              width="120px"
              marginBottom={5}
              startColor={startColor}
              endColor={endColor}
            />

            <Skeleton
              height="20px"
              width="80px"
              marginBottom={2}
              startColor={startColor}
              endColor={endColor}
            />
            <Skeleton
              height="20px"
              width="180px"
              marginBottom={5}
              startColor={startColor}
              endColor={endColor}
            />

            <Skeleton
              height="20px"
              width="80px"
              marginBottom={2}
              startColor={startColor}
              endColor={endColor}
            />
            <Skeleton
              height="20px"
              width="100px"
              startColor={startColor}
              endColor={endColor}
            />
          </Box>
        </SimpleGrid>

        {/* More Like This Section */}
        <Skeleton
          height="30px"
          width="40%"
          marginY={5}
          startColor={startColor}
          endColor={endColor}
        />
        <SimpleGrid columns={{ base: 3, md: 3, lg: 4 }} spacing={3} padding={1}>
          {[...Array(8)].map((_, i) => (
            <Skeleton
              key={i}
              height="200px"
              width="100%"
              startColor={startColor}
              endColor={endColor}
            />
          ))}
        </SimpleGrid>
      </GridItem>
    </SimpleGrid>
  );
};

export default React.memo(MovieSkeleton);
