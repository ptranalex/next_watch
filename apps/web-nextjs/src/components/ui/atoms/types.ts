import { ButtonProps } from "@chakra-ui/react";

/**
 * Atomic Component Types
 *
 * Basic, indivisible UI component types that cannot be broken down further.
 * These are the building blocks for more complex components.
 */

// ============================================================================
// Core Primitive Types
// ============================================================================

/** Standard size variants used across UI components */
export type ComponentSize = "sm" | "md" | "lg";

/** Extended size variants for larger components like modals */
export type ExtendedComponentSize = "xs" | "sm" | "md" | "lg" | "xl" | "full";

/** Responsive breakpoint system */
export type ResponsiveBreakpoints = {
  [key in "base" | "xs" | "sm" | "md" | "lg" | "xl"]?: number;
};

// ============================================================================
// Basic Interactive Element Types
// ============================================================================

/** Toggle component base props */
export interface BaseToggleProps {
  isActive: boolean;
  onToggle: (isActive: boolean) => void;
  size?: ComponentSize;
  isLoading?: boolean;
  isDisabled?: boolean;
  ariaLabel?: string;
}

/** Button with icon pattern */
export interface IconButtonBaseProps extends Omit<ButtonProps, "size"> {
  icon: React.ElementType;
  size?: ComponentSize;
  ariaLabel: string;
  tooltip?: string;
}

// ============================================================================
// Basic Display Types
// ============================================================================

/** Skeleton loading props */
export interface SkeletonProps {
  count?: number;
  height?: string | string[];
  width?: string | string[];
  borderRadius?: string;
  animate?: boolean;
}

/** Badge/Tag component props */
export interface BaseBadgeProps {
  variant?: "solid" | "subtle" | "outline";
  colorScheme?: string;
  size?: ComponentSize;
  isRounded?: boolean;
}

// ============================================================================
// Basic Loading and Error States
// ============================================================================

/** Standard loading state props */
export interface LoadingStateProps {
  isLoading?: boolean;
  loadingText?: string;
  loadingSpinner?: boolean;
}

/** Standard error state props */
export interface ErrorStateProps {
  error?: string | null;
  onRetry?: () => void;
  showErrorBoundary?: boolean;
}

// ============================================================================
// Utility Types
// ============================================================================

/** Basic callback types */
export type VoidCallback = () => void;
export type ValueCallback<T> = (value: T) => void;
export type ClickHandler = (event: React.MouseEvent) => void;

/** Basic React patterns */
export interface WithChildren {
  children: React.ReactNode;
}

export interface WithOptionalChildren {
  children?: React.ReactNode;
}

/** Theme-aware component props */
export interface ThemeAwareProps {
  colorScheme?: string;
  variant?: string;
  size?: ComponentSize | ExtendedComponentSize;
}
