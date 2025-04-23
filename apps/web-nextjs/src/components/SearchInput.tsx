import React, { useState, useCallback, useEffect } from "react";
import {
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  IconButton,
} from "@chakra-ui/react";
import { SearchIcon, CloseIcon } from "@chakra-ui/icons";
import useDebounce from "../hooks/useDebounce";

interface SearchInputProps {
  onSearch: (term: string) => void;
  placeholder?: string;
  initialValue?: string;
  debounceTime?: number;
}

const SearchInput = ({
  onSearch,
  placeholder = "Search movies...",
  initialValue = "",
  debounceTime = 500,
}: SearchInputProps) => {
  const [searchTerm, setSearchTerm] = useState(initialValue);
  const debouncedSearchTerm = useDebounce(searchTerm, debounceTime);

  // Call onSearch whenever the debounced value changes
  useEffect(() => {
    onSearch(debouncedSearchTerm);
  }, [debouncedSearchTerm, onSearch]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchTerm("");
  }, []);

  return (
    <InputGroup>
      <InputLeftElement pointerEvents="none">
        <SearchIcon color="gray.500" />
      </InputLeftElement>
      <Input
        value={searchTerm}
        onChange={handleChange}
        placeholder={placeholder}
        borderRadius="md"
        focusBorderColor="blue.500"
      />
      {searchTerm && (
        <InputRightElement>
          <IconButton
            aria-label="Clear search"
            icon={<CloseIcon />}
            size="sm"
            variant="ghost"
            onClick={clearSearch}
          />
        </InputRightElement>
      )}
    </InputGroup>
  );
};

export default SearchInput;
