import React from "react";
import {
  Skeleton,
  SkeletonText,
  SimpleGrid,
  Box,
  VStack,
  HStack,
  useColorModeValue,
} from "@chakra-ui/react";

interface SkeletonLoaderProps {
  type: "card" | "list" | "details" | "filter";
  count?: number;
}

/**
 * SkeletonLoader component
 * Provides content-specific skeleton loading states for mobile UX
 * Displays placeholder UI while content is being loaded
 */
const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ type, count = 6 }) => {
  const bgColor = useColorModeValue("gray.100", "gray.700");

  const renderCardSkeleton = () => (
    <SimpleGrid columns={{ base: 2, sm: 3, md: 4, lg: 6 }} spacing={4}>
      {Array(count)
        .fill(0)
        .map((_, i) => (
          <Box key={i}>
            <Skeleton
              height={{ base: "180px", md: "200px" }}
              borderRadius="md"
              mb={2}
            />
            <SkeletonText noOfLines={2} spacing={2} />
          </Box>
        ))}
    </SimpleGrid>
  );

  const renderListSkeleton = () => (
    <VStack spacing={4} width="100%">
      {Array(count)
        .fill(0)
        .map((_, i) => (
          <HStack
            key={i}
            width="100%"
            p={4}
            borderWidth="1px"
            borderRadius="md"
          >
            <Skeleton height="90px" width="60px" borderRadius="md" />
            <VStack align="start" spacing={2} flex={1}>
              <Skeleton height="20px" width="70%" />
              <Skeleton height="16px" width="40%" />
              <Skeleton height="16px" width="90%" />
            </VStack>
          </HStack>
        ))}
    </VStack>
  );

  const renderDetailsSkeleton = () => (
    <VStack spacing={6} width="100%" align="start">
      <Skeleton height="32px" width="60%" />
      <HStack width="100%" spacing={4} align="start">
        <Skeleton height="260px" width="180px" borderRadius="md" />
        <VStack align="start" spacing={4} flex={1}>
          <SkeletonText noOfLines={4} spacing={4} width="100%" />
          <HStack spacing={4} width="100%">
            <Skeleton height="32px" width="50px" borderRadius="full" />
            <Skeleton height="32px" width="80px" borderRadius="full" />
            <Skeleton height="32px" width="60px" borderRadius="full" />
          </HStack>
        </VStack>
      </HStack>
      <SkeletonText noOfLines={6} spacing={4} width="100%" />
    </VStack>
  );

  const renderFilterSkeleton = () => (
    <VStack spacing={4} width="100%" p={4} bg={bgColor} borderRadius="md">
      <Skeleton height="24px" width="50%" alignSelf="flex-start" />
      <Skeleton height="40px" width="100%" borderRadius="md" />
      <Skeleton height="40px" width="100%" borderRadius="md" />
      <Skeleton height="24px" width="40%" alignSelf="flex-start" />
      <HStack width="100%" spacing={2}>
        <Skeleton height="32px" width="20%" borderRadius="full" />
        <Skeleton height="32px" width="25%" borderRadius="full" />
        <Skeleton height="32px" width="28%" borderRadius="full" />
      </HStack>
    </VStack>
  );

  switch (type) {
    case "card":
      return renderCardSkeleton();
    case "list":
      return renderListSkeleton();
    case "details":
      return renderDetailsSkeleton();
    case "filter":
      return renderFilterSkeleton();
    default:
      return renderCardSkeleton();
  }
};

export default SkeletonLoader;
