import React from "react";
import {
  Box,
  Heading,
  Text,
  Avatar,
  SimpleGrid,
  VStack,
  Center,
  Spinner,
} from "@chakra-ui/react";
import Link from "next/link";

interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path?: string;
  profile_url?: string;
}

interface MovieCastProps {
  cast?: CastMember[];
  isLoading: boolean;
  profileUrlFn: (path: string | null | undefined) => string | null;
}

const MovieCast: React.FC<MovieCastProps> = ({
  cast,
  isLoading,
  profileUrlFn,
}) => {
  return (
    <Box mb={8}>
      <Heading size="lg" mb={4}>
        Cast
      </Heading>
      {isLoading ? (
        <Center py={8}>
          <Spinner />
        </Center>
      ) : cast && cast.length > 0 ? (
        <SimpleGrid minChildWidth="120px" spacing={4}>
          {cast.slice(0, 12).map((person) => (
            <Link key={person.id} href={`/actors/${person.id}`} passHref>
              <VStack
                spacing={2}
                p={2}
                borderRadius="md"
                _hover={{ bg: "gray.700" }}
                cursor="pointer"
                align="center"
              >
                <Avatar
                  size="xl"
                  name={person.name}
                  src={
                    profileUrlFn(person.profile_path || person.profile_url) ||
                    undefined
                  }
                />
                <Text fontWeight="bold" textAlign="center" noOfLines={1}>
                  {person.name}
                </Text>
                <Text
                  fontSize="sm"
                  color="gray.400"
                  textAlign="center"
                  noOfLines={1}
                >
                  {person.character}
                </Text>
              </VStack>
            </Link>
          ))}
        </SimpleGrid>
      ) : (
        <Text color="gray.400">No cast information available.</Text>
      )}
    </Box>
  );
};

export default MovieCast;
