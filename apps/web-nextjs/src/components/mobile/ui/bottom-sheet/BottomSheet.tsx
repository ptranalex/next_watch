import React, { useEffect, useRef, useState } from "react";
import { Box, Flex, Portal } from "@chakra-ui/react";
import { HiX } from "react-icons/hi";
import { createLogger } from "@/utils/logging";
import { MobileTertiaryCTA } from "../form/MobileFormCTA";

// Create logger for this component
const logger = createLogger("BottomSheet");

export interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  minHeight?: string;
  maxHeight?: string;
  showDragIndicator?: boolean;
  showCloseButton?: boolean;
  avoidKeyboard?: boolean;
  enableHaptics?: boolean;
  title?: string;
}

/**
 * BottomSheet component
 * A mobile-optimized alternative to modals that slides up from the bottom of the screen
 * Dynamically sizes based on content with touch gesture support
 */
const BottomSheet: React.FC<BottomSheetProps> = ({
  isOpen,
  onClose,
  children,
  minHeight = "20vh",
  maxHeight = "90vh",
  showDragIndicator = true,
  showCloseButton = true,
  avoidKeyboard = true,
  enableHaptics = true,
  title,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const startY = useRef(0);
  const currentY = useRef(0);
  const sheetRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  // Apply haptic feedback with consistent patterns
  const triggerHaptics = (pattern: number | number[] = 20) => {
    if (enableHaptics && window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(pattern);
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
      setIsExpanded(false);

      // Provide haptic feedback when opening
      triggerHaptics(30);
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

  // Handle input focus - auto-scroll to input when focused
  useEffect(() => {
    if (!isOpen) return;

    const handleFocus = (e: FocusEvent) => {
      // Check if the focused element is an input inside the sheet
      const target = e.target as HTMLElement;

      if (
        target &&
        (target instanceof HTMLInputElement ||
          target instanceof HTMLTextAreaElement ||
          target instanceof HTMLSelectElement)
      ) {
        if (sheetRef.current?.contains(target)) {
          // Give the DOM time to adjust, then scroll the element into view
          setTimeout(() => {
            target.scrollIntoView({ behavior: "smooth", block: "center" });
          }, 100);
        }
      }
    };

    document.addEventListener("focusin", handleFocus);
    return () => {
      document.removeEventListener("focusin", handleFocus);
    };
  }, [isOpen]);

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
    } else if (deltaY < 0 && !isExpanded) {
      // Allow dragging up slightly to expand if not already expanded
      const dampedDelta = deltaY * 0.2;

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
      triggerHaptics([20, 50]);
      onClose();
    } else if (deltaY < -50 && !isExpanded) {
      // If dragged up significantly, expand to max height
      toggleExpand();
    } else {
      // Reset position
      if (sheetRef.current) {
        sheetRef.current.style.transform = "translateY(0)";
      }
    }
  };

  // Toggle between expanded and normal states
  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
    triggerHaptics(20);
  };

  // Handle indicator drag
  const handleIndicatorClick = () => {
    toggleExpand();
  };

  // Handle close button click
  const handleClose = () => {
    triggerHaptics(20);
    onClose();
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
        bg="blackAlpha.700"
        backdropFilter="blur(8px) hue-rotate(15deg)"
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
        maxHeight={isExpanded ? maxHeight : "auto"}
        minHeight={minHeight}
        bg="bg.primary"
        borderTopRadius="16px"
        borderTop="1px"
        borderColor="text.tertiary"
        shadow="xl"
        zIndex={1001}
        transform={isOpen ? "translateY(0)" : "translateY(100%)"}
        transition="transform 0.3s ease, max-height 0.3s ease"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        overflow="hidden"
        display="flex"
        flexDirection="column"
      >
        {/* Header area with drag indicator and title */}
        <Flex
          justify="center"
          align="center"
          direction="column"
          position="relative"
          borderBottom={title ? "1px solid" : "none"}
          borderColor="text.tertiary"
          py={2}
          flexShrink={0}
        >
          {/* Drag indicator */}
          {showDragIndicator && (
            <Box
              w="36px"
              h="4px"
              borderRadius="full"
              bg="text.tertiary"
              my={1}
              onClick={handleIndicatorClick}
              cursor="grab"
            />
          )}

          {/* Optional title */}
          {title && (
            <Box fontWeight="medium" fontSize="md" my={1} color="text.primary">
              {title}
            </Box>
          )}

          {/* Close button */}
          {showCloseButton && (
            <Box position="absolute" top={2} right={2}>
              <MobileTertiaryCTA
                icon={HiX}
                onClick={handleClose}
                width="auto"
                enableHaptics={enableHaptics}
              >
                {""}
              </MobileTertiaryCTA>
            </Box>
          )}
        </Flex>

        {/* Content */}
        <Box ref={contentRef} overflowY="auto" flex="1" px={6} pb={14}>
          {children}
        </Box>
      </Box>
    </Portal>
  );
};

export default BottomSheet;
