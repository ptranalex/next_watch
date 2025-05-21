import React from "react";
import {
  Box,
  Flex,
  useColorModeValue,
  IconButton,
  IconButtonProps,
  BoxProps,
} from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("BottomActionBar");

interface ActionProps extends Omit<IconButtonProps, "aria-label"> {
  icon: React.ReactElement;
  label: string;
  onClick: () => void;
}

interface BottomActionBarProps extends BoxProps {
  actions: ActionProps[];
  show?: boolean;
}

/**
 * BottomActionBar component
 * Displays a fixed action bar at the bottom of the screen on mobile devices
 * Optimized for thumb-reachable interactions
 */
const BottomActionBar: React.FC<BottomActionBarProps> = ({
  actions,
  show = true,
  ...boxProps
}) => {
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  if (!show || actions.length === 0) return null;

  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      zIndex={10}
      bg={bgColor}
      borderTopWidth="1px"
      borderColor={borderColor}
      px={2}
      py={2}
      {...boxProps}
    >
      <Flex justifyContent="space-around" alignItems="center">
        {actions.map((action, index) => {
          const { icon, label, onClick, ...rest } = action;
          return (
            <IconButton
              key={index}
              aria-label={label}
              icon={icon}
              onClick={() => {
                logger.info(`Action clicked: ${label}`);
                // Apply haptic feedback
                if (window.navigator && "vibrate" in window.navigator) {
                  try {
                    window.navigator.vibrate(30);
                  } catch (e) {
                    logger.warn("Vibration not supported", e);
                  }
                }
                onClick();
              }}
              variant="ghost"
              size="lg"
              fontSize="24px"
              borderRadius="full"
              minW="60px"
              height="60px"
              {...rest}
            />
          );
        })}
      </Flex>
    </Box>
  );
};

export default BottomActionBar;
