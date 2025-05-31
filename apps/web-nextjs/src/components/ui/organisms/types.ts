import type { ExtendedComponentSize, VoidCallback } from "../atoms/types";
import type { NavLinkProps } from "../molecules/types";
import { ReactNode } from "react";

/**
 * Organism Component Types
 *
 * Types for complex components that combine molecules and atoms to create
 * complete interface sections with specific business logic.
 */

/**
 * Shared types for organism-level components
 *
 * These types define the interfaces for complex UI components that combine
 * multiple molecules and atoms to create complete UI sections.
 */

// ============================================================================
// Modal and Overlay Organisms
// ============================================================================

/** Standard modal props pattern used across all modal components */
export interface BaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: ExtendedComponentSize;
  children?: React.ReactNode;
}

/** Bottom sheet props for mobile components */
export interface BaseBottomSheetProps extends BaseModalProps {
  showHandle?: boolean;
  isClosable?: boolean;
}

/** Drawer props pattern */
export interface BaseDrawerProps extends BaseModalProps {
  placement?: "left" | "right" | "top" | "bottom";
}

// ============================================================================
// Navigation Organisms
// ============================================================================

/** Navigation section props */
export interface NavSectionProps {
  title?: string;
  links: NavLinkProps[];
  isCollapsible?: boolean;
  defaultOpen?: boolean;
}

/**
 * Props for the main navigation header component
 *
 * Used by both desktop and mobile navigation components to ensure
 * consistent interface and behavior across different screen sizes.
 */
export interface HeaderProps {
  /** Custom logo element (defaults to Next Watch logo) */
  logo?: ReactNode;

  /** Navigation title text (defaults to "Next Watch") */
  title?: string;

  /** Whether to show the search input (default: true) */
  showSearch?: boolean;

  /** Whether to show user authentication actions (default: true) */
  showUserActions?: boolean;

  /** Whether to show color mode toggle (default: true) */
  showColorMode?: boolean;

  /** Custom click handler for logo (defaults to home navigation) */
  onLogoClick?: () => void;

  /** Additional custom action elements */
  customActions?: ReactNode;

  /** CSS class name for custom styling */
  className?: string;

  /** Whether search input is currently focused (affects header opacity) */
  isSearchFocused?: boolean;

  /** Callback when search focus state changes */
  onSearchFocusChange?: (isFocused: boolean) => void;
}

/** Section-based navigation bar props (alternative pattern) */
export interface SectionBasedNavBarProps {
  sections: NavSectionProps[];
  logo?: React.ReactNode;
  actions?: React.ReactNode;
  isMobile?: boolean;
}

/**
 * Props for section-based navigation components
 *
 * Used for navigation components that organize content into distinct sections
 * with different navigation patterns and behaviors.
 */
export interface SectionBasedHeaderProps {
  /** Array of navigation sections */
  sections?: Array<{
    id: string;
    title: string;
    items: Array<{
      id: string;
      label: string;
      href: string;
      icon?: ReactNode;
    }>;
  }>;

  /** Currently active section ID */
  activeSection?: string;

  /** Callback when section changes */
  onSectionChange?: (sectionId: string) => void;
}

/** Mobile navigation drawer props - supports both trigger and controlled modes */
export interface MobileNavDrawerProps {
  /** Custom trigger element (if not provided, default hamburger menu will be used) */
  trigger?: React.ReactNode;
  /** Custom drawer header content */
  header?: React.ReactNode;
  /** Custom drawer footer content */
  footer?: React.ReactNode;
  /** Custom navigation sections content */
  children?: React.ReactNode;
  /** Drawer size */
  size?: "xs" | "sm" | "md" | "lg" | "xl" | "full";
  /** Custom onClose handler */
  onClose?: VoidCallback;
  /** CSS class name for styling */
  className?: string;
}

/** Controlled mobile navigation drawer props (when used as controlled component) */
export interface ControlledMobileNavDrawerProps {
  isOpen: boolean;
  onClose: VoidCallback;
  sections?: NavSectionProps[];
  header?: React.ReactNode;
  footer?: React.ReactNode;
  size?: "xs" | "sm" | "md" | "lg" | "xl" | "full";
}

// ============================================================================
// Form Organisms
// ============================================================================

/** Complex form container props */
export interface FormOrganism {
  title?: string;
  subtitle?: string;
  onSubmit: (data: Record<string, unknown>) => void | Promise<void>;
  isLoading?: boolean;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

/** Multi-step form props */
export interface MultiStepFormProps {
  steps: Array<{
    id: string;
    title: string;
    component: React.ComponentType;
    isValid?: boolean;
  }>;
  currentStep: number;
  onStepChange: (step: number) => void;
  onComplete: (data: Record<string, unknown>) => void;
}

// ============================================================================
// Data Display Organisms
// ============================================================================

/** Data table props */
export interface DataTableProps<T = Record<string, unknown>> {
  data: T[];
  columns: Array<{
    key: keyof T;
    header: string;
    render?: (value: unknown, item: T) => React.ReactNode;
    sortable?: boolean;
  }>;
  isLoading?: boolean;
  onSort?: (key: keyof T, direction: "asc" | "desc") => void;
  onRowClick?: (item: T) => void;
  pagination?: {
    page: number;
    total: number;
    pageSize: number;
    onPageChange: (page: number) => void;
  };
}

/** Content grid props for displaying items in a responsive grid */
export interface ContentGridProps<T = Record<string, unknown>> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  columns?: {
    base: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: string | number;
  isLoading?: boolean;
  loadingComponent?: React.ReactNode;
  emptyComponent?: React.ReactNode;
}

// ============================================================================
// Layout Organisms
// ============================================================================

/** Page header organism props */
export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: Array<{
    label: string;
    href?: string;
  }>;
  actions?: React.ReactNode;
  tabs?: Array<{
    id: string;
    label: string;
    isActive?: boolean;
    onClick?: () => void;
  }>;
}
