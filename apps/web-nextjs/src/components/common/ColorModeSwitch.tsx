"use client";

import {
  HStack,
  Switch,
  Text,
  useColorMode,
  IconButton,
  Tooltip,
  useBreakpointValue,
} from "@chakra-ui/react";
import { HiSun, HiMoon } from "react-icons/hi2";

interface ColorModeSwitchProps {
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

export default function ColorModeSwitch({
  showLabel = true,
  size = "md",
}: ColorModeSwitchProps) {
  const { colorMode, toggleColorMode } = useColorMode();
  const isMobile = useBreakpointValue({ base: true, md: false });

  // If on mobile or showLabel is false, show icon button
  if (isMobile || !showLabel) {
    return (
      <Tooltip label={colorMode === "dark" ? "Light Mode" : "Dark Mode"}>
        <IconButton
          aria-label="Toggle color mode"
          icon={colorMode === "dark" ? <HiSun /> : <HiMoon />}
          onClick={toggleColorMode}
          variant="ghost"
          size={size}
        />
      </Tooltip>
    );
  }

  // Otherwise show with label
  return (
    <HStack>
      <Switch
        colorScheme="blue"
        isChecked={colorMode === "dark"}
        onChange={toggleColorMode}
        size={size}
      />
      <Text fontSize={size}>
        {colorMode === "dark" ? "Dark Mode" : "Light Mode"}
      </Text>
    </HStack>
  );
}
