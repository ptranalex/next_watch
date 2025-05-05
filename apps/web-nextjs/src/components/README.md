***REMOVED*** UI Components

This directory contains all the React components used throughout the application, organized by their domain and purpose.

***REMOVED******REMOVED*** 📂 Directory Structure

```
components/
├── common/             ***REMOVED*** Common UI components used across features
│   ├── Button.tsx      ***REMOVED*** Custom button component
│   ├── Card.tsx        ***REMOVED*** Generic card component
│   └── ...             ***REMOVED*** Other common components
├── layout/             ***REMOVED*** Layout components for page structure
│   ├── Navbar.tsx      ***REMOVED*** Top navigation bar
│   ├── LeftNavBar.tsx  ***REMOVED*** Side navigation bar
│   └── Footer.tsx      ***REMOVED*** Footer component
├── movies/             ***REMOVED*** Movie-related components
│   ├── MovieCard.tsx   ***REMOVED*** Movie card component
│   ├── MovieDetail.tsx ***REMOVED*** Movie details component
│   └── ...             ***REMOVED*** Other movie components
├── actors/             ***REMOVED*** Actor-related components
│   ├── ActorCard.tsx   ***REMOVED*** Actor card component
│   └── ...             ***REMOVED*** Other actor components
├── auth/               ***REMOVED*** Authentication-related components
│   ├── LoginForm.tsx   ***REMOVED*** Login form component
│   └── ...             ***REMOVED*** Other auth components
└── user/               ***REMOVED*** User-related components
    ├── ProfileView.tsx ***REMOVED*** User profile component
    └── ...             ***REMOVED*** Other user components
```

***REMOVED******REMOVED*** 🧩 Component Categories

***REMOVED******REMOVED******REMOVED*** Layout Components

Layout components define the overall structure of pages:

- **Navbar**: Top navigation with search, user menu
- **LeftNavBar**: Side navigation for main sections
- **Footer**: Page footer with links and information
- **MainLayout**: Wraps content with consistent layout

***REMOVED******REMOVED******REMOVED*** Feature Components

Feature components are specific to application domains:

- **Movie Components**: Movie cards, details, grids
- **Actor Components**: Actor cards, filmography
- **User Components**: User profile, watchlist
- **Auth Components**: Login, signup, password reset

***REMOVED******REMOVED******REMOVED*** Common Components

Common components are reusable across features:

- **Buttons**: Standard, outline, icon buttons
- **Cards**: Content cards with consistent styling
- **Forms**: Input fields, dropdowns, checkboxes
- **Feedback**: Alerts, toasts, loading indicators

***REMOVED******REMOVED*** 🚀 Component Architecture

Components follow these principles:

1. **Separation of Concerns**: Components should do one thing well
2. **Composition Over Inheritance**: Build complex components via composition
3. **Props Interface**: All components have explicit props interface
4. **Pure Components**: Minimize side effects in components
5. **Responsive Design**: Components adapt to different screen sizes

***REMOVED******REMOVED******REMOVED*** Component Pattern Example

```tsx
import React from "react";
import { Box, Text } from "@chakra-ui/react";
import { Movie } from "@/domain/entities";

interface MovieCardProps {
  movie: Movie;
  isFeatured?: boolean;
  onClick?: (movie: Movie) => void;
}

export const MovieCard: React.FC<MovieCardProps> = ({
  movie,
  isFeatured = false,
  onClick,
}) => {
  const handleClick = () => {
    if (onClick) onClick(movie);
  };

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      p={4}
      onClick={handleClick}
      cursor={onClick ? "pointer" : "default"}
      bg={isFeatured ? "blue.50" : "white"}
    >
      <Text fontWeight="bold">{movie.title}</Text>
      <Text fontSize="sm">{movie.release_date}</Text>
    </Box>
  );
};
```

***REMOVED******REMOVED*** 🔄 Data Flow

Components interact with the application data flow:

1. **Container Components**: Fetch data via hooks, handle state
2. **Presentational Components**: Render data from props
3. **Data Updates**: Pass callbacks to children for updates
4. **Domain Entities**: Components receive domain entities from hooks

***REMOVED******REMOVED*** 📝 Style Guidelines

Components use Chakra UI for styling:

1. **Theme-Based**: Use theme values for colors, spacing, etc.
2. **Responsive Props**: Use responsive array syntax `{base: "value", md: "value"}`
3. **Composition**: Use Chakra's composition pattern (Box, Flex, etc.)
4. **Semantic Elements**: Use proper HTML elements for accessibility

***REMOVED******REMOVED*** 🧪 Testing

Component tests focus on user interactions:

```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { MovieCard } from "./MovieCard";

describe("MovieCard", () => {
  const mockMovie = {
    id: 1,
    title: "Test Movie",
    release_date: "2023-01-01",
  };

  it("displays movie title", () => {
    render(<MovieCard movie={mockMovie} />);
    expect(screen.getByText("Test Movie")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = jest.fn();
    render(<MovieCard movie={mockMovie} onClick={handleClick} />);
    fireEvent.click(screen.getByText("Test Movie"));
    expect(handleClick).toHaveBeenCalledWith(mockMovie);
  });
});
```

***REMOVED******REMOVED*** 📚 Related Documentation

- [Domain Layer](../domain/README.md) - Domain entities used by components
- [Hooks Layer](../hooks/README.md) - React hooks used in container components
