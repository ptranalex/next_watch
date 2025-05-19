"use client";

import { useAllGenres } from "@/hooks";
import {
  Tag,
  Button,
  VStack,
  Box,
  Text,
  useColorModeValue,
  SimpleGrid,
  Flex,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { FC, useCallback } from "react";
import { createLogger } from "@/utils/logging";
import { Genre } from "@/domain/entities";

const logger = createLogger("MobileGenreSection");

interface MobileGenreSectionProps {
  /**
   * Layout style for genres
   * - 'vertical': List of full-width buttons (best for limited genres)
   * - 'grid': Grid of square buttons (best for many genres)
   * - 'chips': Horizontal scrolling row of tag-like chips
   */
  layout?: "vertical" | "grid" | "chips";
  /**
   * Maximum number of genres to display before "See More" (for chips layout)
   */
  maxDisplayed?: number;
  /**
   * Custom onClose handler for the drawer (optional)
   */
  onClose?: () => void;
}

const MobileGenreSection: FC<MobileGenreSectionProps> = ({
  layout = "vertical",
  maxDisplayed = 12,
  onClose,
}) => {
  const { genres, isLoading, error } = useAllGenres();
  const router = useRouter();
  const bgColor = useColorModeValue("gray.100", "gray.700");
  const activeBgColor = useColorModeValue("blue.100", "blue.700");

  const handleGenreClick = useCallback(
    (genreId: number) => {
      logger.info(`Navigating to genre ${genreId}`);
      router.push(`/genres/${genreId}`);
      // Close the drawer if onClose is provided
      if (onClose) onClose();
    },
    [router, onClose]
  );

  if (isLoading) {
    return (
      <VStack spacing={2} align="stretch">
        <Text>Loading genres...</Text>
      </VStack>
    );
  }

  if (error) {
    return (
      <VStack spacing={2} align="stretch">
        <Text color="red.400">Error loading genres</Text>
      </VStack>
    );
  }

  if (!genres || genres.length === 0) {
    return (
      <VStack spacing={2} align="stretch">
        <Text>No genres available</Text>
      </VStack>
    );
  }

  // Vertical list layout - full width buttons
  if (layout === "vertical") {
    return (
      <VStack spacing={2} align="stretch">
        {genres.map((genre: Genre) => (
          <Button
            key={genre.id}
            size="md"
            variant="outline"
            width="100%"
            justifyContent="flex-start"
            onClick={() => handleGenreClick(genre.id)}
            px={4}
            py={2}
          >
            {genre.name}
          </Button>
        ))}
      </VStack>
    );
  }

  // Grid layout - compact square buttons
  if (layout === "grid") {
    return (
      <SimpleGrid columns={2} spacing={2}>
        {genres.map((genre: Genre) => (
          <Button
            key={genre.id}
            size="md"
            height="60px"
            variant="outline"
            onClick={() => handleGenreClick(genre.id)}
            whiteSpace="normal"
            textAlign="center"
          >
            {genre.name}
          </Button>
        ))}
      </SimpleGrid>
    );
  }

  // Horizontal scrolling chips
  return (
    <Box width="100%">
      <Flex flexWrap="wrap" gap={2}>
        {genres.map((genre: Genre) => (
          <Tag
            key={genre.id}
            size="lg"
            variant="solid"
            colorScheme="blue"
            borderRadius="full"
            cursor="pointer"
            py={2}
            px={4}
            onClick={() => handleGenreClick(genre.id)}
          >
            {genre.name}
          </Tag>
        ))}
      </Flex>
    </Box>
  );
};

export default MobileGenreSection;
