***REMOVED*** Error Handling Design Patterns

This document outlines the reusable design patterns implemented for consistent error handling across page components.

***REMOVED******REMOVED*** 🎯 Design Patterns Overview

***REMOVED******REMOVED******REMOVED*** 1. **Error State Management Pattern** (`useErrorHandling`)

***REMOVED******REMOVED******REMOVED*** 2. **Error UI Component Pattern** (`ErrorStateDisplay`)

***REMOVED******REMOVED******REMOVED*** 3. **Page Error Boundary Pattern** (`PageErrorBoundary`)

***REMOVED******REMOVED******REMOVED*** 4. **Centralized Error Categorization Pattern**

---

***REMOVED******REMOVED*** 🔧 Pattern Implementations

***REMOVED******REMOVED******REMOVED*** 1. Error State Management Pattern

**File**: `src/hooks/useErrorHandling.ts`

**Purpose**: Centralizes error analysis, logging, and action handling logic.

```tsx
const { analyzeError, logError, handleRetry, handleGoBack } = useErrorHandling({
  pageId: "genre-page",
  resourceId: genreId,
  resourceName: genreName,
  refetch,
});
```

**Benefits**:

- ✅ Consistent error categorization across all pages
- ✅ Standardized logging with context
- ✅ Reusable retry and navigation logic
- ✅ Type-safe error analysis

***REMOVED******REMOVED******REMOVED*** 2. Error UI Component Pattern

**File**: `src/components/ui/feedback/ErrorStateDisplay.tsx`

**Purpose**: Provides consistent error UI with configurable content and actions.

```tsx
<ErrorStateDisplay
  title="Genre Not Found"
  description="The genre you're looking for doesn't exist."
  actions={[
    { label: "Retry", onClick: handleRetry, variant: "primary" },
    { label: "Go Back", onClick: handleGoBack, variant: "secondary" },
  ]}
/>
```

**Benefits**:

- ✅ Consistent styling and accessibility
- ✅ Configurable actions and content
- ✅ Responsive design built-in
- ✅ Focus management for accessibility

***REMOVED******REMOVED******REMOVED*** 3. Page Error Boundary Pattern

**File**: `src/components/ui/layout/PageErrorBoundary.tsx`

**Purpose**: High-level wrapper that combines error handling logic with consistent layout.

```tsx
<PageErrorBoundary
  error={error}
  pageId="genre-page"
  resourceId={genreId}
  resourceName={genreName}
  refetch={refetch}
  title={<Heading>Genre Title</Heading>}
  errorMessages={{
    notFound: {
      title: "Genre Not Found",
      description: "Custom message for genre not found",
    },
  }}
>
  <YourPageContent />
</PageErrorBoundary>
```

**Benefits**:

- ✅ One-line error handling integration
- ✅ Layout consistency with MovieBrowseLayout
- ✅ Customizable error messages per page
- ✅ Automatic error logging and analysis

---

***REMOVED******REMOVED*** 🚀 Usage Examples

***REMOVED******REMOVED******REMOVED*** Before (Manual Error Handling)

```tsx
// ❌ Repetitive, inconsistent error handling
const GenrePage = ({ genreId }) => {
  const { error, refetch } = useGenrePage(genreId);

  if (error) {
    const apiError = error as { status?: number };
    if (apiError.status === 404) {
      return (
        <MovieBrowseLayout title={title}>
          <div className="text-center py-10">
            <h2>Genre Not Found</h2>
            <p>The genre doesn't exist</p>
            <button onClick={() => window.history.back()}>Go Back</button>
          </div>
        </MovieBrowseLayout>
      );
    }
    // More repetitive error handling...
  }

  return <YourContent />;
};
```

***REMOVED******REMOVED******REMOVED*** After (Pattern-Based Error Handling)

```tsx
// ✅ Clean, reusable, consistent error handling
const GenrePage = ({ genreId }) => {
  const { error, refetch, genre, genreName } = useGenrePage(genreId);

  return (
    <PageErrorBoundary
      error={error}
      pageId="genre-page"
      resourceId={genreId}
      resourceName={genreName}
      refetch={refetch}
      title={<Heading>{genreName} Movies</Heading>}
    >
      <MovieBrowseLayout title={title}>
        <YourContent />
      </MovieBrowseLayout>
    </PageErrorBoundary>
  );
};
```

---

***REMOVED******REMOVED*** 📋 Error Categories

***REMOVED******REMOVED******REMOVED*** 1. **404 Not Found**

- **UI**: "Resource Not Found" with go back action
- **Use Case**: Genre/Actor/Movie doesn't exist
- **Actions**: Go Back only

***REMOVED******REMOVED******REMOVED*** 2. **Network/Server Errors (500+)**

- **UI**: "Connection Problem" with retry option
- **Use Case**: Server down, network issues
- **Actions**: Retry, Go Back

***REMOVED******REMOVED******REMOVED*** 3. **Client Errors (400-499)**

- **UI**: "Unable to Load Resource" with error details
- **Use Case**: Bad request, unauthorized, etc.
- **Actions**: Try Again, Go Back

---

***REMOVED******REMOVED*** 🔄 Migration Guide

***REMOVED******REMOVED******REMOVED*** Step 1: Replace Manual Error Handling

```tsx
// Remove manual error handling code
if (error) {
  // Remove this entire block
}
```

***REMOVED******REMOVED******REMOVED*** Step 2: Wrap with PageErrorBoundary

```tsx
return (
  <PageErrorBoundary
    error={error}
    pageId="your-page-id"
    resourceId={resourceId}
    resourceName={resourceName}
    refetch={refetch}
    title={yourTitle}
  >
    {/* Your existing success content */}
  </PageErrorBoundary>
);
```

***REMOVED******REMOVED******REMOVED*** Step 3: Customize Error Messages (Optional)

```tsx
<PageErrorBoundary
  // ... other props
  errorMessages={{
    notFound: {
      title: "Custom Not Found Title",
      description: "Custom description for your resource type"
    }
  }}
>
```

---

***REMOVED******REMOVED*** 🎨 Styling Customization

***REMOVED******REMOVED******REMOVED*** Button Variants

```tsx
// Available button variants in ErrorStateDisplay
actions={[
  { label: 'Primary Action', variant: 'primary' },   // Blue button
  { label: 'Secondary Action', variant: 'secondary' } // Gray button
]}
```

***REMOVED******REMOVED******REMOVED*** Custom Styling

```tsx
<ErrorStateDisplay
  className="custom-error-styles"
  icon={<YourCustomIcon />}
  // ... other props
/>
```

---

***REMOVED******REMOVED*** 🧪 Testing Patterns

***REMOVED******REMOVED******REMOVED*** Testing Error States

```tsx
// Test error categorization
const { analyzeError } = useErrorHandling({
  pageId: "test",
  resourceId: 1,
});

const notFoundError = { status: 404 };
const result = analyzeError(notFoundError);
expect(result.isNotFound).toBe(true);
```

***REMOVED******REMOVED******REMOVED*** Testing Error UI

```tsx
// Test error display
render(
  <ErrorStateDisplay
    title="Test Error"
    description="Test description"
    actions={[{ label: "Test Action", onClick: mockFn }]}
  />
);

expect(screen.getByText("Test Error")).toBeInTheDocument();
```

---

***REMOVED******REMOVED*** 🔮 Future Enhancements

***REMOVED******REMOVED******REMOVED*** Planned Improvements

1. **Error Analytics Integration**

   - Automatic error tracking
   - Performance monitoring
   - User behavior analysis

2. **Offline Support**

   - Offline detection
   - Cached data fallbacks
   - Sync when online

3. **A/B Testing Integration**

   - Different error messages
   - Action button variations
   - Recovery flow optimization

4. **Internationalization**
   - Multi-language error messages
   - Cultural context adaptation
   - RTL layout support

---

***REMOVED******REMOVED*** 📚 Related Patterns

- **Loading State Patterns**: See skeleton loading implementations
- **Data Fetching Patterns**: See React Query hook patterns
- **Layout Patterns**: See MovieBrowseLayout and responsive patterns
- **Component Composition Patterns**: See compound component examples
