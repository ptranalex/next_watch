"use client";

import { extendTheme, type ThemeConfig } from "@chakra-ui/react";

const config: ThemeConfig = {
  initialColorMode: "system",
  useSystemColorMode: true,
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

// Define the application's color palette
const colors = {
  // Brand colors
  brand: {
    primary: {
      100: "***REMOVED***FFFFFF",
      200: "***REMOVED***E2EEFC",
      300: "***REMOVED***C6DCF9",
      400: "***REMOVED***A9CBF6",
      500: "***REMOVED***8CB9F3",
      600: "***REMOVED***70A8F1",
      700: "***REMOVED***5396EE",
      800: "***REMOVED***3784EB",
      900: "***REMOVED***1A73E8", // your brand blue
    },
    secondary: {
      100: "***REMOVED***FFFFFF",
      200: "***REMOVED***B3FEF8",
      300: "***REMOVED***99F4ED",
      400: "***REMOVED***80EAE2",
      500: "***REMOVED***66E0D6",
      600: "***REMOVED***4CD6CB",
      700: "***REMOVED***33CCC0",
      800: "***REMOVED***1AC2B4",
      900: "***REMOVED***00B8A9", // secondary accent teal
    },
  },

  // Semantic colors - these provide meaning to your interface elements
  semantic: {
    // Feedback and status colors
    error: {
      light: "red.500",
      dark: "red.300",
    },
    success: {
      light: "green.500",
      dark: "green.300",
    },
    warning: {
      light: "orange.500",
      dark: "orange.300",
    },
    info: {
      light: "blue.500",
      dark: "blue.300",
    },
  },
};

// Define semantic tokens for easy reference
const semanticTokens = {
  colors: {
    // Brand color tokens
    "colors.primary": {
      default: "brand.primary.900",
      _dark: "brand.primary.500",
    },
    "colors.primary.lighter": {
      default: "brand.primary.700",
      _dark: "brand.primary.400",
    },
    "colors.primary.darker": {
      default: "brand.primary.800",
      _dark: "brand.primary.600",
    },
    "colors.secondary": {
      default: "brand.secondary.900",
      _dark: "brand.secondary.500",
    },
    "colors.secondary.lighter": {
      default: "brand.secondary.700",
      _dark: "brand.secondary.400",
    },
    "colors.secondary.darker": {
      default: "brand.secondary.800",
      _dark: "brand.secondary.600",
    },

    // Text colors
    "text.primary": {
      default: "gray.800",
      _dark: "white",
    },
    "text.secondary": {
      default: "gray.600",
      _dark: "gray.300",
    },
    "text.tertiary": {
      default: "gray.500",
      _dark: "gray.400",
    },
    "text.inverse": {
      default: "white",
      _dark: "gray.800",
    },

    // Background colors
    "bg.primary": {
      default: "gray.50",
      _dark: "gray.800",
    },
    "bg.secondary": {
      default: "gray.100",
      _dark: "gray.700",
    },
    "bg.tertiary": {
      default: "gray.200",
      _dark: "gray.600",
    },

    // Feedback colors
    "feedback.error": {
      default: "semantic.error.light",
      _dark: "semantic.error.dark",
    },
    "feedback.success": {
      default: "semantic.success.light",
      _dark: "semantic.success.dark",
    },
    "feedback.warning": {
      default: "semantic.warning.light",
      _dark: "semantic.warning.dark",
    },
    "feedback.info": {
      default: "semantic.info.light",
      _dark: "semantic.info.dark",
    },
  },
};

const theme = extendTheme({
  config,
  breakpoints,
  space,
  fonts,
  textStyles,
  sizes,
  zIndices,
  semanticTokens,
  colors,
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
        bg: "bg.primary",
        color: "text.primary",
        height: "100%", // Explicit height helps with positioning context
        // Removing overflowX: "hidden" to fix sticky header positioning
      },
      body: {
        bg: "bg.primary",
        color: "text.primary",
        minHeight: "100%",
        // We MUST NOT set overflowX: "hidden" here - it breaks sticky positioning by creating a new containing block
        // that prevents elements with position: sticky from working properly
        // When overflow properties are set, they create a new containing block for sticky positioned elements
      },
      // Improve tap highlights
      "a, button": {
        WebkitTapHighlightColor: "rgba(0, 0, 0, 0)",
      },
    },
  },
});

export default theme;
