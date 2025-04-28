"use client";

import {
  Box,
  Container,
  Heading,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
  Divider,
  VStack,
} from "@chakra-ui/react";
import MovieCard from "@/src/components/movies/MovieCard";
import TrailerCard from "@/src/components/movies/TrailerCard";
import MovieAttributes from "@/src/components/movies/MovieAttributes";
import ActorsGallery from "@/src/components/movies/ActorsGallery";
import CriticScore from "@/src/components/movies/CriticScore";
import ColorModeSwitch from "@/src/components/common/ColorModeSwitch";
import ScrollToTopButton from "@/src/components/common/ScrollToTopButton";

export default function DemoPage() {
  // Sample data for demonstration
  const sampleMovie = {
    id: "1",
    title: "The Matrix",
    poster_path: "https://via.placeholder.com/300x450?text=The+Matrix",
    vote_average: 8.7,
    release_date: "1999-03-31",
    genres: ["Action", "Sci-Fi"],
  };

  const sampleActors = [
    {
      id: "1",
      name: "Keanu Reeves",
      character: "Neo",
      profile_path: "https://via.placeholder.com/150x225?text=Keanu+Reeves",
    },
    {
      id: "2",
      name: "Laurence Fishburne",
      character: "Morpheus",
      profile_path:
        "https://via.placeholder.com/150x225?text=Laurence+Fishburne",
    },
    {
      id: "3",
      name: "Carrie-Anne Moss",
      character: "Trinity",
      profile_path: "https://via.placeholder.com/150x225?text=Carrie-Anne+Moss",
    },
    {
      id: "4",
      name: "Hugo Weaving",
      character: "Agent Smith",
      profile_path: "https://via.placeholder.com/150x225?text=Hugo+Weaving",
    },
  ];

  return (
    <Container maxW="container.xl" py={8}>
      <Box
        mb={8}
        display="flex"
        justifyContent="space-between"
        alignItems="center"
      >
        <Heading as="h1" size="xl">
          Component Demo
        </Heading>
        <ColorModeSwitch />
      </Box>

      <Tabs colorScheme="blue" isLazy>
        <TabList
          overflowX="auto"
          flexWrap="nowrap"
          sx={{ scrollbarWidth: "none" }}
        >
          <Tab>Movie Card</Tab>
          <Tab>Trailer Card</Tab>
          <Tab>Movie Attributes</Tab>
          <Tab>Actors Gallery</Tab>
          <Tab>Critic Score</Tab>
          <Tab>Utility Components</Tab>
        </TabList>

        <TabPanels>
          {/* Movie Card Demo */}
          <TabPanel>
            <Heading as="h2" size="lg" mb={4}>
              Movie Card
            </Heading>
            <Text mb={6}>
              The MovieCard component displays a movie with its poster, title,
              rating, and genres. It also supports interactive buttons for
              favorites, watchlist, and watched status.
            </Text>
            <Box maxW="250px">
              <MovieCard
                movie={sampleMovie}
                onFavoriteToggle={(id) =>
                  alert(`Toggle favorite for movie ${id}`)
                }
                onWatchlistToggle={(id) =>
                  alert(`Toggle watchlist for movie ${id}`)
                }
                onWatchedToggle={(id) =>
                  alert(`Toggle watched for movie ${id}`)
                }
              />
            </Box>
          </TabPanel>

          {/* Trailer Card Demo */}
          <TabPanel>
            <Heading as="h2" size="lg" mb={4}>
              Trailer Card
            </Heading>
            <Text mb={6}>
              The TrailerCard component displays a movie trailer with a
              thumbnail and play button. It supports both YouTube and Vimeo
              videos.
            </Text>
            <Box maxW="500px">
              <TrailerCard
                id="dQw4w9WgXcQ"
                title="The Matrix - Official Trailer"
                site="YouTube"
                publishedAt="2010-03-31"
                onClick={() =>
                  alert("Trailer clicked - could open a modal player")
                }
              />
            </Box>
          </TabPanel>

          {/* Movie Attributes Demo */}
          <TabPanel>
            <Heading as="h2" size="lg" mb={4}>
              Movie Attributes
            </Heading>
            <Text mb={6}>
              The MovieAttributes component displays key metadata about a movie
              in a visually appealing grid format.
            </Text>
            <MovieAttributes
              runtime={136}
              releaseDate="1999-03-31"
              language="English"
              countries={["United States"]}
              revenue={463517383}
              budget={63000000}
              voteCount={24075}
            />
          </TabPanel>

          {/* Actors Gallery Demo */}
          <TabPanel>
            <Heading as="h2" size="lg" mb={4}>
              Actors Gallery
            </Heading>
            <Text mb={6}>
              The ActorsGallery component displays a grid of actors with their
              photos, names, and character names.
            </Text>
            <ActorsGallery actors={sampleActors} title="Cast" />
          </TabPanel>

          {/* Critic Score Demo */}
          <TabPanel>
            <Heading as="h2" size="lg" mb={4}>
              Critic Score
            </Heading>
            <Text mb={6}>
              The CriticScore component displays a movie&apos;s rating with
              appropriate color coding based on the score.
            </Text>
            <VStack align="start" spacing={6}>
              <Card>
                <CardHeader>
                  <Heading size="md">Score Examples</Heading>
                </CardHeader>
                <CardBody>
                  <SimpleGrid columns={3} spacing={4}>
                    <Box>
                      <Text>High Rating (Green)</Text>
                      <CriticScore score={85} />
                    </Box>
                    <Box>
                      <Text>Medium Rating (Yellow)</Text>
                      <CriticScore score={65} />
                    </Box>
                    <Box>
                      <Text>Low Rating (Red)</Text>
                      <CriticScore score={45} />
                    </Box>
                  </SimpleGrid>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Utility Components Demo */}
          <TabPanel>
            <Heading as="h2" size="lg" mb={4}>
              Utility Components
            </Heading>
            <Text mb={6}>
              Various utility components that enhance the user experience.
            </Text>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
              <Card>
                <CardHeader>
                  <Heading size="md">Color Mode Switch</Heading>
                </CardHeader>
                <CardBody>
                  <Text mb={4}>
                    Allows users to toggle between light and dark mode.
                  </Text>
                  <ColorModeSwitch showLabel={true} />
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <Heading size="md">Scroll To Top Button</Heading>
                </CardHeader>
                <CardBody>
                  <Text mb={4}>
                    Button that appears when scrolling down and allows users to
                    quickly return to the top.
                  </Text>
                  <Text>
                    The ScrollToTopButton component is fixed at the bottom right
                    of the page. Scroll down to see it in action.
                  </Text>
                </CardBody>
              </Card>
            </SimpleGrid>
          </TabPanel>
        </TabPanels>
      </Tabs>

      <Divider my={10} />

      <Box textAlign="center" mb={10}>
        <Heading as="h2" size="lg" mb={4}>
          Migration Progress
        </Heading>
        <Text>
          These components are part of the migration from React.js to Next.js.
          See the MIGRATION_PLAN.md file for more details.
        </Text>
      </Box>

      {/* ScrollToTopButton is visible when scrolling down */}
      <ScrollToTopButton />
    </Container>
  );
}
