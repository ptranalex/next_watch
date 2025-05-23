import React from "react";
import { Button, Menu, MenuButton, MenuItem, MenuList } from "@chakra-ui/react";
import { BsChevronDown } from "react-icons/bs";
import useMovieFilterStore from "@/store/movieFilterStore";
import type { SortSelectorProps } from "./types";

/**
 * Movie-specific sort value type
 */
type MovieSortValue =
  | "title"
  | "release_date"
  | "imdb_rating"
  | "rotten_tomatoes_rating"
  | "metacritic_rating"
  | "vote_count";

/**
 * MovieSortSelectorProps
 *
 * Extends the shared SortSelectorProps with movie-specific functionality
 */
interface MovieSortSelectorProps
  extends Omit<
    SortSelectorProps<MovieSortValue>,
    "options" | "value" | "onChange"
  > {
  currentSortOrder?: string;
  currentSortDesc?: boolean;
  onSortChange: (value: MovieSortValue, desc: boolean) => void;
}

/**
 * Default movie sort options
 */
const defaultMovieSortOptions = [
  { value: "title" as const, label: "Name", desc: false },
  { value: "release_date" as const, label: "Release date", desc: true },
  { value: "imdb_rating" as const, label: "IMDB rating", desc: true },
  { value: "imdb_rating" as const, label: "IMDB rating (Asc)", desc: false },
  {
    value: "rotten_tomatoes_rating" as const,
    label: "Rotten Tomatoes rating",
    desc: true,
  },
  {
    value: "metacritic_rating" as const,
    label: "Metacritic rating",
    desc: true,
  },
  { value: "vote_count" as const, label: "Popularity", desc: true },
];

/**
 * MovieSortSelector - Movie-specific implementation of SortSelector
 *
 * @param currentSortOrder - Current sort field
 * @param currentSortDesc - Whether sorting in descending order
 * @param onSortChange - Callback when sort selection changes
 * @param size - Size variant from ComponentSize
 * @param placeholder - Placeholder text
 */
const MovieSortSelector: React.FC<MovieSortSelectorProps> = ({
  currentSortOrder = "release_date",
  currentSortDesc = true,
  onSortChange,
  size = "md",
  placeholder = "Order by",
}) => {
  // Find the current sort order for display
  const currentOption = defaultMovieSortOptions.find(
    (option) =>
      option.value === currentSortOrder && option.desc === currentSortDesc
  );

  return (
    <Menu>
      <MenuButton
        as={Button}
        rightIcon={<BsChevronDown />}
        bg="bg.secondary"
        color="text.primary"
        _hover={{ bg: "bg.tertiary" }}
        _active={{ bg: "bg.tertiary" }}
        size={size}
      >
        {placeholder}: {currentOption?.label || "Release date"}
      </MenuButton>
      <MenuList bg="bg.secondary" borderColor="text.tertiary">
        {defaultMovieSortOptions.map((option) => (
          <MenuItem
            onClick={() => {
              onSortChange(option.value, option.desc ?? true);
            }}
            key={`${option.value}-${option.desc ? "desc" : "asc"}`}
            _hover={{ bg: "bg.tertiary" }}
            _focus={{ bg: "bg.tertiary" }}
          >
            {option.label}
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
};

/**
 * Generic SortSelector component using shared types
 */
const SortSelector = <T extends string = string>({
  options,
  value,
  onChange,
  size = "md",
  placeholder = "Sort by",
}: SortSelectorProps<T>): React.ReactElement => {
  const currentOption = options.find((option) => option.value === value);

  return (
    <Menu>
      <MenuButton
        as={Button}
        rightIcon={<BsChevronDown />}
        bg="bg.secondary"
        color="text.primary"
        _hover={{ bg: "bg.tertiary" }}
        _active={{ bg: "bg.tertiary" }}
        size={size}
      >
        {placeholder}: {currentOption?.label || "Select"}
      </MenuButton>
      <MenuList bg="bg.secondary" borderColor="text.tertiary">
        {options.map((option) => (
          <MenuItem
            onClick={() => onChange(option.value)}
            key={option.value}
            _hover={{ bg: "bg.tertiary" }}
            _focus={{ bg: "bg.tertiary" }}
          >
            {option.label}
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
};

/**
 * Connected MovieSortSelector - Backward compatible component connected to store
 *
 * This maintains the original API while using the new shared type system internally
 */
const ConnectedMovieSortSelector: React.FC = () => {
  const { filters, setSorting } = useMovieFilterStore();
  const { sortOrder, sortDesc } = filters;

  return (
    <MovieSortSelector
      currentSortOrder={sortOrder}
      currentSortDesc={sortDesc}
      onSortChange={(value, desc) => setSorting(value, desc)}
    />
  );
};

// Export both the generic and movie-specific components
// Default export maintains backward compatibility
export default ConnectedMovieSortSelector;
export { SortSelector, MovieSortSelector };
