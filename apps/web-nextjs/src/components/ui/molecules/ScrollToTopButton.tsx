import React, { useEffect, useState, useCallback, useRef } from "react";
import {
  IconButton,
  useColorModeValue,
  Box,
  VisuallyHidden,
} from "@chakra-ui/react";
import { ArrowUpIcon } from "@chakra-ui/icons";
import { HiArrowUp } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";
import type { ScrollToTopButtonProps } from "./types";

// Create logger for this component
const logger = createLogger("ScrollToTopButton");

/**
 * ScrollToTopButton component with enhanced mobile support and performance
 *
 * A performant, accessible scroll-to-top button with mobile optimizations.
 * Features throttled scroll event handling, smooth animations, haptic feedback,
 * and responsive design considerations.
 *
 * Features:
 * - Throttled scroll event handling for better performance
 * - Configurable visibility threshold and positioning
 * - Mobile-optimized with haptic feedback support
 * - Smooth animations with proper accessibility
 * - SSR-safe implementation with proper cleanup
 * - Customizable styling and behavior
 * - Responsive design with mobile-specific considerations
 *
 * @example
 * ```tsx
 * // Basic usage
 * <ScrollToTopButton />
 *
 * // Customized configuration
 * <ScrollToTopButton
 *   threshold={500}
 *   bottom={8}
 *   right={8}
 *   size="lg"
 *   iconType="heroicons"
 *   enableHaptics={true}
 *   animated={true}
 * />
 *
 * // Mobile-specific configuration
 * <ScrollToTopButton
 *   showOnMobile={true}
 *   enableHaptics={true}
 *   threshold={200}
 *   throttleDelay={50}
 * />
 *
 * // Performance-optimized configuration
 * <ScrollToTopButton
 *   throttleDelay={200}
 *   smoothScroll={true}
 *   scrollDuration={800}
 *   animated={false}
 * />
 * ```
 *
 * @param threshold - Scroll distance to show button (default: 300)
 * @param bottom - Distance from bottom edge (default: 6)
 * @param right - Distance from right edge (default: 6)
 * @param size - Button size (default: "md")
 * @param iconType - Icon style to use (default: "chakra")
 * @param smoothScroll - Enable smooth scrolling (default: true)
 * @param showOnMobile - Show on mobile devices (default: true)
 * @param scrollDuration - Custom scroll duration (default: 500)
 * @param enableHaptics - Enable haptic feedback (default: true)
 * @param throttleDelay - Scroll event throttle delay (default: 100)
 * @param zIndex - Custom z-index (default: 1000)
 * @param animated - Enable button animations (default: true)
 */
const ScrollToTopButton: React.FC<ScrollToTopButtonProps> = ({
  threshold = 300,
  bottom = 6,
  right = 6,
  size = "md",
  iconType = "chakra",
  smoothScroll = true,
  showOnMobile = true,
  scrollDuration = 500,
  enableHaptics = true,
  throttleDelay = 100,
  zIndex = 1000,
  animated = true,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isScrolling, setIsScrolling] = useState(false);
  const throttleTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Theme-aware colors (must be called before any conditional logic)
  const bgColor = useColorModeValue("colors.primary", "colors.primary");
  const hoverBgColor = useColorModeValue(
    "colors.primary.emphasis",
    "colors.primary.emphasis"
  );
  const textColor = useColorModeValue("text.inverse", "text.inverse");
  const shadowColor = useColorModeValue("blackAlpha.300", "blackAlpha.500");
  const focusRingColor = useColorModeValue(
    "colors.primary.200",
    "colors.primary.300"
  );

  // Throttled scroll handler for better performance
  const handleScroll = useCallback(() => {
    if (throttleTimeoutRef.current) {
      clearTimeout(throttleTimeoutRef.current);
    }

    throttleTimeoutRef.current = setTimeout(() => {
      if (typeof window !== "undefined") {
        const scrollY =
          window.pageYOffset || document.documentElement.scrollTop;
        setIsVisible(scrollY > threshold);
      }
    }, throttleDelay);
  }, [threshold, throttleDelay]);

  // Smooth scroll to top with optional custom duration
  const scrollToTop = useCallback(() => {
    if (typeof window === "undefined") return;

    logger.debug("Scrolling to top", { smoothScroll, scrollDuration });

    // Haptic feedback for mobile devices
    if (enableHaptics && navigator.vibrate) {
      try {
        navigator.vibrate(25);
      } catch (error) {
        logger.warn("Haptic feedback not supported", error);
      }
    }

    setIsScrolling(true);

    if (smoothScroll) {
      // Enhanced smooth scrolling with custom duration
      const startPosition = window.pageYOffset;
      const startTime = performance.now();

      const animateScroll = (currentTime: number) => {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / scrollDuration, 1);

        // Easing function for smooth animation
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const newPosition = startPosition * (1 - easeOutCubic);

        window.scrollTo(0, newPosition);

        if (progress < 1) {
          requestAnimationFrame(animateScroll);
        } else {
          setIsScrolling(false);
        }
      };

      requestAnimationFrame(animateScroll);
    } else {
      // Immediate scroll
      window.scrollTo({ top: 0 });
      setIsScrolling(false);
    }
  }, [smoothScroll, scrollDuration, enableHaptics]);

  // Setup scroll event listener with proper cleanup
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Initial check
    handleScroll();

    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (throttleTimeoutRef.current) {
        clearTimeout(throttleTimeoutRef.current);
      }
    };
  }, [handleScroll]);

  // Don't render if configured to hide on mobile and we're on mobile
  if (!showOnMobile && typeof window !== "undefined") {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) return null;
  }

  const iconElement =
    iconType === "heroicons" ? <HiArrowUp /> : <ArrowUpIcon />;

  return (
    <Box
      position="fixed"
      bottom={bottom}
      right={right}
      zIndex={zIndex}
      opacity={isVisible ? 1 : 0}
      visibility={isVisible ? "visible" : "hidden"}
      transform={isVisible && animated ? "translateY(0)" : "translateY(10px)"}
      transition={animated ? "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)" : "none"}
      pointerEvents={isVisible ? "auto" : "none"}
    >
      <IconButton
        aria-label="Scroll to top"
        aria-describedby="scroll-to-top-description"
        icon={iconElement}
        size={size}
        variant="solid"
        bg={bgColor}
        color={textColor}
        boxShadow={`0 4px 12px ${shadowColor}`}
        _hover={{
          bg: hoverBgColor,
          transform: animated ? "translateY(-2px)" : "none",
          boxShadow: `0 6px 16px ${shadowColor}`,
        }}
        _active={{
          transform: animated ? "translateY(0)" : "none",
        }}
        _focus={{
          boxShadow: `0 0 0 3px ${focusRingColor}`,
        }}
        onClick={scrollToTop}
        isLoading={isScrolling}
        transition={animated ? "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)" : "none"}
        borderRadius="full"
        // Mobile-specific optimizations
        sx={{
          "@media (hover: none)": {
            _hover: {
              transform: "none",
            },
          },
        }}
      />

      {/* Hidden description for screen readers */}
      <VisuallyHidden id="scroll-to-top-description">
        Scroll to the top of the page
      </VisuallyHidden>
    </Box>
  );
};

export default ScrollToTopButton;
