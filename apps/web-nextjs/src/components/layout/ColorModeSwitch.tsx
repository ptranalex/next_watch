import { HStack, IconButton, useColorMode } from "@chakra-ui/react";
import { HiMoon, HiSun } from "react-icons/hi";

const ColorModeSwitch = () => {
  const { toggleColorMode, colorMode } = useColorMode();
  return (
    <HStack>
      <IconButton
        aria-label="Toggle dark mode"
        icon={colorMode === "dark" ? <HiSun /> : <HiMoon />}
        onClick={toggleColorMode}
        fontSize={25}
      />
    </HStack>
  );
};

export default ColorModeSwitch;
