import React, { useEffect, useRef, useState } from "react";
import {
  Box,
  Flex,
  useColorModeValue,
  Portal,
  IconButton,
} from "@chakra-ui/react";
import { HiX } from "react-icons/hi";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("BottomSheet");

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  height?: string | number;
  snapPoints?: string[];
  showDragIndicator?: boolean;
  showCloseButton?: boolean;
  avoidKeyboard?: boolean;
}

/**
 * BottomSheet component
 * A mobile-optimized alternative to modals that slides up from the bottom of the screen
 * Supports dragging, multiple snap points, and touch gestures
 */
const BottomSheet: React.FC<BottomSheetProps> = ({
  isOpen,
  onClose,
  children,
  height = "60vh",
  snapPoints = ["25vh", "50vh", "75vh"],
  showDragIndicator = true,
  showCloseButton = true,
  avoidKeyboard = true,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentHeight, setCurrentHeight] = useState(height);
  const [isDragging, setIsDragging] = useState(false);
  const startY = useRef(0);
  const currentY = useRef(0);
  const sheetRef = useRef<HTMLDivElement>(null);

  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");
  const overlayBg = useColorModeValue(
    "rgba(0, 0, 0, 0.4)",
    "rgba(0, 0, 0, 0.6)"
  );

  // Apply haptic feedback
  const applyHapticFeedback = (intensity: number = 10) => {
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(intensity);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }
  };

  // Handle sheet open/close
  useEffect(() => {
    if (isOpen) {
      // Delay to allow for animation
      setIsVisible(true);
      document.body.style.overflow = "hidden"; // Prevent background scrolling
    } else {
      // Animate out then hide
      setTimeout(() => {
        setIsVisible(false);
        document.body.style.overflow = ""; // Restore scrolling
      }, 300);
    }

    return () => {
      document.body.style.overflow = ""; // Cleanup
    };
  }, [isOpen]);

  // Handle keyboard visibility (for inputs)
  useEffect(() => {
    if (!avoidKeyboard) return;

    const handleResize = () => {
      const visualViewport = window.visualViewport;
      if (!visualViewport) return;

      const viewport = {
        height: visualViewport.height,
        width: visualViewport.width,
      };

      // If keyboard is likely visible (viewport height reduced significantly)
      if (viewport.height < window.innerHeight * 0.75) {
        // Calculate keyboard height
        const keyboardHeight = window.innerHeight - viewport.height;
        // Adjust the sheet to stay above keyboard
        if (sheetRef.current) {
          sheetRef.current.style.bottom = `${keyboardHeight}px`;
        }
      } else {
        // Reset when keyboard is hidden
        if (sheetRef.current) {
          sheetRef.current.style.bottom = "0";
        }
      }
    };

    window.visualViewport?.addEventListener("resize", handleResize);
    return () => {
      window.visualViewport?.removeEventListener("resize", handleResize);
    };
  }, [avoidKeyboard]);

  // Touch event handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    startY.current = e.touches[0].clientY;
    currentY.current = startY.current;
    setIsDragging(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;

    currentY.current = e.touches[0].clientY;
    const deltaY = currentY.current - startY.current;

    // Only allow dragging down or to snap points
    if (deltaY > 0) {
      // Dampen the movement for better feel
      const dampedDelta = deltaY * 0.6;

      if (sheetRef.current) {
        sheetRef.current.style.transform = `translateY(${dampedDelta}px)`;
      }
    }
  };

  const handleTouchEnd = () => {
    if (!isDragging) return;
    setIsDragging(false);

    const deltaY = currentY.current - startY.current;

    if (deltaY > 100) {
      // If dragged down significantly, close the sheet
      applyHapticFeedback(15);
      onClose();
    } else if (deltaY > 20) {
      // If dragged down a small amount, snap to a smaller size
      snapToSmallerSize();
    } else {
      // Reset position
      if (sheetRef.current) {
        sheetRef.current.style.transform = "translateY(0)";
      }
    }
  };

  // Snap to next smaller size
  const snapToSmallerSize = () => {
    if (!snapPoints.length) return;

    const currentIndex = snapPoints.indexOf(currentHeight.toString());
    if (currentIndex > 0) {
      const newHeight = snapPoints[currentIndex - 1];
      setCurrentHeight(newHeight);
      applyHapticFeedback(10);
    } else {
      // Already at smallest size, close
      onClose();
    }
  };

  // Snap to next larger size
  const snapToLargerSize = () => {
    if (!snapPoints.length) return;

    const currentIndex = snapPoints.indexOf(currentHeight.toString());
    if (currentIndex < snapPoints.length - 1) {
      const newHeight = snapPoints[currentIndex + 1];
      setCurrentHeight(newHeight);
      applyHapticFeedback(10);
    }
  };

  // Handle indicator drag
  const handleIndicatorClick = () => {
    snapToLargerSize();
  };

  // Don't render anything if not open and not visible
  if (!isOpen && !isVisible) {
    return null;
  }

  return (
    <Portal>
      {/* Backdrop overlay */}
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bg={overlayBg}
        zIndex={1000}
        onClick={onClose}
        opacity={isOpen ? 1 : 0}
        transition="opacity 0.3s ease"
        pointerEvents={isOpen ? "auto" : "none"}
      />

      {/* Bottom sheet */}
      <Box
        ref={sheetRef}
        position="fixed"
        left={0}
        right={0}
        bottom={0}
        height={currentHeight}
        bg={bgColor}
        borderTopRadius="16px"
        borderTop="1px"
        borderColor={borderColor}
        shadow="xl"
        zIndex={1001}
        transform={isOpen ? "translateY(0)" : "translateY(100%)"}
        transition="transform 0.3s ease, height 0.3s ease"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        overflow="hidden"
      >
        {/* Drag indicator */}
        {showDragIndicator && (
          <Flex
            justify="center"
            align="center"
            h="24px"
            onClick={handleIndicatorClick}
            cursor="grab"
          >
            <Box
              w="36px"
              h="4px"
              borderRadius="full"
              bg="gray.300"
              _dark={{ bg: "gray.600" }}
              my={2}
            />
          </Flex>
        )}

        {/* Close button */}
        {showCloseButton && (
          <Box position="absolute" top={2} right={2}>
            <IconButton
              icon={<HiX />}
              aria-label="Close panel"
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
            />
          </Box>
        )}

        {/* Content */}
        <Box
          overflowY="auto"
          height={`calc(${currentHeight} - ${
            showDragIndicator ? "24px" : "0px"
          })`}
          px={4}
          pb={4}
        >
          {children}
        </Box>
      </Box>
    </Portal>
  );
};

export default BottomSheet;
