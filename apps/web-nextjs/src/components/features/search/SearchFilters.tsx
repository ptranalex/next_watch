"use client";

import React, { useCallback } from "react";
import {
  Box,
  Button,
  HStack,
  VStack,
  Select,
  Text,
  Collapse,
  useColorModeValue,
  Badge,
  Wrap,
  WrapItem,
} from "@chakra-ui/react";
import { HiOutlineAdjustmentsHorizontal, HiXMark } from "react-icons/hi2";

interface SearchFiltersProps {
  genreId?: number;
  year?: number;
  sortBy: string;
  sortDesc: boolean;
  showFilters: boolean;
  onToggleFilters: () => void;
  onFiltersChange: (filters: {
    genreId?: number;
    year?: number;
    sortBy?: string;
    sortDesc?: boolean;
  }) => void;
  onClearFilters: () => void;
  isMobile?: boolean;
}

// Common movie years for filtering
const MOVIE_YEARS = Array.from(
  { length: 30 },
  (_, i) => new Date().getFullYear() - i
);

// Sort options for movies
const SORT_OPTIONS = [
  { value: "title", label: "Title" },
  { value: "release_date", label: "Release Date" },
  { value: "imdb_rating", label: "IMDb Rating" },
  { value: "rotten_tomatoes_rating", label: "Rotten Tomatoes" },
  { value: "metacritic_rating", label: "Metacritic Score" },
];

/**
 * SearchFilters - Advanced filtering component for search results
 *
 * Provides filtering options for:
 * - Genre selection
 * - Release year
 * - Sort criteria and direction
 * - Responsive layout for mobile and desktop
 */
export function SearchFilters({
  genreId,
  year,
  sortBy,
  sortDesc,
  showFilters,
  onToggleFilters,
  onFiltersChange,
  onClearFilters,
  isMobile = false,
}: SearchFiltersProps): React.JSX.Element {
  const bgColor = useColorModeValue("bg.secondary", "bg.secondary");
  const borderColor = useColorModeValue("border.subtle", "border.subtle");

  // Handle individual filter changes
  const handleGenreChange = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      const value = event.target.value;
      onFiltersChange({
        genreId: value ? parseInt(value) : undefined,
        year,
        sortBy,
        sortDesc,
      });
    },
    [year, sortBy, sortDesc, onFiltersChange]
  );

  const handleYearChange = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      const value = event.target.value;
      onFiltersChange({
        genreId,
        year: value ? parseInt(value) : undefined,
        sortBy,
        sortDesc,
      });
    },
    [genreId, sortBy, sortDesc, onFiltersChange]
  );

  const handleSortChange = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      onFiltersChange({
        genreId,
        year,
        sortBy: event.target.value,
        sortDesc,
      });
    },
    [genreId, year, sortDesc, onFiltersChange]
  );

  const handleSortDirectionToggle = useCallback(() => {
    onFiltersChange({
      genreId,
      year,
      sortBy,
      sortDesc: !sortDesc,
    });
  }, [genreId, year, sortBy, sortDesc, onFiltersChange]);

  // Count active filters
  const activeFilterCount = [genreId, year].filter(Boolean).length;
  const hasActiveFilters = activeFilterCount > 0;

  return (
    <Box>
      {/* Filter Toggle Button */}
      <HStack justify="space-between" align="center" mb={4}>
        <Button
          leftIcon={<HiOutlineAdjustmentsHorizontal />}
          onClick={onToggleFilters}
          variant="outline"
          size={isMobile ? "sm" : "md"}
        >
          Filters
          {hasActiveFilters && (
            <Badge ml={2} colorScheme="blue" variant="solid">
              {activeFilterCount}
            </Badge>
          )}
        </Button>

        {hasActiveFilters && (
          <Button
            size="sm"
            variant="ghost"
            colorScheme="red"
            onClick={onClearFilters}
            leftIcon={<HiXMark />}
          >
            Clear All
          </Button>
        )}
      </HStack>

      {/* Filters Panel */}
      <Collapse in={showFilters} animateOpacity>
        <Box
          p={4}
          bg={bgColor}
          borderRadius="lg"
          border="1px"
          borderColor={borderColor}
        >
          <VStack spacing={4} align="stretch">
            {/* Active Filters Display */}
            {hasActiveFilters && (
              <Box>
                <Text fontSize="sm" color="text.secondary" mb={2}>
                  Active Filters:
                </Text>
                <Wrap spacing={2}>
                  {year && (
                    <WrapItem>
                      <Badge colorScheme="blue" variant="subtle">
                        Year: {year}
                      </Badge>
                    </WrapItem>
                  )}
                  {genreId && (
                    <WrapItem>
                      <Badge colorScheme="blue" variant="subtle">
                        Genre ID: {genreId}
                      </Badge>
                    </WrapItem>
                  )}
                </Wrap>
              </Box>
            )}

            {/* Filter Controls */}
            <VStack spacing={4} align="stretch">
              {/* Year Filter */}
              <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                  Release Year
                </Text>
                <Select
                  placeholder="Any year"
                  value={year || ""}
                  onChange={handleYearChange}
                  size={isMobile ? "sm" : "md"}
                >
                  {MOVIE_YEARS.map((movieYear) => (
                    <option key={movieYear} value={movieYear}>
                      {movieYear}
                    </option>
                  ))}
                </Select>
              </Box>

              {/* Genre Filter - Placeholder for now */}
              <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                  Genre
                </Text>
                <Select
                  placeholder="Any genre"
                  value={genreId || ""}
                  onChange={handleGenreChange}
                  size={isMobile ? "sm" : "md"}
                >
                  <option value="28">Action</option>
                  <option value="12">Adventure</option>
                  <option value="16">Animation</option>
                  <option value="35">Comedy</option>
                  <option value="80">Crime</option>
                  <option value="18">Drama</option>
                  <option value="14">Fantasy</option>
                  <option value="27">Horror</option>
                  <option value="9648">Mystery</option>
                  <option value="10749">Romance</option>
                  <option value="878">Science Fiction</option>
                  <option value="53">Thriller</option>
                </Select>
              </Box>

              {/* Sort Options */}
              <HStack spacing={4} align="end">
                <Box flex="1">
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Sort By
                  </Text>
                  <Select
                    value={sortBy}
                    onChange={handleSortChange}
                    size={isMobile ? "sm" : "md"}
                  >
                    {SORT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </Box>

                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Order
                  </Text>
                  <Button
                    onClick={handleSortDirectionToggle}
                    variant="outline"
                    size={isMobile ? "sm" : "md"}
                    minW="90px"
                  >
                    {sortDesc ? "Desc" : "Asc"}
                  </Button>
                </Box>
              </HStack>
            </VStack>
          </VStack>
        </Box>
      </Collapse>
    </Box>
  );
}
