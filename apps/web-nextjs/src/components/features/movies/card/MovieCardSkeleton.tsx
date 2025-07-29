import { Card, Skeleton, useColorModeValue } from "@chakra-ui/react";

const MovieCardSkeleton = () => {
  const startColor = useColorModeValue("gray.100", "gray.600");
  const endColor = useColorModeValue("gray.300", "gray.800");

  return (
    <Card>
      <Skeleton
        aspectRatio={2 / 3}
        borderRadius={5}
        startColor={startColor}
        endColor={endColor}
      />
    </Card>
  );
};

MovieCardSkeleton.displayName = "MovieCardSkeleton";

export default MovieCardSkeleton;
