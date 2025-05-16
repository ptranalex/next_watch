"use client";

import { useFilterParams } from "@/hooks/useUrlParams";
import { Search2Icon } from "@chakra-ui/icons";
import {
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  IconButton,
} from "@chakra-ui/react";
import { useCallback, useEffect, useState, useRef } from "react";
import { FaTimes } from "react-icons/fa";

// Interface for search params using Record type
type SearchParams = Record<string, string | null> & {
  q: string | null;
};

const SearchInput = () => {
  // Local state for controlled input
  const [inputValue, setInputValue] = useState("");
  // Timeout ref for manual debouncing
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Default search params
  const defaultParams: SearchParams = {
    q: null,
  };

  // Use filter params hook
  const { filters, setFilters } = useFilterParams<SearchParams>({
    defaults: defaultParams,
  });

  // Sync local state with URL on mount and URL change
  useEffect(() => {
    setInputValue(filters.q || "");
  }, [filters.q]);

  // Manual debounce function for search
  const debouncedSearch = useCallback(
    (value: string) => {
      // Clear existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Set new timeout
      timeoutRef.current = setTimeout(() => {
        setFilters({ q: value || null });
      }, 300);
    },
    [setFilters]
  );

  // Handle input change
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setInputValue(value);

      // Update URL (with manual debounce)
      debouncedSearch(value);
    },
    [debouncedSearch]
  );

  // Clear search
  const handleClear = useCallback(() => {
    setInputValue("");
    setFilters({ q: null });
  }, [setFilters]);

  // Clean up timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <InputGroup>
      <InputLeftElement pointerEvents="none">
        <Search2Icon color="gray.300" />
      </InputLeftElement>

      <Input
        placeholder="Search movies..."
        value={inputValue}
        onChange={handleChange}
        borderRadius="md"
      />

      {inputValue && (
        <InputRightElement>
          <IconButton
            aria-label="Clear search"
            icon={<FaTimes />}
            size="sm"
            variant="ghost"
            onClick={handleClear}
          />
        </InputRightElement>
      )}
    </InputGroup>
  );
};

export default SearchInput;
