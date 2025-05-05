***REMOVED*** Authentication Architecture

This document outlines the authentication architecture used in the Next Watch application.

***REMOVED******REMOVED*** Core Principles

- **Single Source of Truth**: All auth state is managed through a Zustand store
- **Type Safety**: All interfaces and return types are properly typed
- **Separation of Concerns**: API logic is isolated from state management
- **Progressive Enhancement**: Additional auth features can be added without breaking existing functionality

***REMOVED******REMOVED*** Architecture Overview

***REMOVED******REMOVED******REMOVED*** 1. Auth Service (`authService.ts`)

Responsible for all API communication with the backend auth endpoints:

- Login, register, and logout
- Token management (via AuthTokenManager)
- User profile fetching
- Token refresh

***REMOVED******REMOVED******REMOVED*** 2. Auth Store (`auth.ts`)

Central state management for authentication using Zustand:

- Stores user data, authentication status, and errors
- Provides actions for login, register, logout
- Handles token refresh logic
- Persists authentication state

***REMOVED******REMOVED******REMOVED*** 3. Auth Hooks (`useAuth.ts`)

Provides React hooks for consuming auth functionality:

- `useAuth()` - General auth state and actions
- `useLogin()` - Login-specific functionality
- `useRegister()` - Registration-specific functionality
- `useAuthCheck()` - Simple authentication status check
- `useUser()` - Access to current user data

***REMOVED******REMOVED******REMOVED*** 4. Route Protection

Route protection is provided through:

- `useProtectedRoute()` hook - For custom protection logic
- `<ProtectedRoute>` component - For declarative protection

***REMOVED******REMOVED******REMOVED*** 5. Auth Initialization

Auth is initialized on app startup via:

- `<AuthInitializer>` component in app layout

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Basic Authentication

```tsx
import { useLogin } from "@/hooks/useAuth";

function LoginForm() {
  const { login, isLoading, error } = useLogin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(email, password);
    if (success) {
      // Redirect or show success message
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      {/* Form fields */}
      <button type="submit" disabled={isLoading}>
        {isLoading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}
```

***REMOVED******REMOVED******REMOVED*** Protecting Routes

```tsx
// In your page component
import ProtectedRoute from "@/components/auth/ProtectedRoute";

export default function AdminPage() {
  return (
    <ProtectedRoute requiredPermission="admin.access">
      <div>Admin Dashboard Content</div>
    </ProtectedRoute>
  );
}
```

***REMOVED******REMOVED******REMOVED*** Accessing User Data

```tsx
import { useUser } from "@/hooks/useAuth";

function UserProfile() {
  const user = useUser();

  if (!user) return <div>Not logged in</div>;

  return (
    <div>
      <h1>Welcome, {user.username || user.email}</h1>
      <p>Email: {user.email}</p>
    </div>
  );
}
```

***REMOVED******REMOVED******REMOVED*** Conditional Rendering Based on Auth

```tsx
import { useAuthCheck } from "@/hooks/useAuth";

function NavBar() {
  const isAuthenticated = useAuthCheck();

  return (
    <nav>
      <a href="/">Home</a>
      {isAuthenticated ? (
        <>
          <a href="/profile">Profile</a>
          <LogoutButton />
        </>
      ) : (
        <a href="/login">Login</a>
      )}
    </nav>
  );
}
```

***REMOVED******REMOVED*** Setting Up New Pages

When creating a new authenticated page:

1. Wrap your page with `<ProtectedRoute>` if it requires authentication
2. Use auth hooks to access auth state and actions
3. Handle loading and error states appropriately

***REMOVED******REMOVED*** Best Practices

1. Always check auth state before rendering sensitive content
2. Use the appropriate specialized hooks (`useLogin`, `useUser`) when possible
3. Handle auth errors at the UI level
4. Include loading states for better UX
5. For form submissions, prefer async/await with try/catch over promise chains
