import React, { useState } from "react";
import { Stack, Flex, useColorModeValue, useToast } from "@chakra-ui/react";
import { HiArrowPath, HiCheck } from "react-icons/hi2";
import { MovieFilter } from "@/components/features/movies/filter";
import useMovieFilterStore from "@/store/movieFilterStore";
import { BottomSheet } from "@/components/mobile/ui/bottom-sheet";
import {
  MobilePrimaryCTA,
  MobileSecondaryCTA,
} from "@/components/mobile/ui/form";
import { createLogger } from "@/utils/logging";
import type { MobileBottomSheetProps } from "@/components/mobile/types";

// Create logger for this component
const logger = createLogger("MovieFilterBottomSheet");

/**
 * MovieFilterBottomSheet Props
 *
 * Extends shared MobileBottomSheetProps with filter-specific features
 */
interface MovieFilterBottomSheetProps
  extends Omit<MobileBottomSheetProps, "children"> {
  /** Callback when filters are applied */
  onApplyFilters?: () => void;
  /** Callback when filters are reset */
  onResetFilters?: () => void;
  /** Whether to show haptic feedback on actions */
  enableHaptics?: boolean;
  /** Custom apply button text */
  applyText?: string;
  /** Custom reset button text */
  resetText?: string;
}

/**
 * MovieFilterBottomSheet component using shared MobileBottomSheetProps
 *
 * A mobile-optimized filter interface using the BottomSheet pattern.
 * Replaces the modal-based approach for a more touch-friendly experience.
 *
 * Features:
 * - Integrated movie filter components
 * - Apply and reset actions with haptic feedback
 * - Loading states for better UX
 * - Toast notifications for user feedback
 * - Configurable through shared mobile bottom sheet props
 *
 * @param isOpen - Whether the bottom sheet is open
 * @param onClose - Callback when bottom sheet is closed
 * @param showHandle - Whether to show drag handle (default: true)
 * @param snapPoints - Snap points for the bottom sheet
 * @param swipeToClose - Whether to enable swipe to close (default: true)
 * @param enableHaptics - Whether to enable haptic feedback (default: true)
 * @param onApplyFilters - Callback when filters are applied
 * @param onResetFilters - Callback when filters are reset
 * @param applyText - Custom apply button text (default: "Apply Filters")
 * @param resetText - Custom reset button text (default: "Reset All Filters")
 */
const MovieFilterBottomSheet: React.FC<MovieFilterBottomSheetProps> = ({
  isOpen,
  onClose,
  showHandle = true,
  snapPoints,
  swipeToClose = true,
  enableHaptics = true,
  onApplyFilters,
  onResetFilters,
  applyText = "Apply Filters",
  resetText = "Reset All Filters",
  ...bottomSheetProps
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const textColor = useColorModeValue("black", "white");
  const toast = useToast();

  const { resetFilters } = useMovieFilterStore();

  const onApply = () => {
    logger.info("Applying movie filters");
    setIsLoading(true);

    // Simulate loading for better UX
    setTimeout(() => {
      toast({
        title: "Filters applied",
        status: "success",
        duration: 2000,
        isClosable: true,
        position: "bottom",
      });

      setIsLoading(false);

      // Call custom apply callback if provided
      if (onApplyFilters) {
        onApplyFilters();
      }

      onClose();
    }, 400);
  };

  const onReset = () => {
    logger.info("Resetting movie filters");
    setIsLoading(true);

    // Simulate loading for better UX
    setTimeout(() => {
      resetFilters();

      toast({
        title: "Filters reset",
        status: "info",
        duration: 2000,
        isClosable: true,
        position: "bottom",
      });

      setIsLoading(false);

      // Call custom reset callback if provided
      if (onResetFilters) {
        onResetFilters();
      }

      onClose();
    }, 400);
  };

  return (
    <BottomSheet
      isOpen={isOpen}
      onClose={onClose}
      title="Filter Movies"
      showDragIndicator={showHandle}
      enableHaptics={enableHaptics}
    >
      <Stack spacing={4} color={textColor} pt={4} pb={2}>
        <MovieFilter />
        <Flex direction="column" gap={3} mt="auto" pb={4}>
          <MobilePrimaryCTA
            icon={HiCheck}
            onClick={onApply}
            isLoading={isLoading}
            enableHaptics={enableHaptics}
          >
            {applyText}
          </MobilePrimaryCTA>
          <MobileSecondaryCTA
            icon={HiArrowPath}
            onClick={onReset}
            isLoading={isLoading}
            variant="outline"
            enableHaptics={enableHaptics}
          >
            {resetText}
          </MobileSecondaryCTA>
        </Flex>
      </Stack>
    </BottomSheet>
  );
};

export default MovieFilterBottomSheet;
