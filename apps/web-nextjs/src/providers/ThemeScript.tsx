"use client";

import { ColorModeScript } from "@chakra-ui/react";
import theme from "@/theme";

export default function ThemeScript() {
  return <ColorModeScript initialColorMode={theme.config.initialColorMode} />;
}
