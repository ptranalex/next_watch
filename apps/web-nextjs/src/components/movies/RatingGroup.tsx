"use client";

import {
  HStack,
  VStack,
  Text,
  Image,
  Tooltip,
  Box,
  useColorModeValue,
} from "@chakra-ui/react";
import CriticScore from "./CriticScore";

interface Rating {
  source: string;
  value: number;
  maxValue: number;
  logo?: string;
}

interface RatingGroupProps {
  ratings: Rating[];
  size?: "sm" | "md" | "lg";
  orientation?: "horizontal" | "vertical";
}

export default function RatingGroup({
  ratings,
  size = "md",
  orientation = "horizontal",
}: RatingGroupProps) {
  const Container = orientation === "horizontal" ? HStack : VStack;
  const bgColor = useColorModeValue("gray.50", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  if (!ratings || ratings.length === 0) {
    return null;
  }

  // Size variants
  const getSizeVariant = () => {
    switch (size) {
      case "sm":
        return {
          logoSize: "20px",
          fontSize: "xs",
          spacing: 2,
          padding: 2,
        };
      case "lg":
        return {
          logoSize: "32px",
          fontSize: "md",
          spacing: 4,
          padding: 4,
        };
      case "md":
      default:
        return {
          logoSize: "24px",
          fontSize: "sm",
          spacing: 3,
          padding: 3,
        };
    }
  };

  const sizeVariant = getSizeVariant();

  // Format the rating score based on its type
  const formatRatingValue = (rating: Rating): string => {
    // IMDB-style (out of 10)
    if (rating.maxValue === 10) {
      return rating.value.toFixed(1);
    }

    // Percentage style (out of 100)
    if (rating.maxValue === 100) {
      return `${Math.round(rating.value)}%`;
    }

    // Default format
    return `${rating.value}/${rating.maxValue}`;
  };

  // Convert any rating to 0-100 scale for the CriticScore component
  const normalizeScore = (rating: Rating): number => {
    return (rating.value / rating.maxValue) * 100;
  };

  return (
    <Container spacing={4} align="center">
      {ratings.map((rating, index) => (
        <Tooltip key={index} label={`${rating.source} Rating`}>
          <Box
            borderRadius="md"
            p={sizeVariant.padding}
            bg={bgColor}
            borderWidth="1px"
            borderColor={borderColor}
          >
            <HStack spacing={sizeVariant.spacing}>
              {rating.logo && (
                <Image
                  src={rating.logo}
                  alt={rating.source}
                  boxSize={sizeVariant.logoSize}
                  objectFit="contain"
                />
              )}

              <VStack spacing={1} align="start">
                <Text
                  fontSize={sizeVariant.fontSize}
                  fontWeight="medium"
                  color="gray.500"
                >
                  {rating.source}
                </Text>

                <HStack spacing={2} align="center">
                  <CriticScore score={normalizeScore(rating)} />
                  <Text fontWeight="bold" fontSize={sizeVariant.fontSize}>
                    {formatRatingValue(rating)}
                  </Text>
                </HStack>
              </VStack>
            </HStack>
          </Box>
        </Tooltip>
      ))}
    </Container>
  );
}
