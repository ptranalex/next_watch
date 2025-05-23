import CriticScore from "./CriticScore";
import { HStack } from "@chakra-ui/react";
import type { RatingGroupProps } from "./types";

const RatingGroup = ({ movie, scale_up = 1 }: RatingGroupProps) => {
  return (
    <HStack marginBottom={3}>
      <CriticScore
        value={movie.imdb_rating}
        source="imdb"
        scale_up={scale_up}
      />
      <CriticScore
        value={movie.rotten_tomatoes_rating}
        source="rotten_tomatoes"
        scale_up={scale_up}
      />
      <CriticScore
        value={movie.metacritic_rating}
        source="metacritic"
        scale_up={scale_up}
      />
    </HStack>
  );
};

export default RatingGroup;
