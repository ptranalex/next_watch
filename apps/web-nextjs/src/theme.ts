import { extendTheme, ThemeConfig } from "@chakra-ui/react";

const config: ThemeConfig = {
  initialColorMode: "dark",
};

const theme = extendTheme({
  config,
  colors: {
    // gray: {
    //   50: "***REMOVED***f9f9f9",
    //   100: "***REMOVED***ededed",
    //   200: "***REMOVED***d3d3d3",
    //   300: "***REMOVED***b3b3b3",
    //   400: "***REMOVED***a0a0a0",
    //   500: "***REMOVED***898989",
    //   600: "***REMOVED***6c6c6c",
    //   700: "***REMOVED***202020",
    //   800: "***REMOVED***121212",
    //   900: "***REMOVED***111",
    // },
  },
});

export default theme;
