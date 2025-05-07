import SuggestionItem from "@/components/layout/SuggestionItem";
import { useSearchSuggestions } from "@/hooks";
import { TextSuggestion } from "@/services/api/search/types";
import {
  Box,
  Link as ChakraLink,
  HStack,
  Icon,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  Kbd,
  List,
  ListItem,
  Spinner,
  Text,
  useBreakpointValue,
} from "@chakra-ui/react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import { HiMiniMagnifyingGlass } from "react-icons/hi2";

const SearchBar = ({
  onFocus,
  onBlur,
}: {
  onFocus: () => void;
  onBlur: () => void;
}) => {
  const [query, setQuery] = useState("");
  const { data, isFetching } = useSearchSuggestions(query);
  const suggestions = data?.suggestions || [];
  const [showDropdown, setShowDropdown] = useState(false);
  const showHotkey = useBreakpointValue({ base: false, md: true });
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useHotkeys("meta+k", (event) => {
    event.preventDefault();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  });

  const onOpenSuggestionItem = () => {
    setShowDropdown(false);
    setQuery("");
    onBlur();
  };

  useEffect(() => {
    if (query.length === 0) {
      setShowDropdown(false);
      return;
    }
    setShowDropdown(true);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
        // onBlur();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setShowDropdown(false);
        if (inputRef.current) {
          inputRef.current.blur();
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  const handleOnFocus = () => {
    if (query.length > 0) setShowDropdown(true);
    if (!showHotkey) onFocus();
  };

  const handleOnBlur = () => {
    if (!showHotkey) onBlur();
  };

  return (
    <Box position="relative" width="100%">
      <InputGroup>
        <InputLeftElement pointerEvents="none">
          <Icon as={HiMiniMagnifyingGlass} w="20px" h="30px" />
        </InputLeftElement>
        <Input
          ref={inputRef}
          borderRadius={10}
          placeholder="Search movies..."
          variant="filled"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={handleOnFocus}
          onBlur={handleOnBlur}
        />

        <InputRightElement width="auto" paddingRight={2}>
          <HStack spacing={1}>
            {isFetching && <Spinner size="sm" />}
            {showHotkey && (
              <>
                <Kbd>⌘</Kbd>
                <Kbd>K</Kbd>
              </>
            )}
          </HStack>
        </InputRightElement>
      </InputGroup>

      {showDropdown && suggestions.length > 0 && (
        <>
          <Box
            position="fixed"
            top="64px"
            left="0"
            width="calc(100vw - 15px)"
            height="calc(100vh - 64px)"
            zIndex="999"
            onClick={() => setShowDropdown(false)}
            bg="blackAlpha.300"
            backdropFilter="auto"
            backdropBlur="4px"
          />
          <Box
            ref={dropdownRef}
            position="absolute"
            width="100%"
            bg="gray.700"
            boxShadow="md"
            borderRadius="md"
            zIndex="1000"
            mt={2}
            overflow={"hidden"}
          >
            <List spacing={0}>
              <ListItem key="search" padding={1} _hover={{ bg: "gray.600" }}>
                <ChakraLink
                  as={Link}
                  href={`/search/${query}`}
                  textDecoration="none"
                  _hover={{ textDecoration: "none" }}
                >
                  <HStack spacing={2} height="45px">
                    <Box
                      w="30px"
                      h="45px"
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                    >
                      <Icon as={HiMiniMagnifyingGlass} w="20px" h="30px" />
                    </Box>
                    <Text>{query}</Text>
                  </HStack>
                </ChakraLink>
              </ListItem>
              {suggestions.map((suggestion: TextSuggestion) => (
                <ListItem
                  key={`${suggestion.type}-${suggestion.id || suggestion.text}`}
                  padding={1}
                  _hover={{ bg: "gray.600" }}
                >
                  <SuggestionItem
                    suggestion={suggestion}
                    onClick={onOpenSuggestionItem}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </>
      )}
    </Box>
  );
};

export default SearchBar;
