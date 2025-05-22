import { Card, Skeleton } from "@chakra-ui/react";

const MovieCardSkeleton = () => {
  return (
    <Card>
      <Skeleton aspectRatio={2 / 3} borderRadius={5} />
    </Card>
  );
};

export default MovieCardSkeleton;
