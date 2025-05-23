import type { ExtendedComponentSize, VoidCallback } from "../atoms/types";
import type { NavLinkProps } from "../molecules/types";

/**
 * Organism Component Types
 *
 * Types for complex components that combine molecules and atoms to create
 * complete interface sections with specific business logic.
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

/** Main navigation bar props */
export interface NavBarProps {
  /** Custom logo element */
  logo?: React.ReactNode;
  /** Navigation bar title */
  title?: string;
  /** Whether to show search input */
  showSearch?: boolean;
  /** Whether to show user authentication actions */
  showUserActions?: boolean;
  /** Whether to show mobile menu trigger */
  showMobileMenu?: boolean;
  /** Whether to show color mode switch */
  showColorMode?: boolean;
  /** Custom logo click handler */
  onLogoClick?: VoidCallback;
  /** Additional action elements */
  customActions?: React.ReactNode;
  /** CSS class name for styling */
  className?: string;
  /** Whether search input is currently focused (affects navbar opacity) */
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

/** Mobile navigation menu props - supports both trigger and controlled modes */
export interface MobileNavMenuProps {
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

/** Controlled mobile navigation menu props (when used as controlled component) */
export interface ControlledMobileNavMenuProps {
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
  onSubmit: (data: any) => void | Promise<void>;
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
  onComplete: (data: any) => void;
}

// ============================================================================
// Data Display Organisms
// ============================================================================

/** Data table props */
export interface DataTableProps<T = any> {
  data: T[];
  columns: Array<{
    key: keyof T;
    header: string;
    render?: (value: any, item: T) => React.ReactNode;
    sortable?: boolean;
  }>;
  isLoading?: boolean;
  onSort?: (key: keyof T, direction: "asc" | "desc") => void;
  onRowClick?: (item: T) => void;
  pagination?: {
    page: number;
    total: number;
    onPageChange: (page: number) => void;
  };
}

/** Content grid props */
export interface ContentGridProps<T = any> {
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
