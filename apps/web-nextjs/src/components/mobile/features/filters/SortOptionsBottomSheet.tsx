import React from "react";
import { useColorModeValue, Text, VStack, Flex, Box } from "@chakra-ui/react";
import useMovieFilterStore from "@/store/movieFilterStore";
import { BottomSheet } from "@/components/mobile/ui/bottom-sheet";
import { createLogger } from "@/utils/logging";
import { HiCheck } from "react-icons/hi";
import type { MobileBottomSheetProps } from "@/components/mobile/types";

// Create logger for this component
const logger = createLogger("SortOptionsBottomSheet");

/** Sort option definition */
interface SortOption {
  value: string;
  label: string;
  desc: boolean;
}

/**
 * SortOptionsBottomSheet Props
 *
 * Extends shared MobileBottomSheetProps with sorting-specific features
 */
interface SortOptionsBottomSheetProps
  extends Omit<MobileBottomSheetProps, "children"> {
  /** Custom sort options (defaults to movie sort options) */
  customSortOptions?: SortOption[];
  /** Callback when sort option is changed */
  onSortChange?: (value: string, desc: boolean) => void;
  /** Whether to show haptic feedback on selection */
  enableHaptics?: boolean;
  /** Custom title for the bottom sheet */
  title?: string;
}

// Default movie sort options
const defaultSortOptions: SortOption[] = [
  { value: "title", label: "Name", desc: false },
  { value: "release_date", label: "Release date", desc: true },
  { value: "imdb_rating", label: "IMDB rating", desc: true },
  { value: "imdb_rating", label: "IMDB rating (Asc)", desc: false },
  {
    value: "rotten_tomatoes_rating",
    label: "Rotten Tomatoes rating",
    desc: true,
  },
  { value: "metacritic_rating", label: "Metacritic rating", desc: true },
  { value: "vote_count", label: "Popularity", desc: true },
];

/**
 * SortOptionsBottomSheet component using shared MobileBottomSheetProps
 *
 * A mobile-optimized sort interface using the BottomSheet pattern.
 * Replaces the dropdown-based approach for a more touch-friendly experience.
 *
 * Features:
 * - Configurable sort options
 * - Visual feedback for active selection
 * - Haptic feedback on selection
 * - Clean touch-optimized interface
 * - Configurable through shared mobile bottom sheet props
 *
 * @param isOpen - Whether the bottom sheet is open
 * @param onClose - Callback when bottom sheet is closed
 * @param showHandle - Whether to show drag handle (default: true)
 * @param snapPoints - Snap points for the bottom sheet
 * @param swipeToClose - Whether to enable swipe to close (default: true)
 * @param customSortOptions - Custom sort options (defaults to movie sort options)
 * @param onSortChange - Callback when sort option is changed
 * @param enableHaptics - Whether to enable haptic feedback (default: true)
 * @param title - Custom title (default: "Sort By")
 */
const SortOptionsBottomSheet: React.FC<SortOptionsBottomSheetProps> = ({
  isOpen,
  onClose,
  showHandle = true,
  snapPoints,
  swipeToClose = true,
  customSortOptions,
  onSortChange,
  enableHaptics = true,
  title = "Sort By",
  ...bottomSheetProps
}) => {
  const textColor = useColorModeValue("text.primary", "text.primary");
  const activeColor = useColorModeValue("colors.primary", "colors.primary");
  const hoverBg = useColorModeValue("bg.subtle", "bg.subtle");
  const borderColor = useColorModeValue("border.subtle", "border.subtle");

  // Get filters and the setSorting method from the store
  const { filters, setSorting } = useMovieFilterStore();
  const { sortOrder, sortDesc } = filters;

  const sortOptions = customSortOptions || defaultSortOptions;

  // Find the current sort order for display
  const currentSortOrder = sortOptions.find(
    (order) => order.value === sortOrder && order.desc === sortDesc
  );

  const handleSortChange = (value: string, desc: boolean) => {
    logger.info(`Setting sort to: ${value}, desc: ${desc}`);

    // Apply haptic feedback if enabled
    if (enableHaptics && window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(25);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }

    // Call custom sort change handler if provided
    if (onSortChange) {
      onSortChange(value, desc);
    } else {
      setSorting(value, desc);
    }

    onClose();
  };

  return (
    <BottomSheet
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      showDragIndicator={showHandle}
      enableHaptics={enableHaptics}
      minHeight="auto"
    >
      <VStack spacing={0} align="stretch" color={textColor} pt={2}>
        {sortOptions.map((option) => {
          const isActive =
            option.value === currentSortOrder?.value &&
            option.desc === currentSortOrder?.desc;

          return (
            <Flex
              key={`${option.value}-${option.desc ? "desc" : "asc"}`}
              px={4}
              py={4}
              alignItems="center"
              justifyContent="space-between"
              borderBottomWidth="1px"
              borderColor={borderColor}
              onClick={() =>
                handleSortChange(option.value, option.desc ?? true)
              }
              cursor="pointer"
              bg={isActive ? hoverBg : "transparent"}
              _hover={{ bg: hoverBg }}
              transition="background 0.2s"
              borderRadius="md"
            >
              <Text
                fontWeight={isActive ? "bold" : "normal"}
                color={isActive ? activeColor : "inherit"}
                fontSize="lg"
              >
                {option.label}
              </Text>

              {isActive && (
                <Box color={activeColor} fontSize="xl">
                  <HiCheck />
                </Box>
              )}
            </Flex>
          );
        })}
      </VStack>
    </BottomSheet>
  );
};

export default SortOptionsBottomSheet;
