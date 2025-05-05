import { HStack } from "@chakra-ui/react";
import CriticScore from "./CriticScore";

interface Props {
  movie: {
    imdb_rating?: number | null;
    rotten_tomatoes_rating?: number | null;
    metacritic_rating?: number | null;
  };
  scale_up?: number;
}

const RatingGroup = ({ movie, scale_up = 1 }: Props) => {
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
