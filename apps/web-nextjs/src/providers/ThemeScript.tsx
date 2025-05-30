import { ColorModeScript } from "@chakra-ui/react";
import { themeConfig } from "@/config/theme-config";

export default function ThemeScript() {
  return <ColorModeScript initialColorMode={themeConfig.initialColorMode} />;
}
