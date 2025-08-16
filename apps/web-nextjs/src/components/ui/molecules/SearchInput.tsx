"use client";

import React, {
  useState,
  useRef,
  useEffect,
  useCallback,
  useMemo,
} from "react";
import {
  Box,
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
  useBreakpointValue,
  FormControl,
  FormErrorMessage,
  IconButton,
  useColorModeValue,
} from "@chakra-ui/react";
import { useRouter, usePathname } from "next/navigation";
import { useHotkeys } from "react-hotkeys-hook";
import { HiMiniMagnifyingGlass, HiXMark } from "react-icons/hi2";
import SuggestionItem from "@/components/ui/molecules/SuggestionItem";
import SearchItem from "@/components/ui/molecules/SearchItem";
import { useSearchSuggestions } from "@/services/hooks";
import { TextSuggestion } from "@/services/api/search/types";
import { useDebounce } from "@/services/hooks/ui/useDebounce";
import type { SearchInputProps } from "./types";

/**
 * SearchInput component with enhanced functionality and mobile support
 *
 * Features:
 * - Real-time search suggestions with debouncing
 * - Keyboard shortcuts and navigation
 * - Mobile-optimized with haptic feedback
 * - Comprehensive accessibility support
 * - Error handling and loading states
 * - Responsive design
 */
const SearchInput: React.FC<SearchInputProps> = ({
  value: controlledValue,
  onChange: controlledOnChange,
  onFocus,
  onBlur,
  placeholder = "Search movies...",
  showHotkey: propShowHotkey,
  hotkey = "meta+k",
  enableSuggestions = true,
  maxSuggestions = 8,
  showOnMobile = true,
  searchIcon: SearchIcon = HiMiniMagnifyingGlass,
  enableHaptics = true,
  debounceDelay = 300,
  dropdownZIndex = 1000,
  animated = true,
  isDisabled = false,
  error,
  size = "md",
  clearOnNavigation = true,
}) => {
  const router = useRouter();
  const pathname = usePathname();

  // Internal state for uncontrolled usage
  const [internalValue, setInternalValue] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [focusedSuggestionIndex, setFocusedSuggestionIndex] = useState(-1);

  // Determine if component is controlled
  const isControlled = controlledValue !== undefined;
  const value = isControlled ? controlledValue : internalValue;
  const onChange = isControlled ? controlledOnChange : setInternalValue;

  // Debounce search query for API calls
  const debouncedQuery = useDebounce(value, debounceDelay);

  // Responsive breakpoint detection
  const responsiveShowHotkey = useBreakpointValue({ base: false, md: true });
  const showHotkey = propShowHotkey ?? responsiveShowHotkey;

  // Theme-aware colors using hydration-safe values
  const dropdownBg = useColorModeValue("gray.100", "gray.700");
  const overlayBg = useColorModeValue("blackAlpha.300", "blackAlpha.500");
  const borderColor = useColorModeValue("gray.200", "gray.600");
  const hoverBg = useColorModeValue("gray.200", "gray.600");

  // Refs for DOM manipulation
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Search suggestions hook
  const {
    data,
    isFetching,
    error: suggestionsError,
  } = useSearchSuggestions(enableSuggestions ? debouncedQuery : "");

  const suggestions = useMemo(() => {
    const rawSuggestions = data?.results || [];
    return rawSuggestions.slice(0, maxSuggestions);
  }, [data?.results, maxSuggestions]);

  // Keyboard shortcut handling
  useHotkeys(
    hotkey,
    useCallback(
      (event) => {
        if (isDisabled) return;

        event.preventDefault();
        if (inputRef.current) {
          inputRef.current.focus();

          // Haptic feedback for mobile
          if (enableHaptics && navigator.vibrate) {
            try {
              navigator.vibrate(25);
            } catch (error) {
              console.warn("Haptic feedback not supported", error);
            }
          }
        }
      },
      [isDisabled, enableHaptics]
    )
  );

  // Handle input value changes
  const handleInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value;
      if (onChange) {
        onChange(newValue);
      }
      setFocusedSuggestionIndex(-1);
    },
    [onChange]
  );

  // Handle input focus
  const handleInputFocus = useCallback(() => {
    if (isDisabled) return;
    if (value.length > 0 && enableSuggestions) {
      setShowDropdown(true);
    }
    if (onFocus) {
      onFocus();
    }
  }, [value, enableSuggestions, onFocus, isDisabled]);

  // Handle input blur
  const handleInputBlur = useCallback(() => {
    if (isDisabled) return;
    if (onBlur) {
      onBlur();
    }
  }, [onBlur, isDisabled]);

  // Handle suggestion selection (clears input and closes dropdown)
  const handleSuggestionSelect = useCallback(() => {
    setShowDropdown(false);
    setFocusedSuggestionIndex(-1);
    if (onChange) {
      onChange("");
    }
    if (onBlur) {
      onBlur();
    }
  }, [onChange, onBlur]);

  // Handle direct search click (keeps input value)
  const handleDirectSearchClick = useCallback(() => {
    setShowDropdown(false);
    setFocusedSuggestionIndex(-1);
  }, []);

  // Handle clear button click
  const handleClear = useCallback(() => {
    if (isDisabled) return;
    if (onChange) {
      onChange("");
    }
    setShowDropdown(false);
    setFocusedSuggestionIndex(-1);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [onChange, isDisabled]);

  // Navigate to search results
  const navigateToSearch = useCallback(
    (query: string) => {
      if (query.trim().length > 0) {
        const searchUrl = `/search?q=${encodeURIComponent(query.trim())}`;
        setShowDropdown(false);
        setFocusedSuggestionIndex(-1);
        router.push(searchUrl);
      }
    },
    [router]
  );

  // Keyboard navigation for suggestions
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      switch (event.key) {
        case "ArrowDown":
          if (!showDropdown || suggestions.length === 0) return;
          event.preventDefault();
          setFocusedSuggestionIndex((prev) =>
            prev < suggestions.length ? prev + 1 : prev
          );
          break;
        case "ArrowUp":
          if (!showDropdown || suggestions.length === 0) return;
          event.preventDefault();
          setFocusedSuggestionIndex((prev) => (prev > -1 ? prev - 1 : -1));
          break;
        case "Enter":
          event.preventDefault();
          if (
            showDropdown &&
            suggestions.length > 0 &&
            focusedSuggestionIndex >= 0
          ) {
            handleSuggestionSelect();
          } else {
            navigateToSearch(value);
          }
          break;
        case "Escape":
          setShowDropdown(false);
          setFocusedSuggestionIndex(-1);
          if (inputRef.current) {
            inputRef.current.blur();
          }
          break;
      }
    },
    [
      showDropdown,
      suggestions.length,
      focusedSuggestionIndex,
      handleSuggestionSelect,
      navigateToSearch,
      value,
    ]
  );

  // Handle dropdown visibility
  useEffect(() => {
    if (!enableSuggestions) {
      setShowDropdown(false);
      return;
    }

    if (value.length === 0) {
      setShowDropdown(false);
      return;
    }

    if (suggestions.length > 0 && document.activeElement === inputRef.current) {
      setShowDropdown(true);
    }
  }, [value, suggestions.length, enableSuggestions]);

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
        setFocusedSuggestionIndex(-1);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Clear input when navigating away from search pages
  useEffect(() => {
    // Clear dropdown and suggestions when leaving any page
    if (pathname !== "/search") {
      setShowDropdown(false);
      setFocusedSuggestionIndex(-1);

      // Clear input value when navigating away from search pages
      // This provides a clean slate when user returns to search
      if (onChange && !isControlled && clearOnNavigation) {
        onChange("");
      }
    }
  }, [pathname, onChange, isControlled, clearOnNavigation]);

  // Don't render if configured to hide on mobile
  if (!showOnMobile && typeof window !== "undefined") {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) return null;
  }

  const hasError = Boolean(error || suggestionsError);
  const showClearButton = value.length > 0 && !isDisabled;

  return (
    <FormControl isInvalid={hasError} isDisabled={isDisabled}>
      <Box position="relative" width="100%">
        <InputGroup size={size}>
          <InputLeftElement pointerEvents="none">
            <Icon
              as={SearchIcon}
              w="20px"
              h="20px"
              color={hasError ? "feedback.error" : "text.secondary"}
            />
          </InputLeftElement>

          <Input
            ref={inputRef}
            borderRadius="md"
            placeholder={placeholder}
            variant="filled"
            value={value}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onBlur={handleInputBlur}
            onKeyDown={handleKeyDown}
            aria-label="Search input"
            aria-expanded={showDropdown}
            aria-haspopup="listbox"
            aria-autocomplete="list"
            aria-activedescendant={
              focusedSuggestionIndex >= 0
                ? `suggestion-${focusedSuggestionIndex}`
                : undefined
            }
            isDisabled={isDisabled}
            borderColor={hasError ? "feedback.error" : undefined}
            _focus={{
              borderColor: hasError ? "feedback.error" : "colors.primary",
            }}
          />

          <InputRightElement width="auto" paddingRight={2}>
            <HStack spacing={1}>
              {isFetching && <Spinner size="sm" />}
              {showClearButton && (
                <IconButton
                  aria-label="Clear search"
                  icon={<HiXMark />}
                  size="xs"
                  variant="ghost"
                  onClick={handleClear}
                />
              )}
              {showHotkey && !showClearButton && (
                <>
                  <Kbd fontSize="xs">⌘</Kbd>
                  <Kbd fontSize="xs">K</Kbd>
                </>
              )}
            </HStack>
          </InputRightElement>
        </InputGroup>

        {/* Dropdown with suggestions */}
        {showDropdown && suggestions.length > 0 && (
          <>
            {/* Backdrop overlay - positioned below input to not interfere with typing */}
            <Box
              position="fixed"
              top="0"
              left="0"
              width="100vw"
              height="100vh"
              zIndex={dropdownZIndex - 1}
              onClick={() => setShowDropdown(false)}
              // Create invisible clickable area that doesn't block input visibility
              bg="transparent"
            />

            {/* Visual backdrop blur effect positioned below the dropdown */}
            <Box
              position="absolute"
              top="calc(100% + 8px)" // Start just below the dropdown
              left="-100vw" // Extend to cover full width
              width="300vw" // Ensure full coverage
              height="100vh" // Cover remaining height
              zIndex={dropdownZIndex - 2}
              bg={overlayBg}
              backdropFilter="auto"
              backdropBlur="4px"
              opacity={animated ? 0.8 : 0.6}
              transition={animated ? "opacity 0.2s ease-in-out" : "none"}
              pointerEvents="none" // Don't interfere with interactions
            />

            {/* Suggestions dropdown */}
            <Box
              ref={dropdownRef}
              position="absolute"
              width="100%"
              bg={dropdownBg}
              boxShadow="lg"
              borderRadius="md"
              borderWidth="1px"
              borderColor={borderColor}
              zIndex={dropdownZIndex}
              mt={2}
              overflow="hidden"
              transform={
                animated && showDropdown ? "translateY(0)" : "translateY(-4px)"
              }
              opacity={animated && showDropdown ? 1 : 0}
              transition={
                animated ? "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)" : "none"
              }
            >
              <List spacing={0} role="listbox" aria-label="Search suggestions">
                {/* Direct search option */}
                <ListItem
                  key="search"
                  padding={1}
                  _hover={{ bg: hoverBg }}
                  bg={focusedSuggestionIndex === -1 ? hoverBg : "transparent"}
                >
                  <SearchItem
                    text={`Search for "${value}"`}
                    icon={HiMiniMagnifyingGlass}
                    href={`/search?q=${encodeURIComponent(value)}`}
                    onClick={handleDirectSearchClick}
                    role="option"
                    aria-selected={focusedSuggestionIndex === -1}
                  />
                </ListItem>

                {/* Suggestion items */}
                {suggestions.map(
                  (suggestion: TextSuggestion, index: number) => (
                    <ListItem
                      key={`${suggestion.type}-${
                        suggestion.id || suggestion.text
                      }`}
                      padding={1}
                      _hover={{ bg: hoverBg }}
                      bg={
                        focusedSuggestionIndex === index
                          ? hoverBg
                          : "transparent"
                      }
                    >
                      <SuggestionItem
                        suggestion={suggestion}
                        onClick={handleSuggestionSelect}
                      />
                    </ListItem>
                  )
                )}
              </List>
            </Box>
          </>
        )}
      </Box>

      {/* Error message */}
      {hasError && (
        <FormErrorMessage>
          {error || "Failed to load search suggestions"}
        </FormErrorMessage>
      )}
    </FormControl>
  );
};

export default SearchInput;
