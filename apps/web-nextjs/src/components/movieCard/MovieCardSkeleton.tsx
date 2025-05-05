import { Card, CardBody, Skeleton, SkeletonText } from "@chakra-ui/react";
import React from "react";

const MovieCardSkeleton = () => {
  return (
    <Card>
      <Skeleton aspectRatio={2 / 3} borderRadius={5} />
    </Card>
  );
};

export default MovieCardSkeleton;
