# Next Watch - Cursor Rules Overview

A comprehensive set of development patterns and rules for building consistent, maintainable, and scalable Next.js applications.

## 📚 Rule Categories

### 🏗️ [01. Architecture & Directory Structure](./01-architecture.md)

- **Core technology stack** and architectural principles
- **Directory organization** with domain-driven design
- **File structure rules** and naming conventions
- **Domain boundaries** and separation of concerns

### 🎯 [02. Component Development Rules](./02-components.md)

- **Atomic Design hierarchy** implementation
- **Component structure patterns** and lifecycle
- **Performance optimization** with memoization
- **Export patterns** and component organization

### 🔧 [03. TypeScript Type Organization](./03-typescript.md)

- **Type hierarchy** by atomic design levels
- **Shared type interfaces** and callback standardization
- **Import patterns** and type usage rules
- **Domain-specific typing** strategies

### 🔗 [04. Data Flow Patterns](./04-data-flow.md)

- **Hooks-based architecture** organization
- **State management strategy** (React Query + Zustand + Context)
- **Optimistic updates** and data synchronization
- **Error handling** in data flow

### 🎨 [05. Design System Rules](./05-design-system.md)

- **Chakra UI integration** with semantic tokens
- **Responsive design** and mobile-first approach
- **Dark mode support** and accessibility
- **Animation patterns** and layout systems

### 🧰 [06. Development Best Practices](./06-best-practices.md)

- **Structured logging** requirements
- **Error handling patterns** and boundaries
- **Performance optimization** rules
- **Import organization** and code quality

### 🛡️ [07. Quality Assurance & Workflow](./07-quality-assurance.md)

- **Feature development workflow** and checklists
- **Quality standards** with zero tolerance policies
- **Testing strategies** and accessibility requirements
- **Comprehensive anti-patterns** to avoid

## 🚀 Quick Start Guide

### For New Features

1. Review [Architecture Rules](./01-architecture.md) for directory structure
2. Follow [Component Development](./02-components.md) for implementation
3. Use [TypeScript Organization](./03-typescript.md) for type safety
4. Apply [Data Flow Patterns](./04-data-flow.md) for state management
5. Implement [Design System Rules](./05-design-system.md) for UI consistency

### For Code Reviews

1. Check [Quality Assurance](./07-quality-assurance.md) standards
2. Verify [Best Practices](./06-best-practices.md) compliance
3. Ensure [TypeScript](./03-typescript.md) type safety
4. Validate [Component](./02-components.md) structure patterns

## 🎯 Core Principles

### 1. **Layered Architecture**

```
UI Layer (Components) → Business Logic Layer (Hooks) → Data Layer (Services)
```

### 2. **Atomic Design Hierarchy**

```
Atoms → Molecules → Organisms → Templates
```

### 3. **State Management Separation**

- **React Query**: Server state and caching
- **Zustand**: Client state and UI preferences
- **Context**: App-wide concerns (auth, theme)

### 4. **TypeScript-First Development**

- Zero tolerance for `any` types
- Shared interfaces to prevent duplication
- Atomic-level type organization

### 5. **Performance & Accessibility**

- Mobile-first responsive design
- WCAG 2.1 AA compliance
- Optimistic updates for better UX

## 🛡️ Quality Gates

Before any code is committed, ensure:

- [ ] **Zero ESLint warnings**
- [ ] **Zero TypeScript errors**
- [ ] **Zero unused imports**
- [ ] **Proper error boundaries** for async components
- [ ] **Comprehensive logging** for debugging
- [ ] **Mobile responsiveness**
- [ ] **Accessibility compliance**

## 🚨 Critical Anti-Patterns

### Never Do

```typescript
// ❌ Direct API calls in components
useEffect(() => {
  fetch('/api/data'); // Use hooks instead
}, []);

// ❌ Missing error boundaries
<AsyncComponent /> // Wrap with ErrorBoundary

// ❌ Local types when shared types exist
interface Props {
  onClose: () => void; // Use VoidCallback
}

// ❌ Direct color values
<Box bg="gray.100"> // Use semantic tokens

// ❌ Missing logging
const Component = () => {
  // No logger = debugging nightmare
};
```

## 📖 Usage Examples

### Component Structure

```typescript
import React, { useEffect, useCallback } from "react";
import { Box, Button } from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";
import type { ComponentProps } from "./types";

const logger = createLogger("ComponentName");

const ComponentName: React.FC<ComponentProps> = ({ data, onUpdate }) => {
  useEffect(() => {
    logger.debug("Component initialized", { dataId: data.id });
  }, [data.id]);

  const handleAction = useCallback(() => {
    logger.info("Action performed", { dataId: data.id });
    onUpdate(data);
  }, [data, onUpdate]);

  return (
    <Box bg="bg.secondary" color="text.primary">
      <Button onClick={handleAction}>Perform Action</Button>
    </Box>
  );
};

export default ComponentName;
```

### Hook Structure

```typescript
import { useQuery } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";

const logger = createLogger("useCustomHook");

export const useCustomHook = (id: string) => {
  return useQuery({
    queryKey: ["entity", id],
    queryFn: () => {
      logger.debug(`Fetching entity: ${id}`);
      return api.getById(id);
    },
    onError: (error) => {
      logger.error(`Failed to fetch entity ${id}`, { error });
    },
  });
};
```

## 🔄 Rule Updates

These rules evolve with the project. When updating:

1. **Document changes** in the relevant rule file
2. **Update examples** to reflect new patterns
3. **Cross-reference** related rules
4. **Communicate changes** to the team

## 📞 Support

For questions about these rules:

- **Architecture questions**: See [Architecture Rules](./01-architecture.md)
- **Component patterns**: See [Component Development](./02-components.md)
- **Type safety**: See [TypeScript Organization](./03-typescript.md)
- **State management**: See [Data Flow Patterns](./04-data-flow.md)
- **Design system**: See [Design System Rules](./05-design-system.md)
- **Quality standards**: See [Quality Assurance](./07-quality-assurance.md)

---

**These rules ensure enterprise-level code quality, maintainability, and developer experience across the Next.js application.**
