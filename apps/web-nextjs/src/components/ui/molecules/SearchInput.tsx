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
  useColorModeValue,
  FormControl,
  FormErrorMessage,
  IconButton,
} from "@chakra-ui/react";
import Link from "next/link";
import { useHotkeys } from "react-hotkeys-hook";
import { HiMiniMagnifyingGlass, HiXMark } from "react-icons/hi2";
import SuggestionItem from "@/components/ui/molecules/SuggestionItem";
import { useSearchSuggestions } from "@/hooks";
import { TextSuggestion } from "@/services/api/search/types";
import { createLogger } from "@/utils/logging";
import { useDebounce } from "@/hooks/ui/useDebounce";
import type { SearchInputProps } from "./types";

// Create logger for this component
const logger = createLogger("SearchInput");

/**
 * SearchInput component with enhanced functionality and mobile support
 *
 * A powerful search input with real-time suggestions, keyboard shortcuts,
 * mobile optimizations, and comprehensive accessibility features.
 *
 * Features:
 * - Real-time search suggestions with debouncing
 * - Keyboard shortcuts with customizable hotkeys
 * - Mobile-optimized with haptic feedback
 * - Comprehensive accessibility (ARIA, keyboard navigation)
 * - Performance optimized with proper memoization
 * - Error handling and loading states
 * - Responsive design with breakpoint-aware features
 * - Configurable through comprehensive props interface
 *
 * @example
 * ```tsx
 * // Basic usage
 * <SearchInput />
 *
 * // Controlled with custom configuration
 * <SearchInput
 *   value={searchValue}
 *   onChange={setSearchValue}
 *   onFocus={handleFocus}
 *   onBlur={handleBlur}
 *   enableSuggestions={true}
 *   maxSuggestions={5}
 *   debounceDelay={500}
 * />
 *
 * // Mobile-optimized configuration
 * <SearchInput
 *   showOnMobile={true}
 *   enableHaptics={true}
 *   animated={true}
 *   showHotkey={false}
 * />
 * ```
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
}) => {
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

  // Responsive breakpoint detection (must be called before any conditional logic)
  const responsiveShowHotkey = useBreakpointValue({ base: false, md: true });
  const showHotkey = propShowHotkey ?? responsiveShowHotkey;

  // Theme-aware colors
  const dropdownBg = useColorModeValue("bg.secondary", "bg.secondary");
  const overlayBg = useColorModeValue("blackAlpha.300", "blackAlpha.500");
  const borderColor = useColorModeValue("border.subtle", "border.subtle");
  const hoverBg = useColorModeValue("bg.tertiary", "bg.tertiary");

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
    const rawSuggestions = data?.suggestions || [];
    return rawSuggestions.slice(0, maxSuggestions);
  }, [data?.suggestions, maxSuggestions]);

  // Keyboard shortcut handling
  useHotkeys(
    hotkey,
    useCallback(
      (event) => {
        if (isDisabled) return;

        event.preventDefault();
        logger.debug(`Search hotkey triggered: ${hotkey}`);

        if (inputRef.current) {
          inputRef.current.focus();

          // Haptic feedback for mobile
          if (enableHaptics && navigator.vibrate) {
            try {
              navigator.vibrate(25);
            } catch (error) {
              logger.warn("Haptic feedback not supported", error);
            }
          }
        }
      },
      [hotkey, isDisabled, enableHaptics]
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

      logger.debug("Search input changed", { value: newValue });
    },
    [onChange]
  );

  // Handle input focus
  const handleInputFocus = useCallback(() => {
    if (isDisabled) return;

    logger.debug("Search input focused");

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

    logger.debug("Search input blurred");

    if (onBlur) {
      onBlur();
    }
  }, [onBlur, isDisabled]);

  // Handle suggestion selection
  const handleSuggestionSelect = useCallback(() => {
    setShowDropdown(false);
    setFocusedSuggestionIndex(-1);

    if (onChange) {
      onChange("");
    }

    if (onBlur) {
      onBlur();
    }

    logger.debug("Suggestion selected");
  }, [onChange, onBlur]);

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

    logger.debug("Search input cleared");
  }, [onChange, isDisabled]);

  // Keyboard navigation for suggestions
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (!showDropdown || suggestions.length === 0) return;

      switch (event.key) {
        case "ArrowDown":
          event.preventDefault();
          setFocusedSuggestionIndex((prev) =>
            prev < suggestions.length ? prev + 1 : prev
          );
          break;
        case "ArrowUp":
          event.preventDefault();
          setFocusedSuggestionIndex((prev) => (prev > -1 ? prev - 1 : -1));
          break;
        case "Enter":
          if (focusedSuggestionIndex >= 0) {
            event.preventDefault();
            handleSuggestionSelect();
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
                  <ChakraLink
                    as={Link}
                    href={`/search/${encodeURIComponent(value)}`}
                    textDecoration="none"
                    _hover={{ textDecoration: "none" }}
                    onClick={handleSuggestionSelect}
                    role="option"
                    aria-selected={focusedSuggestionIndex === -1}
                  >
                    <HStack spacing={3} height="45px" px={2}>
                      <Box
                        w="30px"
                        h="30px"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                      >
                        <Icon
                          as={SearchIcon}
                          w="20px"
                          h="20px"
                          color="text.secondary"
                        />
                      </Box>
                      <Text color="text.primary" fontSize="md">
                        Search for &quot;{value}&quot;
                      </Text>
                    </HStack>
                  </ChakraLink>
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
