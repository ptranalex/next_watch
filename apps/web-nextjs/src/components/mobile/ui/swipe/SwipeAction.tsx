import React, { useRef, useState, useEffect } from "react";
import { Box, Flex, Text, Icon, useColorModeValue } from "@chakra-ui/react";
import { IconType } from "react-icons";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("SwipeAction");

export interface SwipeActionOption {
  icon: IconType;
  label: string;
  color: string;
  action: () => void;
}

interface SwipeActionProps {
  children: React.ReactNode;
  leftActions?: SwipeActionOption[];
  rightActions?: SwipeActionOption[];
  threshold?: number; // Percentage threshold to trigger action
  disabled?: boolean;
}

/**
 * SwipeAction component
 * Enables swipe gestures on content (swipe left/right for actions)
 * Mobile-first design with haptic feedback
 */
const SwipeAction: React.FC<SwipeActionProps> = ({
  children,
  leftActions = [],
  rightActions = [],
  threshold = 0.4, // 40% of width
  disabled = false,
}) => {
  const [offset, setOffset] = useState(0);
  const [startX, setStartX] = useState(0);
  const [isSwiping, setIsSwiping] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const containerWidth = useRef(0);
  const dragThreshold = 10; // Minimum movement to start drag (px)

  const bgColorLeft = useColorModeValue("red.500", "red.600");
  const bgColorRight = useColorModeValue("blue.500", "blue.600");

  // Apply haptic feedback when actions are triggered
  const applyHapticFeedback = () => {
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(30);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }
  };

  // Calculate max swipe distance based on content width and actions
  useEffect(() => {
    if (contentRef.current) {
      containerWidth.current = contentRef.current.offsetWidth;
    }
  }, [leftActions, rightActions]);

  // Touch event handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    if (disabled) return;

    setStartX(e.touches[0].clientX);
    setIsSwiping(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isSwiping || disabled) return;

    const currentX = e.touches[0].clientX;
    const diff = currentX - startX;

    // Only start swiping after exceeding drag threshold
    if (Math.abs(diff) < dragThreshold) return;

    // Prevent unwanted scrolls while swiping
    e.preventDefault();

    // Calculate max swipe distance based on number of actions
    const leftMaxWidth = leftActions.length * 80;
    const rightMaxWidth = rightActions.length * 80;

    // Apply natural resistance as we swipe further
    let newOffset;
    if (diff > 0) {
      // Swiping right (showing left actions)
      newOffset = Math.min(
        leftMaxWidth,
        diff * 0.7 // Apply resistance
      );
    } else {
      // Swiping left (showing right actions)
      newOffset = Math.max(
        -rightMaxWidth,
        diff * 0.7 // Apply resistance
      );
    }

    setOffset(newOffset);
  };

  const handleTouchEnd = () => {
    if (!isSwiping || disabled) return;
    setIsSwiping(false);

    // Calculate threshold distances
    const leftActionWidth = leftActions.length * 80;
    const rightActionWidth = rightActions.length * 80;

    // If swiped far enough, keep open and trigger feedback
    if (offset > leftActionWidth * threshold && leftActions.length > 0) {
      setOffset(leftActionWidth);
      applyHapticFeedback();
    } else if (
      offset < -rightActionWidth * threshold &&
      rightActions.length > 0
    ) {
      setOffset(-rightActionWidth);
      applyHapticFeedback();
    } else {
      // Not far enough, reset position
      setOffset(0);
    }
  };

  // Execute action and reset position
  const executeAction = (action: () => void) => {
    action();
    applyHapticFeedback();
    setOffset(0);
  };

  return (
    <Box position="relative" overflow="hidden" mb={2}>
      {/* Left actions (revealed by swiping right) */}
      {leftActions.length > 0 && (
        <Flex
          position="absolute"
          left={0}
          top={0}
          bottom={0}
          width={`${leftActions.length * 80}px`}
          bg={bgColorLeft}
          align="center"
          justify="flex-start"
          zIndex={1}
          borderRadius="md"
        >
          {leftActions.map((action, index) => (
            <Flex
              key={`left-${index}`}
              direction="column"
              align="center"
              justify="center"
              width="80px"
              height="100%"
              color="white"
              onClick={() => executeAction(action.action)}
              cursor="pointer"
            >
              <Icon as={action.icon} boxSize={6} mb={1} />
              <Text fontSize="xs">{action.label}</Text>
            </Flex>
          ))}
        </Flex>
      )}

      {/* Right actions (revealed by swiping left) */}
      {rightActions.length > 0 && (
        <Flex
          position="absolute"
          right={0}
          top={0}
          bottom={0}
          width={`${rightActions.length * 80}px`}
          bg={bgColorRight}
          align="center"
          justify="flex-end"
          zIndex={1}
          borderRadius="md"
        >
          {rightActions.map((action, index) => (
            <Flex
              key={`right-${index}`}
              direction="column"
              align="center"
              justify="center"
              width="80px"
              height="100%"
              color="white"
              onClick={() => executeAction(action.action)}
              cursor="pointer"
            >
              <Icon as={action.icon} boxSize={6} mb={1} />
              <Text fontSize="xs">{action.label}</Text>
            </Flex>
          ))}
        </Flex>
      )}

      {/* Content with swipe behavior */}
      <Box
        ref={contentRef}
        position="relative"
        zIndex={2}
        transform={`translateX(${offset}px)`}
        transition={isSwiping ? "none" : "transform 0.3s ease"}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        borderRadius="md"
      >
        {children}
      </Box>
    </Box>
  );
};

export default SwipeAction;
