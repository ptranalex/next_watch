***REMOVED*** Components

This directory contains all React components used in the application, organized following a structured approach that combines Atomic Design principles with domain-driven design.

***REMOVED******REMOVED*** Directory Structure

```
components/
├── ui/               ***REMOVED*** Pure UI components (Atomic Design)
│   ├── atoms/        ***REMOVED*** Basic building blocks (buttons, inputs)
│   ├── molecules/    ***REMOVED*** Combinations of atoms (search bars, cards)
│   ├── organisms/    ***REMOVED*** Complex UI sections (headers, forms)
│   └── templates/    ***REMOVED*** Page layouts
├── features/         ***REMOVED*** Feature-specific components
│   ├── movies/       ***REMOVED*** All movie-related components
│   ├── actors/       ***REMOVED*** Actor-related components
│   ├── auth/         ***REMOVED*** Authentication components
│   └── profile/      ***REMOVED*** Profile management components
└── mobile/           ***REMOVED*** Mobile-specific components (legacy)
```

***REMOVED******REMOVED*** Development Guidelines

***REMOVED******REMOVED******REMOVED*** Component Organization

- **Separate presentation from logic**: Use hooks for data fetching and state management
- **Use domain hooks**: Components should interact with the domain layer via hooks
- **Responsive design**: Components should be responsive by default
- **Device-specific variants**: When necessary, create device-specific variants in the feature directory

***REMOVED******REMOVED******REMOVED*** Type Safety

- All components should have proper TypeScript interfaces for their props
- Use descriptive prop names and appropriate defaults
- Prefer domain entity types from `@/domain/entities`

***REMOVED******REMOVED******REMOVED*** Performance

- Use React.memo for pure components that render frequently
- Leverage useCallback and useMemo for optimizing render performance
- Implement code-splitting with dynamic imports for larger components

***REMOVED******REMOVED******REMOVED*** Accessibility

- All UI components must meet WCAG 2.1 AA standards
- Use semantic HTML elements appropriately
- Ensure keyboard navigation works correctly

***REMOVED******REMOVED*** Interaction with Other Layers

- **Domain Layer**: Components consume domain entities via hooks
- **Hooks Layer**: Components use hooks for data fetching and business logic
- **Services Layer**: Components never call services directly; always use hooks

***REMOVED******REMOVED*** Best Practices

- Keep components focused on a single responsibility
- Follow the container/presentational pattern for complex components
- Write comprehensive documentation including props and usage examples
- Create appropriate test coverage for each component
