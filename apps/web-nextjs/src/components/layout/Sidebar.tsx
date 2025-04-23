import React from "react";
import {
  Box,
  VStack,
  Heading,
  List,
  ListItem,
  Text,
  Divider,
} from "@chakra-ui/react";
import Link from "next/link";
import { useRouter } from "next/router";

// For now, we'll use a static list of genres
// Later we can fetch this from the API
const GENRES = [
  { id: 28, name: "Action" },
  { id: 12, name: "Adventure" },
  { id: 16, name: "Animation" },
  { id: 35, name: "Comedy" },
  { id: 80, name: "Crime" },
  { id: 18, name: "Drama" },
  { id: 14, name: "Fantasy" },
  { id: 27, name: "Horror" },
  { id: 9648, name: "Mystery" },
  { id: 10749, name: "Romance" },
  { id: 878, name: "Science Fiction" },
  { id: 53, name: "Thriller" },
];

const Sidebar: React.FC = () => {
  const router = useRouter();

  return (
    <Box
      as="aside"
      w="240px"
      bg="gray.800"
      h="calc(100vh - 64px)"
      position="sticky"
      top="64px"
      display={{ base: "none", lg: "block" }}
      px={4}
      py={6}
      overflowY="auto"
    >
      <VStack align="start" spacing={6}>
        <Box>
          <Heading size="md" mb={3}>
            Categories
          </Heading>
          <List spacing={2}>
            <ListItem>
              <Link href="/" passHref>
                <Text
                  fontWeight={router.pathname === "/" ? "bold" : "normal"}
                  color={router.pathname === "/" ? "blue.300" : "gray.300"}
                  cursor="pointer"
                  _hover={{ color: "blue.300" }}
                >
                  Popular
                </Text>
              </Link>
            </ListItem>
            <ListItem>
              <Link href="/top-rated" passHref>
                <Text
                  fontWeight={
                    router.pathname === "/top-rated" ? "bold" : "normal"
                  }
                  color={
                    router.pathname === "/top-rated" ? "blue.300" : "gray.300"
                  }
                  cursor="pointer"
                  _hover={{ color: "blue.300" }}
                >
                  Top Rated
                </Text>
              </Link>
            </ListItem>
            <ListItem>
              <Link href="/upcoming" passHref>
                <Text
                  fontWeight={
                    router.pathname === "/upcoming" ? "bold" : "normal"
                  }
                  color={
                    router.pathname === "/upcoming" ? "blue.300" : "gray.300"
                  }
                  cursor="pointer"
                  _hover={{ color: "blue.300" }}
                >
                  Upcoming
                </Text>
              </Link>
            </ListItem>
          </List>
        </Box>

        <Divider />

        <Box w="100%">
          <Heading size="md" mb={3}>
            Genres
          </Heading>
          <List spacing={2}>
            {GENRES.map((genre) => (
              <ListItem key={genre.id}>
                <Link href={`/genre/${genre.name.toLowerCase()}`} passHref>
                  <Text
                    fontWeight={
                      router.asPath === `/genre/${genre.name.toLowerCase()}`
                        ? "bold"
                        : "normal"
                    }
                    color={
                      router.asPath === `/genre/${genre.name.toLowerCase()}`
                        ? "blue.300"
                        : "gray.300"
                    }
                    cursor="pointer"
                    _hover={{ color: "blue.300" }}
                  >
                    {genre.name}
                  </Text>
                </Link>
              </ListItem>
            ))}
          </List>
        </Box>
      </VStack>
    </Box>
  );
};

export default Sidebar;
