import { Badge } from "@chakra-ui/react";

interface CriticScoreProps {
  score: number;
}

export default function CriticScore({ score }: CriticScoreProps) {
  const color = score >= 75 ? "green" : score >= 60 ? "yellow" : "red";

  return (
    <Badge
      colorScheme={color}
      fontSize="14px"
      paddingX={2}
      borderRadius="4px"
      fontWeight="bold"
    >
      {score}
    </Badge>
  );
}
