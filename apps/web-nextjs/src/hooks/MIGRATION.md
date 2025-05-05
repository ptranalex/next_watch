***REMOVED*** Hooks Migration Guide

The hooks directory has been refactored to improve organization and maintainability. This guide will help you update your imports.

***REMOVED******REMOVED*** Import Changes

***REMOVED******REMOVED******REMOVED*** Before

```tsx
// Direct imports from hook files
import { useAuth } from "@/hooks/useAuth";
import { useMovie } from "@/hooks/useMovie";
import { useDebounce } from "@/hooks/useDebounce";
import { useActor } from "@/hooks/actor/useActor";
```

***REMOVED******REMOVED******REMOVED*** After

```tsx
// All imports from main hooks index
import { useAuth, useMovie, useDebounce, useActor } from "@/hooks";
```

***REMOVED******REMOVED*** Migration Steps

1. Find all imports that reference specific hook files:

   ```bash
   grep -r "from \"@/hooks/" --include="*.tsx" --include="*.ts" src/
   ```

2. Update each import to use the main hooks index:

   ```tsx
   // Before
   import { useAuth } from "@/hooks/useAuth";

   // After
   import { useAuth } from "@/hooks";
   ```

3. If you're importing multiple hooks, consolidate them:

   ```tsx
   // Before
   import { useAuth } from "@/hooks/useAuth";
   import { useMovie } from "@/hooks/useMovie";

   // After
   import { useAuth, useMovie } from "@/hooks";
   ```

***REMOVED******REMOVED*** Testing Your Changes

After updating imports, make sure to:

1. Run the TypeScript compiler to check for type errors
2. Test the affected components to ensure functionality is preserved

If you encounter any issues, check that the hook you're trying to use is properly exported from the appropriate directory index file.
