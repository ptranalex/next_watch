"use client";

import { extendTheme, type ThemeConfig } from "@chakra-ui/react";

const config: ThemeConfig = {
  initialColorMode: "dark",
  useSystemColorMode: false,
  cssVarPrefix: "nextwatch",
};

// Define breakpoints for responsive design
// These follow a mobile-first approach
const breakpoints = {
  base: "0em", // 0px (mobile)
  sm: "30em", // 480px (mobile landscape)
  md: "48em", // 768px (tablet)
  lg: "62em", // 992px (desktop)
  xl: "80em", // 1280px (large desktop)
  "2xl": "96em", // 1536px (extra large desktop)
};

// Define spacing system that works well for both touch and mouse interactions
const space = {
  // Additional spacing for touch targets
  touch: "44px", // Minimum recommended touch target size
  gutter: {
    base: "16px", // Mobile gutter
    sm: "16px",
    md: "24px",
    lg: "32px",
  },
};

// Define fonts with mobile optimization in mind
const fonts = {
  body: "Inter, system-ui, sans-serif",
  heading: "Inter, system-ui, sans-serif",
};

// Text styles with mobile-first adjustments
const textStyles = {
  h1: {
    fontSize: { base: "1.875rem", md: "2.25rem", lg: "3rem" },
    fontWeight: "bold",
    lineHeight: { base: 1.3, md: 1.2 },
  },
  h2: {
    fontSize: { base: "1.5rem", md: "1.875rem", lg: "2.25rem" },
    fontWeight: "semibold",
    lineHeight: { base: 1.4, md: 1.3 },
  },
  h3: {
    fontSize: { base: "1.25rem", md: "1.5rem" },
    fontWeight: "semibold",
    lineHeight: { base: 1.4, md: 1.3 },
  },
  body: {
    fontSize: { base: "1rem", lg: "1.125rem" },
    lineHeight: 1.5,
  },
};

// Sizes based on mobile-first
const sizes = {
  container: {
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
  },
  touch: "44px", // Minimum touch target size
};

// Define z-indices to ensure proper stacking
const zIndices = {
  hide: -1,
  auto: "auto",
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800,
};

const theme = extendTheme({
  config,
  breakpoints,
  space,
  fonts,
  textStyles,
  sizes,
  zIndices,
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
  components: {
    // Add Box component definition first
    Box: {
      // Make sure Box component doesn't interfere with sticky positioning
      baseStyle: {
        // Empty base style to avoid any defaults that might affect positioning
      },
    },
    // Make buttons more touch-friendly by default
    Button: {
      baseStyle: {
        borderRadius: "md",
        minHeight: "44px",
        _focus: {
          boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.6)", // More visible focus indicator
        },
      },
      sizes: {
        lg: {
          h: "56px", // Larger height for better touch targets
          fontSize: "md",
          px: 6,
        },
        md: {
          minH: "44px", // Default to touch-friendly size
          fontSize: "md",
          px: 4,
        },
      },
      defaultProps: {
        size: "md",
      },
    },
    IconButton: {
      baseStyle: {
        borderRadius: "full",
        minHeight: "44px",
        minWidth: "44px",
      },
      sizes: {
        lg: {
          h: "56px", // Larger height for better touch targets
          w: "56px",
          fontSize: "2xl",
        },
        md: {
          h: "44px", // Touch-friendly by default
          w: "44px",
          fontSize: "xl",
        },
      },
      defaultProps: {
        size: "md",
      },
    },
    Input: {
      baseStyle: {
        field: {
          _focus: {
            boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.6)", // More visible focus indicator
          },
        },
      },
      sizes: {
        md: {
          field: {
            h: "44px", // Touch-friendly height
            fontSize: "16px", // Prevents zoom on iOS
            px: 4,
          },
        },
      },
    },
    Select: {
      sizes: {
        md: {
          field: {
            h: "44px", // Touch-friendly height
            fontSize: "16px", // Prevents zoom on iOS
          },
        },
      },
    },
    // Make form elements better on mobile
    Form: {
      baseStyle: {
        helperText: {
          fontSize: "sm",
          mt: 1,
        },
      },
    },
    // Enhance mobile modal experience
    Modal: {
      baseStyle: {
        dialog: {
          mx: { base: 4, md: "auto" },
          my: { base: "auto", md: "3.75rem" },
          borderRadius: { base: "lg", md: "lg" },
        },
      },
    },
  },
  styles: {
    global: {
      // Base styles applied to the entire app
      html: {
        bg: "gray.900",
        color: "whiteAlpha.900",
        height: "100%", // Explicit height helps with positioning context
        overflowX: "hidden",
      },
      body: {
        bg: "gray.900",
        color: "whiteAlpha.900",
        minHeight: "100%",
        // Do not add overflowX: "hidden" here - it breaks sticky positioning by creating a new containing block
        // that prevents elements with position: sticky from working properly
      },
      // Improve tap highlights
      "a, button": {
        WebkitTapHighlightColor: "rgba(0, 0, 0, 0)",
      },
    },
  },
});

export default theme;
