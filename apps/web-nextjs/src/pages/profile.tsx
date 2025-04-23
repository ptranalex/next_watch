import React from "react";
import {
  Box,
  VStack,
  Heading,
  Text,
  Avatar,
  Badge,
  Button,
  Flex,
  Grid,
  GridItem,
  Divider,
  useColorModeValue,
} from "@chakra-ui/react";
import Head from "next/head";
import { GetServerSideProps, NextPage } from "next";
import { StarIcon } from "@chakra-ui/icons";

// Mock user data for initial implementation
const mockUser = {
  id: 1,
  name: "Alex",
  email: "alex@example.com",
  avatarUrl: "https://i.pravatar.cc/300",
  joinDate: "2023-01-15",
  watchlist: [
    { id: 1, title: "The Shawshank Redemption", rating: 9.3 },
    { id: 2, title: "The Godfather", rating: 9.2 },
    { id: 3, title: "The Dark Knight", rating: 9.0 },
  ],
  recentlyViewed: [
    { id: 4, title: "Pulp Fiction", rating: 8.9 },
    { id: 5, title: "The Lord of the Rings", rating: 8.8 },
  ],
};

interface ProfilePageProps {
  user: typeof mockUser;
}

const ProfilePage: NextPage<ProfilePageProps> = ({ user }) => {
  const cardBg = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  return (
    <>
      <Head>
        <title>My Profile | Next Watch</title>
        <meta
          name="description"
          content="Your Next Watch profile and watchlist"
        />
      </Head>

      <Box p={4}>
        <Grid templateColumns={{ base: "1fr", md: "300px 1fr" }} gap={8}>
          {/* User Profile Card */}
          <GridItem>
            <Box
              bg={cardBg}
              borderRadius="lg"
              overflow="hidden"
              boxShadow="md"
              p={6}
            >
              <VStack spacing={4} align="center">
                <Avatar
                  size="2xl"
                  src={user.avatarUrl}
                  name={user.name}
                  mb={2}
                />
                <Heading as="h2" size="lg">
                  {user.name}
                </Heading>
                <Text color="gray.500">{user.email}</Text>
                <Badge colorScheme="blue">
                  Member since {new Date(user.joinDate).getFullYear()}
                </Badge>
                <Button colorScheme="blue" width="full">
                  Edit Profile
                </Button>
              </VStack>
            </Box>
          </GridItem>

          {/* User Activity Section */}
          <GridItem>
            <VStack spacing={6} align="stretch">
              {/* Watchlist */}
              <Box>
                <Flex justify="space-between" align="center" mb={4}>
                  <Heading as="h3" size="md">
                    My Watchlist
                  </Heading>
                  <Button size="sm" variant="outline">
                    View All
                  </Button>
                </Flex>
                <VStack
                  spacing={3}
                  align="stretch"
                  bg={cardBg}
                  borderRadius="lg"
                  p={4}
                  border="1px"
                  borderColor={borderColor}
                >
                  {user.watchlist.map((movie) => (
                    <Flex key={movie.id} justify="space-between" align="center">
                      <Text fontWeight="medium">{movie.title}</Text>
                      <Flex align="center">
                        <StarIcon color="yellow.400" mr={1} />
                        <Text>{movie.rating}</Text>
                      </Flex>
                    </Flex>
                  ))}
                </VStack>
              </Box>

              <Divider />

              {/* Recently Viewed */}
              <Box>
                <Flex justify="space-between" align="center" mb={4}>
                  <Heading as="h3" size="md">
                    Recently Viewed
                  </Heading>
                </Flex>
                <VStack
                  spacing={3}
                  align="stretch"
                  bg={cardBg}
                  borderRadius="lg"
                  p={4}
                  border="1px"
                  borderColor={borderColor}
                >
                  {user.recentlyViewed.map((movie) => (
                    <Flex key={movie.id} justify="space-between" align="center">
                      <Text fontWeight="medium">{movie.title}</Text>
                      <Flex align="center">
                        <StarIcon color="yellow.400" mr={1} />
                        <Text>{movie.rating}</Text>
                      </Flex>
                    </Flex>
                  ))}
                </VStack>
              </Box>
            </VStack>
          </GridItem>
        </Grid>
      </Box>
    </>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  // In a real app, this would fetch the user's data from an API
  // based on their authentication status

  return {
    props: {
      user: mockUser,
    },
  };
};

export default ProfilePage;
