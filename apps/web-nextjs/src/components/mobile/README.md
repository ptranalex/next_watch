# Mobile Components Integration

This directory contains mobile-specific components that are now fully integrated with dynamic data from the BFF API through `useSidebarData`.

## 🚀 **MobileHeader & MobileNavMenu Integration**

The mobile header and navigation menu have been enhanced to use dynamic data from the BFF API instead of hardcoded navigation items.

### Key Integration Features

- **Dynamic Navigation Data**: All navigation links now come from `/bff/v1/sidebar` endpoint
- **User Authentication Aware**: Navigation adapts based on user authentication status
- **Loading State Handling**: Graceful loading states while fetching sidebar data
- **Fallback Support**: Hardcoded fallbacks when API data is unavailable
- **Icon Mapping**: Intelligent icon assignment based on navigation paths

## 📁 **Updated Components**

### `MobileHeader.tsx`

Enhanced with `useSidebarData` integration:

```typescript
interface AppMobileHeaderProps extends MobileHeaderProps {
  showSearch?: boolean;
  showUserNav?: boolean;
  logoSrc?: string;
  logoSrcDark?: string;
  onSearchToggle?: (isOpen: boolean) => void;
}
```

**New Features:**

- ✅ Fetches sidebar data using `useSidebarData()`
- ✅ Passes data and loading state to `MobileNavMenu`
- ✅ Uses dynamic home path from API for logo clicks
- ✅ Handles loading states gracefully

**Usage:**

```tsx
<MobileHeader
  title="My Page"
  showSearch={true}
  showUserNav={true}
  onSearchToggle={(isOpen) => console.log("Search:", isOpen)}
/>
```

### `MobileNavMenu.tsx`

Updated to accept and use sidebar data:

```typescript
interface MobileNavMenuProps {
  sidebarData?: SidebarData;
  isLoading?: boolean;
}
```

**New Features:**

- ✅ Dynamic main navigation from sidebar data
- ✅ User-specific links based on authentication
- ✅ Top movie links from API
- ✅ Dynamic genre navigation
- ✅ Loading skeleton while fetching data
- ✅ Intelligent icon mapping for dynamic links

## 🔄 **Data Flow**

```
BFF API (/bff/v1/sidebar)
         ↓
   useSidebarData()
         ↓
    MobileHeader
         ↓
   MobileNavMenu
         ↓
 Dynamic Navigation
```

### Sidebar Data Structure

```typescript
interface SidebarData {
  home: {
    label: string;
    href: string;
  };
  user_links: SidebarLink[];
  top_links: SidebarLink[];
  filters: SidebarFilters;
  genres: SidebarGenre[];
  metadata: SidebarMetadata;
}
```

## 🎯 **Icon Mapping Strategy**

The `getIconForPath` function intelligently assigns icons based on URL patterns:

```typescript
const getIconForPath = (path: string, label: string): IconType => {
  if (path.includes("/search")) return FaSearch;
  if (path.includes("/movies")) return MdOutlineTheaterComedy;
  if (path.includes("/actors")) return PiMaskSad;
  if (path.includes("/watchlist")) return HiBookmark;
  if (path.includes("/favorites") || path.includes("/liked")) return HiHeart;
  if (path.includes("/history") || path.includes("/watched"))
    return HiDocumentCheck;
  if (path.includes("/recommended")) return HiCheckBadge;
  if (path.includes("/top")) {
    if (label.toLowerCase().includes("all time")) return GiLaurelCrown;
    if (label.toLowerCase().includes("year")) return GiTrophy;
    return GiCalendar;
  }
  return FaHome; // Default fallback
};
```

## 📱 **Loading States**

### MobileNavMenu Loading Skeleton

When `isLoading={true}`, displays skeleton placeholders:

```tsx
const renderLoadingSkeleton = () => (
  <VStack spacing={4} align="stretch" pt={2}>
    <Box>
      <Skeleton height="20px" width="60px" mb={2} />
      <VStack spacing={2}>
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} height="40px" width="100%" />
        ))}
      </VStack>
    </Box>
  </VStack>
);
```

## 🛡️ **Fallback Strategy**

When sidebar data is unavailable, components fall back to hardcoded navigation:

```typescript
// Fallback main navigation items
const fallbackMainNavItems: NavItem[] = [
  { icon: FaHome, label: "Home", path: "/" },
  { icon: FaSearch, label: "Search", path: "/search" },
  { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
  { icon: PiMaskSad, label: "Actors", path: "/actors" },
];

// Fallback top movies items
const fallbackTopMovies = [
  { icon: GiTrophy, label: "Best of Year", path: "/top/current-year" },
  { icon: GiCalendar, label: "Popular in 2024", path: "/top/2024" },
  // ... more items
];
```

## 🔧 **Usage Examples**

### Basic Implementation

```tsx
import MobileHeader from "@/components/mobile/core/layout/MobileHeader";

function MyMobilePage() {
  return (
    <div>
      <MobileHeader title="Movies" showSearch={true} showUserNav={true} />
      {/* Page content */}
    </div>
  );
}
```

### Custom Navigation Handlers

```tsx
function CustomMobilePage() {
  return (
    <MobileHeader
      title="Custom Page"
      showBackButton={true}
      onBackPress={() => {
        // Custom back logic
        router.push("/custom-destination");
      }}
      onSearchToggle={(isOpen) => {
        console.log("Search bar:", isOpen ? "opened" : "closed");
      }}
    />
  );
}
```

### Custom Actions

```tsx
function PageWithCustomActions() {
  return (
    <MobileHeader
      title="Settings"
      rightAction={
        <IconButton
          aria-label="Save"
          icon={<HiCheckBadge />}
          onClick={handleSave}
        />
      }
      leftAction={
        <IconButton
          aria-label="Cancel"
          icon={<HiXMark />}
          onClick={handleCancel}
        />
      }
    />
  );
}
```

## 🚀 **Benefits of Integration**

### 1. **Dynamic Content**

- Navigation items reflect current backend configuration
- User-specific links based on authentication
- Genre navigation updated from CMS/backend

### 2. **Consistency**

- Mobile navigation matches desktop sidebar
- Single source of truth for navigation structure
- Consistent authentication state across all components

### 3. **Performance**

- Efficient caching via React Query
- Loading states prevent UI flashing
- Intelligent prefetching and background updates

### 4. **Maintainability**

- No hardcoded navigation items to maintain
- Navigation changes managed via backend
- Automatic updates when backend data changes

## 🔍 **Testing Integration**

### Manual Testing Checklist

1. **API Integration**

   - [ ] Navigation menu loads dynamic data
   - [ ] Loading skeleton appears during fetch
   - [ ] Fallback navigation works when API fails

2. **Authentication States**

   - [ ] User links appear when authenticated
   - [ ] User links hidden when not authenticated
   - [ ] Profile button shows/hides correctly

3. **Navigation Behavior**

   - [ ] Logo clicks navigate to dynamic home path
   - [ ] All navigation links work correctly
   - [ ] Icons match navigation paths appropriately

4. **Loading & Error States**
   - [ ] Graceful loading state handling
   - [ ] Proper error fallbacks
   - [ ] No UI flashing or broken states

### Dev Tools Debugging

```typescript
// Check sidebar data in console
const { data, isLoading, error } = useSidebarData();
console.log("Sidebar Data:", { data, isLoading, error });
```

## 📚 **Related Documentation**

- [`useSidebarData.ts`](../../../services/hooks/navigation/useSidebarData.ts) - API hook
- [BFF API Documentation](../../../services/api/bff/) - Backend for Frontend
- [Mobile Types](./types/) - TypeScript interfaces
- [Authentication Hooks](../../../services/hooks/core/) - User auth state

---

The mobile navigation is now fully integrated with dynamic data from the BFF API, providing a consistent and maintainable navigation experience across the entire application! 🎉
