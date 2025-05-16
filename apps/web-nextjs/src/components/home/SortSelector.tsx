"use client";

import { useFilterParams } from "@/hooks/useUrlParams";
import {
  Box,
  Button,
  Flex,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Text,
} from "@chakra-ui/react";
import { useCallback } from "react";
import {
  FaChevronDown,
  FaSortAmountDown,
  FaSortAmountUp,
} from "react-icons/fa";

// Sorting params interface using Record type
type SortParams = Record<string, string | null> & {
  sort: string;
  order: string;
};

// Sort options
const sortOptions = [
  { value: "release_date", label: "Release Date" },
  { value: "title", label: "Title" },
  { value: "imdb_rating", label: "IMDb Rating" },
  { value: "rotten_tomatoes_rating", label: "Rotten Tomatoes" },
  { value: "metacritic_rating", label: "Metacritic" },
];

const SortSelector = () => {
  // Default sort values
  const defaultSortParams: SortParams = {
    sort: "release_date",
    order: "desc",
  };

  // Use the filter params hook
  const { filters, setFilters } = useFilterParams<SortParams>({
    defaults: defaultSortParams,
  });

  // Handle sort type change
  const handleSortChange = useCallback(
    (sortValue: string) => {
      setFilters({ sort: sortValue });
    },
    [setFilters]
  );

  // Handle sort direction change
  const toggleSortDirection = useCallback(() => {
    const newOrder = filters.order === "desc" ? "asc" : "desc";
    setFilters({ order: newOrder });
  }, [filters.order, setFilters]);

  // Get current sort label
  const currentSortLabel =
    sortOptions.find((option) => option.value === filters.sort)?.label ||
    "Release Date";

  return (
    <Flex alignItems="center" mb={4}>
      <Text mr={2} fontWeight="medium">
        Sort by:
      </Text>
      <Menu>
        <MenuButton
          as={Button}
          rightIcon={<FaChevronDown />}
          size="sm"
          variant="outline"
        >
          {currentSortLabel}
        </MenuButton>
        <MenuList>
          {sortOptions.map((option) => (
            <MenuItem
              key={option.value}
              onClick={() => handleSortChange(option.value)}
              fontWeight={filters.sort === option.value ? "bold" : "normal"}
            >
              {option.label}
            </MenuItem>
          ))}
        </MenuList>
      </Menu>

      <Button
        ml={2}
        size="sm"
        variant="ghost"
        onClick={toggleSortDirection}
        aria-label={`Sort ${
          filters.order === "desc" ? "descending" : "ascending"
        }`}
      >
        {filters.order === "desc" ? <FaSortAmountDown /> : <FaSortAmountUp />}
      </Button>
    </Flex>
  );
};

export default SortSelector;
