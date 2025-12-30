# UI Component Library

A comprehensive UI component library following **Atomic Design** principles with TypeScript-first development.

## 🏗️ Architecture

This library is organized using Atomic Design methodology:

```
ui/
├── atoms/           # Basic building blocks
├── molecules/       # Combined functionality
├── organisms/       # Complex interface sections
├── templates/       # Complete page layouts
├── examples/        # Integration examples
└── types.ts         # Legacy (being phased out)
```

## 📝 Type Organization

### New Atomic-Level Type System

Types are now organized by their atomic level for better maintainability and discoverability:

#### **Atoms** (`./atoms/types.ts`)

Basic, indivisible types that serve as building blocks:

- Size variants (`ComponentSize`, `ExtendedComponentSize`)
- Basic interactive elements (`BaseToggleProps`, `IconButtonBaseProps`)
- Loading and error states (`LoadingStateProps`, `ErrorStateProps`)
- Utility types (`VoidCallback`, `WithChildren`, etc.)

#### **Molecules** (`./molecules/types.ts`)

Types for components that combine atoms into focused functionality:

- Form patterns (`BaseFormInputProps`, `FormValidationState`)
- Navigation elements (`NavLinkProps`, `SearchInputProps`)
- Content display (`BaseCardProps`, `ExpandableContentProps`)
- Complex callbacks (`AsyncCallback`, `ChangeHandler`)

#### **Organisms** (`./organisms/types.ts`)

Types for complex interface sections:

- Modal and overlay patterns (`BaseModalProps`, `BaseDrawerProps`)
- Navigation systems (`NavBarProps`, `MobileNavMenuProps`)
- Form organisms (`FormOrganism`, `MultiStepFormProps`)
- Data display (`DataTableProps`, `ContentGridProps`)

#### **Templates** (`./templates/types.ts`)

Types for complete page layouts:

- Layout containers (`BaseContainerProps`, `AppShellProps`)
- Page templates (`BrowseLayoutProps`, `DetailLayoutProps`)
- Specialized layouts (`AuthLayoutProps`, `ErrorLayoutProps`)

## 🔗 Component-Type Integration

### **How Components Use Shared Types**

Components should extend and use the shared atomic-level types instead of defining local interfaces:

#### **✅ Correct Integration Examples**

```typescript
// Atom Component - Extending shared types
import type { BaseToggleProps, ComponentSize } from "../atoms/types";

interface ToggleIconButtonProps extends Omit<BaseToggleProps, "onToggle"> {
  icon: React.ReactElement;
  onToggle: () => void;
}

// Molecule Component - Using multiple type levels
import type { BaseFormInputProps, ChangeHandler } from "../molecules/types";

interface FormInputProps extends Omit<BaseFormInputProps, "onChange"> {
  value: string;
  onChange: ChangeHandler<string>;
}

// Organism Component - Extending complex types
import type { BaseModalProps } from "../organisms/types";
import type { VoidCallback, AsyncCallback } from "../atoms/types";

interface ConfirmationModalProps extends BaseModalProps {
  onConfirm: AsyncCallback;
  onCancel: VoidCallback;
}
```

#### **❌ Avoid These Anti-Patterns**

```typescript
// Don't create local interfaces when shared types exist
interface LocalModalProps {
  // ❌ BaseModalProps already exists
  isOpen: boolean;
  onClose: () => void;
  // ...
}

// Don't define callbacks inline when shared types exist
interface BadProps {
  onClick: () => void; // ❌ Use VoidCallback instead
  onChange: (value: string) => void; // ❌ Use ChangeHandler<string>
}

// Don't import from legacy types
import type { BaseModalProps } from "../types"; // ❌ Use "../organisms/types"
```

### **Real Integration Examples**

#### **1. Atom Integration**

```typescript
// atoms/ToggleIconButton.tsx
import type { BaseToggleProps } from "./types";

interface ToggleIconButtonProps extends Omit<BaseToggleProps, "onToggle"> {
  icon: React.ReactElement;
  onToggle: () => void; // Simplified from BaseToggleProps
}

const ToggleIconButton: React.FC<ToggleIconButtonProps> = ({
  isActive, // From BaseToggleProps
  size, // From BaseToggleProps
  isLoading, // From BaseToggleProps
  ariaLabel, // From BaseToggleProps
  onToggle,
  icon,
}) => {
  // Implementation using all shared prop types
};
```

#### **2. Molecule Integration**

```typescript
// molecules/form/FormInput.tsx
import type { BaseFormInputProps, ChangeHandler } from "../types";

interface FormInputProps extends Omit<BaseFormInputProps, "onChange"> {
  value: string;
  onChange: ChangeHandler<string>; // Using shared callback type
}

const FormInput: React.FC<FormInputProps> = ({
  label, // From BaseFormInputProps
  error, // From BaseFormInputProps
  helpText, // From BaseFormInputProps
  size, // From BaseFormInputProps
  isRequired, // From BaseFormInputProps
  value,
  onChange,
}) => {
  // Implementation using shared form patterns
};
```

#### **3. Organism Integration**

```typescript
// organisms/BaseModal.tsx
import type { BaseModalProps } from "./types";

interface ExtendedBaseModalProps extends BaseModalProps {
  isCentered?: boolean; // Component-specific addition
}

const BaseModal: React.FC<ExtendedBaseModalProps> = ({
  isOpen, // From BaseModalProps
  onClose, // From BaseModalProps
  title, // From BaseModalProps
  size, // From BaseModalProps
  children, // From BaseModalProps
  isCentered,
}) => {
  // Implementation using shared modal patterns
};
```

## 📦 Import Patterns

### Recommended (Atomic-Level)

```typescript
// Import from specific atomic levels
import type {
  ComponentSize,
  LoadingStateProps,
} from "@/components/ui/atoms/types";
import type {
  BaseFormInputProps,
  AsyncCallback,
} from "@/components/ui/molecules/types";
import type { BaseModalProps } from "@/components/ui/organisms/types";
import type { BrowseLayoutProps } from "@/components/ui/templates/types";

// Or import from level index files
import type { ComponentSize } from "@/components/ui/atoms";
import type { BaseFormInputProps } from "@/components/ui/molecules";
```

### Legacy (Deprecated)

```typescript
// Avoid - will be removed in future version
import type { ComponentSize, BaseModalProps } from "@/components/ui/types";
```

### Main Index (Convenience)

```typescript
// Acceptable for main exports
import type { ComponentSize, BaseModalProps } from "@/components/ui";
```

## 🧩 Component Development

### Creating New Components

1. **Determine Atomic Level**: Decide if your component is an atom, molecule, organism, or template
2. **Check Existing Types**: Look for shared types that match your component's needs
3. **Extend Shared Types**: Use `extends` or `Omit` to build upon existing type patterns
4. **Define Types**: Add new types to the appropriate atomic level (`./[level]/types.ts`)
5. **Implement Component**: Create the component using the shared types
6. **Export from Index**: Add exports to both the level index and main index

### Type Reuse Guidelines

- **ALWAYS** use shared types instead of creating local interfaces
- Import shared callbacks (`AsyncCallback`, `ChangeHandler`) instead of defining inline
- Extend existing interfaces when adding new props
- Use proper type inheritance with `extends`

## 🔄 Migration Guide

### For Existing Components

1. **Audit Current Types**: Identify local interfaces that could use shared types
2. **Update Imports**: Change from main `types.ts` to atomic-level imports
3. **Replace Local Types**: Use shared types with `extends` or `Omit` as needed
4. **Update Props**: Ensure component props use shared callback types
5. **Test Integration**: Verify all type checking passes

### Example Migration

```typescript
// Before - Local interface
interface LocalModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

// After - Using shared types
import type { BaseModalProps } from "../organisms/types";

interface MyModalProps extends BaseModalProps {
  // Add only component-specific props
  customAction?: React.ReactNode;
}
```

## 🚨 Anti-Patterns

### Avoid These Patterns

- ❌ Creating local interfaces when shared types exist
- ❌ Using `any` type (prefer `unknown` if needed)
- ❌ Importing from the legacy `types.ts` file
- ❌ Defining callback types inline instead of using shared ones
- ❌ Creating circular dependencies between atomic levels

### Code Smells

- Components longer than 200 lines (consider splitting)
- More than 10 props (consider grouping)
- Type definitions duplicated across files
- Missing type inheritance where appropriate

## 🔮 Future Plans

- **Phase 1**: ✅ Organize types by atomic level
- **Phase 2**: 🚧 Update all components to use new type imports
- **Phase 3**: 🔜 Remove legacy `types.ts` file
- **Phase 4**: 🔜 Add comprehensive type validation and testing

## 📚 Best Practices

1. **Type Hierarchy**: Follow the atomic design hierarchy for type organization
2. **Consistent Naming**: Use descriptive, consistent names across similar components
3. **Proper Inheritance**: Use `extends` for related interfaces
4. **Documentation**: Include JSDoc comments for all public types
5. **Import Organization**: Import types last with `type` prefix
6. **Component Integration**: Always extend shared types instead of creating local ones

This organization ensures maintainable, discoverable, and reusable types across the entire UI component library.
