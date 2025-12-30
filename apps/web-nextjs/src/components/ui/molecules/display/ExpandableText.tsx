import { Button, Text, useTheme } from "@chakra-ui/react";
import { useState, useMemo } from "react";

interface ExpandableTextProps {
  children: string;
  limit?: number;
  showButton?: boolean;
  size?: "sm" | "md" | "lg";
  lineHeight?: "normal" | "tall" | "taller";
}

/**
 * ExpandableText Component
 *
 * A text component that truncates long content and provides a toggle to expand/collapse.
 * Features mobile-optimized touch targets, smooth transitions, and theme integration.
 */
const ExpandableText = ({
  children,
  limit = 300,
  showButton = true,
  size = "md",
  lineHeight = "tall",
}: ExpandableTextProps) => {
  const [expanded, setExpanded] = useState(false);
  const theme = useTheme();

  // Memoize text processing for performance
  const { shouldTruncate, summary, fullText } = useMemo(() => {
    if (!children) {
      return { shouldTruncate: false, summary: "", fullText: "" };
    }

    const trimmedText = children.trim();
    const shouldTruncate = trimmedText.length > limit;

    if (!shouldTruncate) {
      return {
        shouldTruncate: false,
        summary: trimmedText,
        fullText: trimmedText,
      };
    }

    // Find the last complete word within the limit
    let cutoff = limit;
    while (
      cutoff > 0 &&
      trimmedText[cutoff] !== " " &&
      trimmedText[cutoff - 1] !== " "
    ) {
      cutoff--;
    }

    // If we couldn't find a good word break, fall back to character limit
    const summary =
      cutoff > 0
        ? trimmedText.substring(0, cutoff).trim()
        : trimmedText.substring(0, limit);

    return { shouldTruncate: true, summary, fullText: trimmedText };
  }, [children, limit]);

  // Early return for empty content
  if (!children?.trim()) return null;

  // Early return if content doesn't need truncation
  if (!shouldTruncate) {
    return (
      <Text fontSize={size} lineHeight={lineHeight}>
        {fullText}
      </Text>
    );
  }

  return (
    <Text
      fontSize={size}
      lineHeight={lineHeight}
      transition="all 0.2s ease-in-out"
    >
      {expanded ? fullText : `${summary}…`}
      {showButton && (
        <Button
          marginLeft={2}
          size="xs"
          fontWeight="semibold"
          // Use semantic theme colors
          bg="colors.primary"
          color="text.inverse"
          borderRadius="md"
          minHeight="32px" // Ensure touch-friendly target
          minWidth="auto"
          px={3}
          py={1}
          // Theme-integrated hover states
          _hover={{
            bg: "colors.primary.emphasis",
            transform: "translateY(-1px)",
            boxShadow: "sm",
          }}
          _active={{
            transform: "translateY(0)",
            boxShadow: "none",
          }}
          _focus={{
            boxShadow: `0 0 0 3px ${
              theme.colors?.brand?.primary?.[300] || "#63B3ED"
            }66`,
            outline: "none",
          }}
          // Smooth transitions
          transition="all 0.2s ease-in-out"
          // Accessibility improvements
          aria-label={expanded ? "Show less text" : "Show more text"}
          aria-expanded={expanded}
          role="button"
          // Touch optimization
          onTouchStart={(e) =>
            (e.currentTarget.style.transform = "scale(0.95)")
          }
          onTouchEnd={(e) => (e.currentTarget.style.transform = "scale(1)")}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Show less" : "Show more"}
        </Button>
      )}
    </Text>
  );
};

export default ExpandableText;
