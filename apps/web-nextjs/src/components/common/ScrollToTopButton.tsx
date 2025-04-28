"use client";

import { useState, useEffect } from "react";
import { IconButton, Tooltip, useColorModeValue } from "@chakra-ui/react";
import { HiArrowUp } from "react-icons/hi2";

interface ScrollToTopButtonProps {
  showAfter?: number; // pixels of scrolling to show the button
  position?: "right" | "left";
  size?: "sm" | "md" | "lg";
  zIndex?: number;
  withTooltip?: boolean;
  tooltipLabel?: string;
}

export default function ScrollToTopButton({
  showAfter = 400,
  position = "right",
  size = "md",
  zIndex = 10,
  withTooltip = true,
  tooltipLabel = "Scroll to top",
}: ScrollToTopButtonProps) {
  const [isVisible, setIsVisible] = useState(false);
  const bgColor = useColorModeValue("white", "gray.800");
  const shadowColor = useColorModeValue("gray.200", "gray.700");

  useEffect(() => {
    // Show the button when the user scrolls down
    const toggleVisibility = () => {
      if (window.pageYOffset > showAfter) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);

    // Clean up the event listener on unmount
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, [showAfter]);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  if (!isVisible) {
    return null;
  }

  const button = (
    <IconButton
      aria-label="Scroll to top"
      icon={<HiArrowUp />}
      onClick={scrollToTop}
      size={size}
      position="fixed"
      bottom={8}
      right={position === "right" ? 8 : undefined}
      left={position === "left" ? 8 : undefined}
      zIndex={zIndex}
      borderRadius="full"
      boxShadow={`0 4px 12px ${shadowColor}`}
      bg={bgColor}
    />
  );

  return withTooltip ? (
    <Tooltip label={tooltipLabel}>{button}</Tooltip>
  ) : (
    button
  );
}
