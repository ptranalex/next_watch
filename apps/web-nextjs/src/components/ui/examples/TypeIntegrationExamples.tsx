/**
 * Type Integration Examples
 *
 * This file demonstrates how to properly integrate components with
 * the new atomic-level type system.
 */

import React from "react";
import { Box, Button, VStack } from "@chakra-ui/react";

// ============================================================================
// Import Examples - Atomic Level Types
// ============================================================================

// Atoms - Basic building blocks
import type {
  ComponentSize,
  LoadingStateProps,
  VoidCallback,
} from "../atoms/types";

// Molecules - Combined functionality
import type {
  BaseFormInputProps,
  ChangeHandler,
  AsyncCallback,
  SearchInputProps,
} from "../molecules/types";

// Organisms - Complex sections
import type {
  BaseModalProps,
  NavBarProps,
  DataTableProps,
} from "../organisms/types";

// Templates - Page layouts
import type { BrowseLayoutProps, AppShellProps } from "../templates/types";

// ============================================================================
// Example 1: Atom Component Using Shared Types
// ============================================================================

interface ActionButtonProps extends LoadingStateProps {
  label: string;
  size: ComponentSize;
  onClick: VoidCallback;
  variant?: "primary" | "secondary";
}

const ActionButton: React.FC<ActionButtonProps> = ({
  label,
  size,
  onClick,
  variant = "primary",
  isLoading,
  loadingText,
}) => {
  return (
    <Button
      size={size}
      onClick={onClick}
      isLoading={isLoading}
      loadingText={loadingText}
      colorScheme={variant === "primary" ? "blue" : "gray"}
    >
      {label}
    </Button>
  );
};

// ============================================================================
// Example 2: Molecule Component Using Multiple Type Levels
// ============================================================================

interface SmartFormInputProps extends Omit<BaseFormInputProps, "onChange"> {
  value: string;
  onChange: ChangeHandler<string>;
  onAsyncValidate?: AsyncCallback;
  validationDelay?: number;
}

const SmartFormInput: React.FC<SmartFormInputProps> = ({
  value,
  onChange,
  onAsyncValidate,
  label,
  error,
  helpText,
  size = "md",
  isRequired,
  // ... other BaseFormInputProps
}) => {
  // Implementation would use all the shared types
  return <Box>{/* Form input implementation using shared types */}</Box>;
};

// ============================================================================
// Example 3: Organism Component Using Shared Modal Props
// ============================================================================

interface ConfirmationModalProps extends BaseModalProps {
  message: string;
  onConfirm: AsyncCallback;
  onCancel: VoidCallback;
  confirmText?: string;
  cancelText?: string;
  isDestructive?: boolean;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  onClose,
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = "Confirm",
  cancelText = "Cancel",
  isDestructive = false,
  size = "md",
}) => {
  const handleConfirm = async () => {
    await onConfirm();
    onClose();
  };

  return (
    <Box>
      {/* Modal implementation using shared BaseModalProps */}
      {/* This would render the actual modal with confirm/cancel actions */}
    </Box>
  );
};

// ============================================================================
// Example 4: Template Component Using Multiple Organism Types
// ============================================================================

interface DashboardTemplateProps extends AppShellProps {
  navigationProps: NavBarProps;
  dataTableProps: DataTableProps;
  quickActions?: React.ReactNode;
}

const DashboardTemplate: React.FC<DashboardTemplateProps> = ({
  header,
  sidebar,
  footer,
  children,
  navigationProps,
  dataTableProps,
  quickActions,
}) => {
  return (
    <Box>
      {/* Template implementation using shared AppShellProps */}
      {/* Plus navigation and data table using their organism types */}
    </Box>
  );
};

// ============================================================================
// Example 5: Component Composition with Type Safety
// ============================================================================

interface ComposedComponentProps {
  searchProps: SearchInputProps;
  modalProps: BaseModalProps;
  tableProps: DataTableProps;
  size: ComponentSize;
}

const ComposedComponent: React.FC<ComposedComponentProps> = ({
  searchProps,
  modalProps,
  tableProps,
  size,
}) => {
  return (
    <VStack spacing={4}>
      {/* Each component gets properly typed props */}
      {/* SearchInput would use searchProps: SearchInputProps */}
      {/* BaseModal would use modalProps: BaseModalProps */}
      {/* DataTable would use tableProps: DataTableProps */}
    </VStack>
  );
};

// ============================================================================
// Export Examples for Documentation
// ============================================================================

export {
  ActionButton,
  SmartFormInput,
  ConfirmationModal,
  DashboardTemplate,
  ComposedComponent,
};

export type {
  ActionButtonProps,
  SmartFormInputProps,
  ConfirmationModalProps,
  DashboardTemplateProps,
  ComposedComponentProps,
};
