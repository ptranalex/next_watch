import React from "react";
import { Box, Heading, Text, HStack, Icon } from "@chakra-ui/react";
import { CalendarIcon } from "@chakra-ui/icons";

interface MovieHeroProps {
  title: string;
  backdropUrl: string | null;
  releaseYear: number | null;
}

const MovieHero: React.FC<MovieHeroProps> = ({
  title,
  backdropUrl,
  releaseYear,
}) => {
  if (!backdropUrl) {
    return null;
  }

  return (
    <Box position="relative" height={{ base: "200px", md: "400px" }} mb={6}>
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        bottom={0}
        backgroundImage={`url(${backdropUrl})`}
        backgroundSize="cover"
        backgroundPosition="center"
        _after={{
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          bg: "rgba(0,0,0,0.6)",
        }}
      />
      <Box
        position="absolute"
        bottom={0}
        left={0}
        right={0}
        p={6}
        bg="linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0))"
      >
        <Heading color="white">{title}</Heading>
        {releaseYear && (
          <HStack spacing={2} color="gray.300" mt={2}>
            <Icon as={CalendarIcon} />
            <Text>{releaseYear}</Text>
          </HStack>
        )}
      </Box>
    </Box>
  );
};

export default MovieHero;
