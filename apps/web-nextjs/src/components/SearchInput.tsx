import React, { useState, useCallback, useEffect, useRef } from "react";
import {
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  IconButton,
  Box,
  List,
  ListItem,
  Text,
  HStack,
  Kbd,
  Spinner,
  Icon,
  useBreakpointValue,
} from "@chakra-ui/react";
import { SearchIcon, CloseIcon } from "@chakra-ui/icons";
import useDebounce from "../hooks/useDebounce";
import useSearchSuggestions from "../hooks/useSearchSuggestions";
import SuggestionItem from "./SuggestionItem";
import { useHotkeys } from "react-hotkeys-hook";
import Link from "next/link";

interface SearchInputProps {
  onSearch: (term: string) => void;
  placeholder?: string;
  initialValue?: string;
  debounceTime?: number;
  onFocus?: () => void;
  onBlur?: () => void;
}

const SearchInput: React.FC<SearchInputProps> = ({
  onSearch,
  placeholder = "Search movies...",
  initialValue = "",
  debounceTime = 500,
  onFocus,
  onBlur,
}) => {
  const [searchTerm, setSearchTerm] = useState(initialValue);
  const debouncedSearchTerm = useDebounce(searchTerm, debounceTime);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const showHotkey = useBreakpointValue({ base: false, md: true });

  // Fetch search suggestions
  const { data: suggestions = [], isFetching } =
    useSearchSuggestions(debouncedSearchTerm);

  // Call onSearch whenever the debounced value changes
  useEffect(() => {
    onSearch(debouncedSearchTerm);
  }, [debouncedSearchTerm, onSearch]);

  // Add keyboard shortcut to focus search
  useHotkeys("meta+k", (event) => {
    event.preventDefault();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  });

  // Handle click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
        if (onBlur) onBlur();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setShowSuggestions(false);
        if (inputRef.current) {
          inputRef.current.blur();
        }
        if (onBlur) onBlur();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [onBlur]);

  // Show suggestions when search term changes
  useEffect(() => {
    if (debouncedSearchTerm.length >= 2) {
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  }, [debouncedSearchTerm]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchTerm("");
    setShowSuggestions(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleFocus = useCallback(() => {
    if (debouncedSearchTerm.length >= 2) {
      setShowSuggestions(true);
    }
    if (onFocus) onFocus();
  }, [debouncedSearchTerm, onFocus]);

  const handleSuggestionClick = useCallback(() => {
    setShowSuggestions(false);
    setSearchTerm("");
    if (onBlur) onBlur();
  }, [onBlur]);

  return (
    <Box position="relative" width="100%">
      <InputGroup>
        <InputLeftElement pointerEvents="none">
          <SearchIcon color="gray.500" />
        </InputLeftElement>

        <Input
          ref={inputRef}
          value={searchTerm}
          onChange={handleChange}
          placeholder={placeholder}
          borderRadius="md"
          focusBorderColor="blue.500"
          onFocus={handleFocus}
          onBlur={() => {
            // Delayed to allow click on suggestions
            setTimeout(() => {
              if (!suggestionsRef.current?.contains(document.activeElement)) {
                if (onBlur) onBlur();
              }
            }, 100);
          }}
        />

        <InputRightElement>
          {searchTerm ? (
            <IconButton
              aria-label="Clear search"
              icon={<CloseIcon />}
              size="sm"
              variant="ghost"
              onClick={clearSearch}
            />
          ) : showHotkey ? (
            <HStack spacing={1} pr={2}>
              <Kbd>⌘</Kbd>
              <Kbd>K</Kbd>
            </HStack>
          ) : null}
        </InputRightElement>
      </InputGroup>

      {/* Suggestions dropdown */}
      {showSuggestions && debouncedSearchTerm.length >= 2 && (
        <Box
          ref={suggestionsRef}
          position="absolute"
          width="100%"
          bg="gray.700"
          boxShadow="lg"
          borderRadius="md"
          zIndex="dropdown"
          mt={2}
          maxH="400px"
          overflowY="auto"
        >
          <List spacing={0}>
            {/* Direct search link */}
            <ListItem key="search-all" p={1}>
              <Link
                href={`/search?q=${encodeURIComponent(debouncedSearchTerm)}`}
                passHref
              >
                <HStack
                  spacing={2}
                  height="45px"
                  p={2}
                  borderRadius="md"
                  _hover={{ bg: "gray.600" }}
                  onClick={handleSuggestionClick}
                >
                  <SearchIcon color="blue.400" />
                  <Text>Search for "{debouncedSearchTerm}"</Text>
                  {isFetching && <Spinner size="sm" />}
                </HStack>
              </Link>
            </ListItem>

            {/* Suggestion items */}
            {suggestions.map((item) => (
              <ListItem key={`${item.type}-${item.info.id}`} p={1}>
                <SuggestionItem item={item} onClick={handleSuggestionClick} />
              </ListItem>
            ))}

            {/* No results state */}
            {!isFetching && suggestions.length === 0 && (
              <ListItem p={3}>
                <Text color="gray.400">No suggestions found</Text>
              </ListItem>
            )}
          </List>
        </Box>
      )}
    </Box>
  );
};

export default SearchInput;
