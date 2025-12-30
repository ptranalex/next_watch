# Feature Components

This directory contains domain-specific feature components that combine UI elements with business logic.

## Structure

- **movies/**: Movie-related components (listings, details, cards)
- **actors/**: Actor-related components (profiles, filmography)
- **auth/**: Authentication and authorization components
- **profile/**: User profile management components

## Guidelines

- Feature components should be organized by domain, not by UI structure
- Each feature directory should represent a coherent business concept
- Mobile and desktop variants should be together in the same directory
- Use the UI components from `../ui` for building feature components
- Keep business logic in hooks and services when possible
