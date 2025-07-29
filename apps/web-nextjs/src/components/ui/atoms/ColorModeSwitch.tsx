"use client";

import { HStack, IconButton, useColorMode } from "@chakra-ui/react";
import { HiMoon, HiSun } from "react-icons/hi";
import { useState, useEffect } from "react";

const ColorModeSwitch = () => {
  const { toggleColorMode, colorMode } = useColorMode();
  const [isHydrated, setIsHydrated] = useState(false);

  // Track hydration to prevent icon flash during SSR
  useEffect(() => {
    setIsHydrated(true);
  }, []);

  // During SSR, show moon icon (for dark mode toggle) to avoid flash
  const icon = isHydrated ? (
    colorMode === "dark" ? (
      <HiSun />
    ) : (
      <HiMoon />
    )
  ) : (
    <HiMoon />
  );

  return (
    <HStack>
      <IconButton
        aria-label="Toggle dark mode"
        icon={icon}
        onClick={toggleColorMode}
        fontSize={25}
      />
    </HStack>
  );
};

export default ColorModeSwitch;
