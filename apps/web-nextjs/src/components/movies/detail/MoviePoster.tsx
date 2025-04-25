import React from "react";
import { Box, Image, Flex, Text } from "@chakra-ui/react";

interface MoviePosterProps {
  title: string;
  posterUrl: string | null;
}

const MoviePoster: React.FC<MoviePosterProps> = ({ title, posterUrl }) => {
  return (
    <Box flexShrink={0}>
      {posterUrl ? (
        <Image
          src={posterUrl}
          alt={title}
          borderRadius="md"
          width={300}
          height={450}
          objectFit="cover"
          fallback={
            <Flex
              bg="gray.700"
              width={300}
              height={450}
              align="center"
              justify="center"
              borderRadius="md"
            >
              <Text p={4} textAlign="center" fontWeight="bold">
                {title}
              </Text>
            </Flex>
          }
        />
      ) : (
        <Flex
          bg="gray.700"
          width={300}
          height={450}
          align="center"
          justify="center"
          borderRadius="md"
        >
          <Text p={4} textAlign="center" fontWeight="bold">
            {title}
          </Text>
        </Flex>
      )}
    </Box>
  );
};

export default MoviePoster;
