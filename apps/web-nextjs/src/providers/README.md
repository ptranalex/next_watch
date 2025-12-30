# Application Providers

This directory contains React Context providers that supply global state and functionality to the application.

## Current Providers

- **AuthProvider**: Manages authentication state and user sessions
- **ThemeScript**: Provides theme initialization for the application
- **ResponsiveContext**: Provides responsive design utilities and device detection
- **MovieQueryContext**: Manages global state for movie queries and filters

## Guidelines

- Providers should be focused on a single responsibility
- Export both the provider component and a hook to access the context
- Ensure providers are performant and don't cause unnecessary re-renders
- Document the shape of the context and how to use it properly
- Place all application-level providers in this directory, not in the components directory

## Usage

Providers should be imported in the application's layout or page files, typically wrapping the main content:

```tsx
import { AuthProvider } from "@/providers/AuthProvider";

export default function RootLayout({ children }) {
  return <AuthProvider>{children}</AuthProvider>;
}
```
