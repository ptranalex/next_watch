import { BoxProps, InputProps } from "@chakra-ui/react";
import type {
  ComponentSize,
  ExtendedComponentSize,
  ResponsiveBreakpoints,
  LoadingStateProps,
  ErrorStateProps,
} from "../atoms/types";

/**
 * Molecular Component Types
 *
 * Types for components that combine multiple atoms to create more complex,
 * reusable UI patterns with specific functionality.
 */

// ============================================================================
// Form Molecules
// ============================================================================

/** Base form input props pattern */
export interface BaseFormInputProps extends Omit<InputProps, "size"> {
  label?: string;
  error?: string | null;
  helpText?: string;
  size?: ComponentSize;
  isRequired?: boolean;
}

/** Form validation state */
export type FormValidationState = "idle" | "validating" | "valid" | "invalid";

/** Form CTA (Call to Action) button props */
export interface BaseFormCTAProps {
  size?: ComponentSize;
  isLoading?: boolean;
  loadingText?: string;
  variant?: "primary" | "secondary" | "tertiary";
  type?: "button" | "submit" | "reset";
  onClick?: () => void;
}

// ============================================================================
// Navigation Molecules
// ============================================================================

/** Navigation link props */
export interface NavLinkProps {
  href: string;
  label: string;
  isActive?: boolean;
  icon?: React.ElementType;
  badge?: string | number;
  isExternal?: boolean;
}

/** Search input component props */
export interface SearchInputProps {
  /** Current search value */
  value?: string;
  /** Callback when search value changes */
  onChange?: (value: string) => void;
  /** Input placeholder text (default: "Search movies...") */
  placeholder?: string;
  /** Callback when search is performed */
  onSearch?: (value: string) => void;
  /** Callback when input is cleared */
  onClear?: () => void;
  /** Whether search is loading */
  isLoading?: boolean;
  /** Search suggestions array */
  suggestions?: string[];
  /** Component size (default: "md") */
  size?: ComponentSize;
  /** Callback when input gains focus */
  onFocus?: () => void;
  /** Callback when input loses focus */
  onBlur?: () => void;
  /** Whether to show keyboard shortcut hint (default: responsive) */
  showHotkey?: boolean;
  /** Custom hotkey combination (default: "meta+k") */
  hotkey?: string;
  /** Whether to enable search suggestions dropdown (default: true) */
  enableSuggestions?: boolean;
  /** Maximum number of suggestions to show (default: 8) */
  maxSuggestions?: number;
  /** Whether to show on mobile devices (default: true) */
  showOnMobile?: boolean;
  /** Custom search icon */
  searchIcon?: React.ElementType;
  /** Whether to enable haptic feedback on mobile (default: true) */
  enableHaptics?: boolean;
  /** Debounce delay for search queries in ms (default: 300) */
  debounceDelay?: number;
  /** Custom z-index for dropdown (default: 1000) */
  dropdownZIndex?: number;
  /** Whether to animate the dropdown (default: true) */
  animated?: boolean;
  /** Whether the input is disabled */
  isDisabled?: boolean;
  /** Error message to display */
  error?: string;
}

// ============================================================================
// Display Molecules
// ============================================================================

/** Combined async state props */
export interface AsyncStateProps extends LoadingStateProps, ErrorStateProps {
  isEmpty?: boolean;
  emptyText?: string;
}

/** Card component base props */
export interface BaseCardProps extends BoxProps {
  variant?: "outline" | "filled" | "elevated" | "unstyled";
  size?: ComponentSize;
  isHoverable?: boolean;
  isClickable?: boolean;
}

/** Expandable content props */
export interface ExpandableContentProps {
  limit?: number;
  showToggle?: boolean;
  expandText?: string;
  collapseText?: string;
  children: React.ReactNode;
}

/** Content with action props */
export interface ContentWithActionProps {
  children: React.ReactNode;
  actionPosition?: "top" | "bottom" | "inline";
  action?: React.ReactNode;
}

// ============================================================================
// Feedback Molecules
// ============================================================================

/** Banner/Alert component props */
export interface BannerProps {
  variant?: "info" | "warning" | "error" | "success";
  title?: string;
  message: string;
  isClosable?: boolean;
  onClose?: () => void;
  action?: React.ReactNode;
}

// ============================================================================
// Utility Molecules
// ============================================================================

/** Sort selector props */
export interface SortSelectorProps<T = string> {
  options: Array<{
    value: T;
    label: string;
  }>;
  value: T;
  onChange: (value: T) => void;
  size?: ComponentSize;
  placeholder?: string;
}

/** Suggestion item props */
export interface SuggestionItemProps {
  text: string;
  isHighlighted?: boolean;
  onClick: () => void;
  onMouseEnter?: () => void;
}

// ============================================================================
// Callback Types
// ============================================================================

export type AsyncCallback = () => Promise<void>;
export type AsyncValueCallback<T> = (value: T) => Promise<void>;
export type ChangeHandler<T = string> = (value: T) => void;
export type SubmitHandler = (event: React.FormEvent) => void;

/**
 * ScrollToTopButton Props
 *
 * Configurable scroll-to-top button with mobile optimization and performance enhancements
 */
export interface ScrollToTopButtonProps {
  /** Scroll threshold to show the button (default: 300px) */
  threshold?: number;
  /** Button position from bottom (default: 6) */
  bottom?: number | string;
  /** Button position from right (default: 6) */
  right?: number | string;
  /** Button size (default: "md") */
  size?: "sm" | "md" | "lg";
  /** Whether to use Chakra UI ArrowUpIcon or HiArrowUp (default: "chakra") */
  iconType?: "chakra" | "heroicons";
  /** Whether to enable smooth scrolling (default: true) */
  smoothScroll?: boolean;
  /** Whether to show on mobile devices (default: true) */
  showOnMobile?: boolean;
  /** Custom scroll duration in ms (default: 500) */
  scrollDuration?: number;
  /** Whether to enable haptic feedback on mobile (default: true) */
  enableHaptics?: boolean;
  /** Throttle delay for scroll events in ms (default: 100) */
  throttleDelay?: number;
  /** Custom z-index (default: 1000) */
  zIndex?: number;
  /** Whether to animate the button appearance (default: true) */
  animated?: boolean;
}
