import {
  Box,
  Skeleton,
  SkeletonText,
  useColorModeValue,
} from "@chakra-ui/react";

export default function MovieCardSkeleton() {
  const cardBg = useColorModeValue("white", "gray.800");
  const cardBorder = useColorModeValue("gray.200", "gray.700");

  return (
    <Box
      borderRadius="lg"
      overflow="hidden"
      bg={cardBg}
      borderWidth="1px"
      borderColor={cardBorder}
    >
      {/* Poster skeleton */}
      <Skeleton height="300px" width="100%" />

      {/* Title and metadata skeleton */}
      <Box p={3}>
        <SkeletonText mt={1} noOfLines={1} spacing={4} skeletonHeight={4} />
        <SkeletonText mt={2} noOfLines={1} spacing={4} skeletonHeight={2} />
      </Box>
    </Box>
  );
}
