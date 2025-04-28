"use client";

import { useState, useEffect } from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  ModalFooter,
  Button,
  Stack,
  Divider,
  Heading,
  Checkbox,
  Select,
  RangeSlider,
  RangeSliderTrack,
  RangeSliderFilledTrack,
  RangeSliderThumb,
  FormControl,
  FormLabel,
  Text,
  HStack,
  Box,
  useColorModeValue,
} from "@chakra-ui/react";

export interface MovieFilterOptions {
  years: number[];
  genres: string[];
  minRating: number;
  maxRating: number;
  providers: string[];
  sortBy: string;
}

interface MovieFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialFilters: MovieFilterOptions;
  onApplyFilters: (filters: MovieFilterOptions) => void;
  availableGenres: string[];
  availableProviders: string[];
}

export default function MovieFilterModal({
  isOpen,
  onClose,
  initialFilters,
  onApplyFilters,
  availableGenres = [],
  availableProviders = [],
}: MovieFilterModalProps) {
  const [filters, setFilters] = useState<MovieFilterOptions>(initialFilters);
  const borderColor = useColorModeValue("gray.200", "gray.700");
  const bgColor = useColorModeValue("white", "gray.800");

  // Reset filters when modal opens
  useEffect(() => {
    if (isOpen) {
      setFilters(initialFilters);
    }
  }, [isOpen, initialFilters]);

  const handleApply = () => {
    onApplyFilters(filters);
    onClose();
  };

  const handleReset = () => {
    const resetFilters = {
      years: [1900, new Date().getFullYear()],
      genres: [],
      minRating: 0,
      maxRating: 10,
      providers: [],
      sortBy: "popularity.desc",
    };
    setFilters(resetFilters);
    onApplyFilters(resetFilters);
    onClose();
  };

  // Handle genre selection
  const toggleGenre = (genre: string) => {
    setFilters((prev) => ({
      ...prev,
      genres: prev.genres.includes(genre)
        ? prev.genres.filter((g) => g !== genre)
        : [...prev.genres, genre],
    }));
  };

  // Handle provider selection
  const toggleProvider = (provider: string) => {
    setFilters((prev) => ({
      ...prev,
      providers: prev.providers.includes(provider)
        ? prev.providers.filter((p) => p !== provider)
        : [...prev.providers, provider],
    }));
  };

  // Handle rating change
  const handleRatingChange = (values: number[]) => {
    setFilters((prev) => ({
      ...prev,
      minRating: values[0],
      maxRating: values[1],
    }));
  };

  // Handle sort change
  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters((prev) => ({
      ...prev,
      sortBy: e.target.value,
    }));
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Filter Movies</ModalHeader>
        <ModalCloseButton />

        <ModalBody>
          <Stack spacing={6}>
            {/* Year filter */}
            <Box>
              <Heading size="sm" mb={3}>
                Year Range
              </Heading>
              <RangeSlider
                min={1900}
                max={new Date().getFullYear()}
                step={1}
                defaultValue={[filters.years[0], filters.years[1]]}
                onChange={(values) =>
                  setFilters((prev) => ({ ...prev, years: values }))
                }
                colorScheme="blue"
              >
                <RangeSliderTrack>
                  <RangeSliderFilledTrack />
                </RangeSliderTrack>
                <RangeSliderThumb index={0} />
                <RangeSliderThumb index={1} />
              </RangeSlider>
              <HStack justifyContent="space-between" mt={1}>
                <Text fontSize="sm">{filters.years[0]}</Text>
                <Text fontSize="sm">{filters.years[1]}</Text>
              </HStack>
            </Box>

            <Divider />

            {/* Rating filter */}
            <Box>
              <Heading size="sm" mb={3}>
                Rating
              </Heading>
              <RangeSlider
                min={0}
                max={10}
                step={0.5}
                defaultValue={[filters.minRating, filters.maxRating]}
                onChange={handleRatingChange}
                colorScheme="blue"
              >
                <RangeSliderTrack>
                  <RangeSliderFilledTrack />
                </RangeSliderTrack>
                <RangeSliderThumb index={0} />
                <RangeSliderThumb index={1} />
              </RangeSlider>
              <HStack justifyContent="space-between" mt={1}>
                <Text fontSize="sm">{filters.minRating.toFixed(1)}</Text>
                <Text fontSize="sm">{filters.maxRating.toFixed(1)}</Text>
              </HStack>
            </Box>

            <Divider />

            {/* Genre filter */}
            <Box>
              <Heading size="sm" mb={3}>
                Genres
              </Heading>
              <Stack maxH="200px" overflowY="auto" spacing={2}>
                {availableGenres.map((genre) => (
                  <Checkbox
                    key={genre}
                    isChecked={filters.genres.includes(genre)}
                    onChange={() => toggleGenre(genre)}
                  >
                    {genre}
                  </Checkbox>
                ))}
              </Stack>
            </Box>

            <Divider />

            {/* Providers filter */}
            <Box>
              <Heading size="sm" mb={3}>
                Streaming Providers
              </Heading>
              <Stack maxH="200px" overflowY="auto" spacing={2}>
                {availableProviders.map((provider) => (
                  <Checkbox
                    key={provider}
                    isChecked={filters.providers.includes(provider)}
                    onChange={() => toggleProvider(provider)}
                  >
                    {provider}
                  </Checkbox>
                ))}
              </Stack>
            </Box>

            <Divider />

            {/* Sort options */}
            <FormControl>
              <FormLabel>Sort by</FormLabel>
              <Select
                value={filters.sortBy}
                onChange={handleSortChange}
                bg={bgColor}
                borderColor={borderColor}
              >
                <option value="popularity.desc">Popularity (Descending)</option>
                <option value="popularity.asc">Popularity (Ascending)</option>
                <option value="vote_average.desc">Rating (Descending)</option>
                <option value="vote_average.asc">Rating (Ascending)</option>
                <option value="release_date.desc">Release Date (Newest)</option>
                <option value="release_date.asc">Release Date (Oldest)</option>
                <option value="title.asc">Title (A-Z)</option>
                <option value="title.desc">Title (Z-A)</option>
              </Select>
            </FormControl>
          </Stack>
        </ModalBody>

        <ModalFooter>
          <Button variant="outline" mr={3} onClick={handleReset}>
            Reset All
          </Button>
          <Button colorScheme="blue" onClick={handleApply}>
            Apply Filters
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
