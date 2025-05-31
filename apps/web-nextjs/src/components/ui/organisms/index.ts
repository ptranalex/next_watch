/**
 * Organisms Index
 *
 * Export point for all organism components and their types.
 * Organisms combine molecules and atoms to create complete interface sections.
 */

/**
 * Organism Components
 *
 * Complex components that combine molecules and atoms to create complete
 * interface sections with specific business logic.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  BaseModalProps,
  BaseBottomSheetProps,
  BaseDrawerProps,
  NavSectionProps,
  HeaderProps,
  SectionBasedHeaderProps,
  MobileNavDrawerProps,
  ControlledMobileNavDrawerProps,
  FormOrganism,
  MultiStepFormProps,
  DataTableProps,
  ContentGridProps,
  PageHeaderProps,
} from "./types";

// ============================================================================
// Components
// ============================================================================

// Modal organisms
export { default as BaseModal } from "./BaseModal";

// Navigation organisms (commented out - to be implemented)
// export { default as NavBar } from "./navigation/NavBar";
// export { default as MobileNavMenu } from "./navigation/MobileNavMenu";

// Form organisms (to be implemented)
// export { default as FormOrganism } from "./form/FormOrganism";
// export { default as MultiStepForm } from "./form/MultiStepForm";

// Data display organisms (to be implemented)
// export { default as DataTable } from "./data/DataTable";
// export { default as ContentGrid } from "./data/ContentGrid";

// Layout organisms (to be implemented)
// export { default as PageHeader } from "./layout/PageHeader";

// Layout components
export { default as AppShell } from "../layout/AppShell";

// Navigation components
export { default as SideBar } from "./navigation/SideBar";
// export { default as Header } from "./navigation/Header";
