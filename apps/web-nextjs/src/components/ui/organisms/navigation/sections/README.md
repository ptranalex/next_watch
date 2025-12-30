# Navigation Sections

This directory contains UI components that form sections of navigation elements across the application.

## Components

- **GenreSection**: Desktop genre navigation section used in sidebar
- **MobileGenreSection**: Mobile-optimized genre navigation with multiple layout options

## Usage Guidelines

- Navigation sections should be composed into larger navigation components
- Keep sections focused on a single category/concern
- For responsive design, use the appropriate section based on device type
- Sections can accept customization props but should have sensible defaults

When adding new navigation sections, follow these patterns:
- Create a new component in this directory
- Export it from the index.ts file
- Update the README to document its purpose
