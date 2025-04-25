import React, { useState } from "react";
import {
  Box,
  Heading,
  SimpleGrid,
  Spinner,
  Center,
  Text,
  Select,
  Flex,
  Button,
  Tabs,
  TabList,
  Tab,
  TabPanel,
  TabPanels,
} from "@chakra-ui/react";
import MovieCard from "./MovieCard";
import useTopMovies from "../../hooks/useTopMovies";

interface TopMoviesSectionProps {
  title?: string;
  initialYear?: number;
}

const getCurrentYear = () => new Date().getFullYear();

const TopMoviesSection: React.FC<TopMoviesSectionProps> = ({
  title = "Top Rated Movies",
  initialYear = getCurrentYear(),
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedYear, setSelectedYear] = useState(initialYear);

  // Fetch top movies data for the selected year
  const {
    data: yearTopMovies,
    isLoading: isLoadingYearTop,
    error: yearTopError,
  } = useTopMovies(selectedYear, false);

  // Fetch all-time top movies
  const {
    data: allTimeTopMovies,
    isLoading: isLoadingAllTime,
    error: allTimeError,
  } = useTopMovies(undefined, true);

  // Generate year options from current year going back 50 years
  const yearOptions = [];
  const currentYear = getCurrentYear();
  for (let year = currentYear; year >= currentYear - 50; year--) {
    yearOptions.push(year);
  }

  const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedYear(parseInt(e.target.value, 10));
  };

  const handleTabChange = (index: number) => {
    setActiveTab(index);
  };

  return (
    <Box mb={8}>
      <Heading size="lg" mb={4}>
        {title}
      </Heading>

      <Tabs variant="enclosed" index={activeTab} onChange={handleTabChange}>
        <TabList mb={4}>
          <Tab>By Year</Tab>
          <Tab>All Time</Tab>
        </TabList>

        <TabPanels>
          {/* Top Movies By Year */}
          <TabPanel p={0}>
            <Flex mb={4} align="center">
              <Text mr={2}>Year:</Text>
              <Select
                value={selectedYear}
                onChange={handleYearChange}
                width="auto"
              >
                {yearOptions.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </Select>
            </Flex>

            {isLoadingYearTop ? (
              <Center py={8}>
                <Spinner />
              </Center>
            ) : yearTopError ? (
              <Text color="red.500">
                Error loading top movies. Please try again.
              </Text>
            ) : yearTopMovies?.movies?.length ? (
              <SimpleGrid
                columns={{ base: 2, sm: 3, md: 4, lg: 5 }}
                spacing={4}
              >
                {yearTopMovies.movies.map((movie) => (
                  <Box key={movie.id}>
                    <MovieCard movie={movie} size="sm" />
                  </Box>
                ))}
              </SimpleGrid>
            ) : (
              <Text>No top movies found for {selectedYear}.</Text>
            )}
          </TabPanel>

          {/* All-Time Top Movies */}
          <TabPanel p={0}>
            {isLoadingAllTime ? (
              <Center py={8}>
                <Spinner />
              </Center>
            ) : allTimeError ? (
              <Text color="red.500">
                Error loading all-time top movies. Please try again.
              </Text>
            ) : allTimeTopMovies?.movies?.length ? (
              <SimpleGrid
                columns={{ base: 2, sm: 3, md: 4, lg: 5 }}
                spacing={4}
              >
                {allTimeTopMovies.movies.map((movie) => (
                  <Box key={movie.id}>
                    <MovieCard movie={movie} size="sm" />
                  </Box>
                ))}
              </SimpleGrid>
            ) : (
              <Text>No all-time top movies found.</Text>
            )}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default TopMoviesSection;
