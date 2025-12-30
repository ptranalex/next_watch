# Components

This directory contains all React components used in the application, organized following a structured approach that combines Atomic Design principles with domain-driven design.

## Directory Structure

```
components/
├── ui/               # Pure UI components (Atomic Design)
│   ├── atoms/        # Basic building blocks (buttons, inputs)
│   ├── molecules/    # Combinations of atoms (search bars, cards)
│   ├── organisms/    # Complex UI sections (headers, forms)
│   └── templates/    # Page layouts
├── features/         # Feature-specific components
│   ├── movies/       # All movie-related components
│   ├── actors/       # Actor-related components
│   ├── auth/         # Authentication components
│   └── profile/      # Profile management components
└── mobile/           # Mobile-specific components (legacy)
```

## Development Guidelines

### Component Organization

- **Separate presentation from logic**: Use hooks for data fetching and state management
- **Use domain hooks**: Components should interact with the domain layer via hooks
- **Responsive design**: Components should be responsive by default
- **Device-specific variants**: When necessary, create device-specific variants in the feature directory

### Type Safety

- All components should have proper TypeScript interfaces for their props
- Use descriptive prop names and appropriate defaults
- Prefer domain entity types from `@/domain/entities`

### Performance

- Use React.memo for pure components that render frequently
- Leverage useCallback and useMemo for optimizing render performance
- Implement code-splitting with dynamic imports for larger components

### Accessibility

- All UI components must meet WCAG 2.1 AA standards
- Use semantic HTML elements appropriately
- Ensure keyboard navigation works correctly

## Interaction with Other Layers

- **Domain Layer**: Components consume domain entities via hooks
- **Hooks Layer**: Components use hooks for data fetching and business logic
- **Services Layer**: Components never call services directly; always use hooks

## Best Practices

- Keep components focused on a single responsibility
- Follow the container/presentational pattern for complex components
- Write comprehensive documentation including props and usage examples
- Create appropriate test coverage for each component
