import type { ThemeConfig } from "@chakra-ui/react";

/**
 * Theme configuration that can be used server-side
 * This is a subset of the full theme that doesn't require client-side APIs
 */
export const themeConfig: ThemeConfig = {
  initialColorMode: "system",
  useSystemColorMode: true,
  cssVarPrefix: "nextwatch",
};

export default themeConfig;
