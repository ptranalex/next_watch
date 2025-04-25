import React, { useEffect, useState } from "react";
import {
  Box,
  VStack,
  Heading,
  List,
  ListItem,
  Text,
  Divider,
  Spinner,
} from "@chakra-ui/react";
import Link from "next/link";
import { useRouter } from "next/router";
import { Genre, getGenres } from "../../services/movie-service";

// Removed static GENRES array

const Sidebar: React.FC = () => {
  const router = useRouter();
  const [genres, setGenres] = useState<Genre[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const genresData = await getGenres();
        setGenres(genresData);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch genres:", err);
        setError("Failed to load genres");
        setLoading(false);
      }
    };

    fetchGenres();
  }, []);

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
          {loading ? (
            <Box textAlign="center" py={4}>
              <Spinner color="blue.300" size="sm" />
            </Box>
          ) : error ? (
            <Text color="red.300" fontSize="sm">
              {error}
            </Text>
          ) : (
            <List spacing={2}>
              {genres.map((genre) => (
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
          )}
        </Box>
      </VStack>
    </Box>
  );
};

export default Sidebar;
