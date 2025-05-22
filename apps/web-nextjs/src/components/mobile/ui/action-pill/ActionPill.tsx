import React, { ReactNode } from "react";
import {
  Text,
  Flex,
  useColorModeValue,
  Divider,
  FlexProps,
  BoxProps,
} from "@chakra-ui/react";

export interface ActionPillItem {
  id: string;
  label: string;
  badge?: string | number;
  icon?: ReactNode;
  onClick: () => void;
  /**
   * Whether the action is currently active/toggled on
   */
  active?: boolean;
  /**
   * Whether the action is disabled
   */
  disabled?: boolean;
  /**
   * Optional color to use when the action is active
   */
  activeColor?: string;
}

export interface ActionPillProps {
  /**
   * Array of action items to display in the pill
   */
  actions: ActionPillItem[];

  /**
   * Optional custom styling for the pill container
   */
  containerStyle?: BoxProps;

  /**
   * Optional custom styling for each action button
   */
  actionStyle?: FlexProps;

  /**
   * Direction of the pill - horizontal or vertical
   */
  direction?: "row" | "column";

  /**
   * Enable haptic feedback on action button press
   */
  enableHaptics?: boolean;

  /**
   * Position of the pill on the screen
   */
  position?: {
    bottom?: string | number;
    top?: string | number;
    left?: string | number;
    right?: string | number;
  };

  /**
   * Custom styling for the divider between actions
   */
  dividerProps?: {
    show?: boolean;
    color?: string;
    thickness?: number;
  };

  /**
   * Default active color if not specified in the action item
   */
  defaultActiveColor?: string;
}

/**
 * ActionPill component - Generic pill-shaped control with configurable actions
 * Designed to provide quick access to common actions in a mobile interface
 */
const ActionPill: React.FC<ActionPillProps> = ({
  actions,
  containerStyle,
  actionStyle,
  direction = "row",
  enableHaptics = true,
  position = { bottom: "20px" },
  dividerProps = { show: true },
  defaultActiveColor,
}) => {
  // Default colors
  const bgColor = useColorModeValue(
    "rgba(33, 33, 33, 0.9)",
    "rgba(26, 32, 44, 0.9)"
  );
  const textColor = "white";
  const dividerColor = "gray.600";
  const activeButtonBg = useColorModeValue(
    "rgba(255, 255, 255, 0.1)",
    "rgba(255, 255, 255, 0.1)"
  );
  const disabledOpacity = 0.5;

  // Helper function for haptic feedback
  const triggerHaptics = () => {
    if (enableHaptics && window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(30);
      } catch {
        console.warn("Vibration not supported");
      }
    }
  };

  // Handler for action click with haptic feedback
  const handleActionClick = (action: ActionPillItem) => {
    return () => {
      if (action.disabled) return;
      triggerHaptics();
      action.onClick();
    };
  };

  // Default container props
  const defaultContainerProps: BoxProps = {
    position: "fixed",
    bottom: position.bottom,
    top: position.top,
    left: position.left ?? "50%",
    right: position.right,
    transform:
      position.left === undefined && position.right === undefined
        ? "translateX(-50%)"
        : undefined,
    zIndex: 10,
    width: "90%",
    maxWidth: "380px",
    borderRadius: "full",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.25)",
    backgroundColor: bgColor,
    color: textColor,
    overflow: "hidden",
    ...containerStyle,
  };

  // Helper function to style the icon based on active state
  const getStyledIcon = (action: ActionPillItem) => {
    if (!action.icon) return null;

    const iconColor =
      action.active && (action.activeColor || defaultActiveColor)
        ? action.activeColor || defaultActiveColor
        : undefined;

    // Clone the icon element with proper size and color
    return React.cloneElement(action.icon as React.ReactElement, {
      size: 20,
      color: iconColor,
    });
  };

  return (
    <Flex {...defaultContainerProps} flexDirection={direction}>
      {actions.map((action, index) => (
        <React.Fragment key={action.id}>
          {/* Render divider between actions (except before the first one) */}
          {index > 0 && dividerProps.show && (
            <Divider
              orientation={direction === "row" ? "vertical" : "horizontal"}
              height={direction === "row" ? "auto" : undefined}
              width={direction === "column" ? "auto" : undefined}
              borderColor={dividerProps.color || dividerColor}
              borderWidth={dividerProps.thickness}
            />
          )}

          {/* Action Button */}
          <Flex
            as="button"
            flex={1}
            align="center"
            justify="center"
            py={2.5}
            px={3}
            _hover={!action.disabled ? { bg: activeButtonBg } : undefined}
            transition="all 0.2s"
            opacity={action.disabled ? disabledOpacity : 1}
            cursor={action.disabled ? "not-allowed" : "pointer"}
            bg={action.active ? activeButtonBg : undefined}
            onClick={handleActionClick(action)}
            {...actionStyle}
          >
            {getStyledIcon(action)}

            {action.label && (
              <Text ml={action.icon ? 1.5 : 0} fontWeight="medium">
                {action.label} {action.badge && `(${action.badge})`}
              </Text>
            )}
          </Flex>
        </React.Fragment>
      ))}
    </Flex>
  );
};

export default ActionPill;
