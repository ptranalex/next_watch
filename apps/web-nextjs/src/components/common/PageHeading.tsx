import { Heading, HeadingProps } from "@chakra-ui/react";
import React from "react";

interface PageHeadingProps extends HeadingProps {
  /**
   * The heading text or element
   */
  children: React.ReactNode;

  /**
   * Optional size variant
   */
  size?: "small" | "medium" | "large";
}

/**
 * PageHeading component
 * Provides consistent, responsive heading styles across the application
 * Automatically adjusts font size, alignment, and spacing based on device
 */
const PageHeading: React.FC<PageHeadingProps> = ({
  children,
  size = "medium",
  ...props
}) => {
  // Font size mapping for different size variants
  const fontSizeMap = {
    small: { base: "lg", sm: "xl", md: "2xl" },
    medium: { base: "xl", sm: "2xl", md: "3xl" },
    large: { base: "2xl", sm: "3xl", md: "4xl" },
  };

  return (
    <Heading
      as="h1"
      fontSize={fontSizeMap[size]}
      marginY={{ base: 3, md: 5 }}
      textAlign={{ base: "center", md: "left" }}
      {...props}
    >
      {children}
    </Heading>
  );
};

export default PageHeading;
