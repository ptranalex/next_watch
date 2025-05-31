"use client";

import ProfileModal from "@/components/features/profile/ProfileModal";
import { useAuth } from "@/services/hooks";
import { createLogger } from "@/utils/logging";
import {
  Box,
  Button,
  Divider,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  Heading,
  Icon,
  IconButton,
  Skeleton,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import type { FC } from "react";
import { useCallback, useMemo, useState } from "react";
import type { IconType } from "react-icons";
import { FaHome, FaSearch } from "react-icons/fa";
import { GiCalendar, GiLaurelCrown, GiTrophy } from "react-icons/gi";
import {
  HiBookmark,
  HiCheckBadge,
  HiDocumentCheck,
  HiHeart,
  HiOutlineBars3,
  HiUser,
} from "react-icons/hi2";
import { MdOutlineTheaterComedy } from "react-icons/md";
import { PiMaskSad } from "react-icons/pi";

// Create a logger for this component
const logger = createLogger("MobileNavDrawer");

/**
 * Sidebar data structure from the BFF API
 *
 * This interface defines the shape of navigation data received from the backend,
 * which includes user-specific links, top movies, genres, and metadata.
 */
interface SidebarLink {
  id: string;
  label: string;
  href: string;
  icon?: string;
}

interface SidebarGenre {
  id: number;
  name: string;
  href: string;
}

interface SidebarData {
  home: {
    label: string;
    href: string;
  };
  user_links: SidebarLink[];
  top_links: SidebarLink[];
  filters: {
    show: boolean;
    defaults: {
      rating_imdb: number | null;
      year: number | null;
    };
    locked: string[];
  };
  genres: SidebarGenre[];
  metadata: {
    layout: string;
    version: string;
    user_authenticated: boolean;
  };
}

/**
 * Internal navigation item structure
 *
 * Normalized format used internally by the component to render navigation items
 * with consistent icon and path handling.
 */
interface NavItem {
  icon: IconType;
  label: string;
  path: string;
}

/**
 * Props for the MobileNavDrawer component
 */
interface MobileNavDrawerProps {
  /** Sidebar data from the BFF API containing navigation structure */
  sidebarData?: SidebarData;
  /** Whether the component is in a loading state */
  isLoading?: boolean;
}

/**
 * Icon mapping utility for dynamic navigation items
 *
 * Maps URL paths and labels to appropriate React Icons based on content type.
 * Provides fallback icons for unknown paths to ensure consistent UI.
 *
 * @param path - The URL path for the navigation item
 * @param label - The display label for additional context
 * @returns The appropriate React Icon component
 */
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
  return FaHome; // Default fallback icon
};

/**
 * MobileNavDrawer Component
 *
 * A comprehensive mobile navigation drawer that provides access to all major
 * application sections. Features a hamburger menu trigger that opens a slide-out
 * drawer containing organized navigation sections.
 *
 * Key Features:
 * - **Responsive Design**: Only visible on mobile devices (hidden on desktop)
 * - **Dynamic Content**: Adapts navigation based on user authentication status
 * - **Organized Sections**: Groups navigation into logical categories (Browse, My Lists, Top Movies, Genres)
 * - **Loading States**: Provides skeleton loading while data is being fetched
 * - **Profile Integration**: Includes profile access for authenticated users
 * - **Icon Mapping**: Automatically assigns appropriate icons based on content type
 *
 * Navigation Sections:
 * 1. **Browse**: Core app navigation (Home, Search, Movies, Actors)
 * 2. **My Lists**: User-specific content (Watchlist, Favorites, History) - auth required
 * 3. **Top Movies**: Curated movie collections (Best of Year, All Time, etc.)
 * 4. **Genres**: Dynamic genre-based browsing
 *
 * @param sidebarData - Navigation data from BFF API
 * @param isLoading - Loading state for skeleton display
 */
const MobileNavDrawer: FC<MobileNavDrawerProps> = ({
  sidebarData,
  isLoading = false,
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isAuthenticated } = useAuth();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const router = useRouter();

  /**
   * Handle navigation with proper cleanup
   *
   * Closes the drawer and navigates to the specified path.
   * Includes logging for debugging navigation flows.
   */
  const handleNavigation = useCallback(
    (path: string) => {
      logger.debug(`Navigating to ${path}`);
      onClose();
      router.push(path);
    },
    [router, onClose]
  );

  /**
   * Fallback navigation items for core app functionality
   *
   * Used when sidebar data is loading or unavailable to ensure
   * basic navigation is always accessible.
   */
  const fallbackMainNavItems: NavItem[] = useMemo(
    () => [
      { icon: FaHome, label: "Home", path: "/" },
      { icon: FaSearch, label: "Search", path: "/search" },
      { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
      { icon: PiMaskSad, label: "Actors", path: "/actors" },
    ],
    []
  );

  /**
   * Dynamic main navigation items from sidebar data
   *
   * Combines home link from API with standard navigation items.
   * Falls back to static items if no sidebar data is available.
   */
  const dynamicMainNavItems = useMemo<NavItem[]>(() => {
    if (!sidebarData) return fallbackMainNavItems;

    const items: NavItem[] = [
      {
        icon: FaHome,
        label: sidebarData.home.label,
        path: sidebarData.home.href,
      },
      // Include standard navigation items that might not be in sidebar data
      { icon: FaSearch, label: "Search", path: "/search" },
      { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
      { icon: PiMaskSad, label: "Actors", path: "/actors" },
    ];

    return items;
  }, [sidebarData, fallbackMainNavItems]);

  /**
   * User-specific navigation items (authenticated users only)
   *
   * Transforms user_links from sidebar data into navigation items.
   * Only displayed when user is authenticated and has personal content.
   */
  const userNavItems = useMemo<NavItem[]>(() => {
    if (!isAuthenticated || !sidebarData?.user_links) return [];

    return sidebarData.user_links.map((link) => ({
      icon: getIconForPath(link.href, link.label),
      label: link.label,
      path: link.href,
    }));
  }, [isAuthenticated, sidebarData?.user_links]);

  /**
   * Top movies navigation items
   *
   * Provides access to curated movie collections. Falls back to
   * static popular collections if no API data is available.
   */
  const topNavItems = useMemo<NavItem[]>(() => {
    if (!sidebarData?.top_links) {
      // Fallback top movies collections
      return [
        { icon: GiTrophy, label: "Best of Year", path: "/top/current-year" },
        { icon: GiCalendar, label: "Popular in 2024", path: "/top/2024" },
        { icon: GiCalendar, label: "Popular by 2023", path: "/top/2023" },
        { icon: GiLaurelCrown, label: "All time top", path: "/top/all-time" },
      ];
    }

    return sidebarData.top_links.map((link) => ({
      icon: getIconForPath(link.href, link.label),
      label: link.label,
      path: link.href,
    }));
  }, [sidebarData?.top_links]);

  /**
   * Profile modal handlers
   *
   * Manages the profile modal state with proper drawer cleanup.
   */
  const handleOpenProfileModal = () => {
    onClose(); // Close the drawer first to avoid overlay conflicts
    setIsProfileModalOpen(true);
  };

  const handleCloseProfileModal = () => {
    setIsProfileModalOpen(false);
  };

  /**
   * Render a group of navigation items with consistent styling
   *
   * @param items - Array of navigation items to render
   * @returns JSX elements for the navigation group
   */
  const renderNavGroup = (items: NavItem[]) =>
    items.map((item) => (
      <Button
        key={item.path}
        variant="ghost"
        justifyContent="flex-start"
        leftIcon={<Icon as={item.icon} color="text.secondary" />}
        onClick={() => handleNavigation(item.path)}
        width="100%"
        color="text.primary"
        _hover={{ bg: "bg.tertiary" }}
      >
        <Text>{item.label}</Text>
      </Button>
    ));

  /**
   * Render loading skeleton for navigation sections
   *
   * Provides visual feedback while navigation data is being fetched.
   */
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

  return (
    <>
      {/* Hamburger menu trigger button */}
      <IconButton
        key="mobile-nav-drawer"
        aria-label="Open navigation menu"
        icon={<HiOutlineBars3 />}
        onClick={onOpen}
        fontSize={25}
        variant="ghost"
        color="text.secondary"
      />

      {/* Navigation drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="xs">
        <DrawerOverlay />
        <DrawerContent bg="bg.primary">
          <DrawerCloseButton size="lg" />
          <DrawerHeader
            borderBottomWidth="1px"
            borderBottomColor="text.tertiary"
          >
            Next Watch
          </DrawerHeader>
          <DrawerBody>
            {isLoading ? (
              renderLoadingSkeleton()
            ) : (
              <VStack spacing={4} align="stretch" pt={2}>
                {/* Main navigation section */}
                <Box>
                  <Heading fontSize="md" fontWeight="bold" mb={2}>
                    Browse
                  </Heading>
                  {renderNavGroup(dynamicMainNavItems)}
                </Box>

                {/* User-specific navigation - only show if authenticated and has content */}
                {userNavItems.length > 0 && (
                  <Box>
                    <Divider mb={2} />
                    <Heading fontSize="md" fontWeight="bold" mb={2}>
                      My Lists
                    </Heading>
                    {renderNavGroup(userNavItems)}
                  </Box>
                )}

                {/* Top movies section */}
                <Box>
                  <Divider mb={2} />
                  <Heading fontSize="md" fontWeight="bold" mb={2}>
                    Top Movies
                  </Heading>
                  {renderNavGroup(topNavItems)}
                </Box>

                {/* Genres section - dynamic or fallback message */}
                <Box>
                  <Divider mb={2} />
                  <Heading fontSize="md" fontWeight="bold" mb={2}>
                    Genres
                  </Heading>
                  {sidebarData?.genres ? (
                    // Dynamic genres from sidebar data
                    <VStack spacing={1} align="stretch">
                      {sidebarData.genres.map((genre) => (
                        <Button
                          key={genre.id}
                          variant="ghost"
                          size="sm"
                          justifyContent="flex-start"
                          onClick={() => handleNavigation(genre.href)}
                          width="100%"
                          color="text.primary"
                          _hover={{ bg: "bg.tertiary" }}
                        >
                          <Text fontSize="sm">{genre.name}</Text>
                        </Button>
                      ))}
                    </VStack>
                  ) : (
                    <Text fontSize="sm" color="text.tertiary">
                      No genres available
                    </Text>
                  )}
                </Box>
              </VStack>
            )}
          </DrawerBody>

          {/* Footer with profile access for authenticated users */}
          {isAuthenticated && (
            <DrawerFooter borderTopWidth="1px" borderTopColor="text.tertiary">
              <Button
                leftIcon={<Icon as={HiUser} />}
                width="100%"
                bg="colors.primary"
                color="text.inverse"
                _hover={{ bg: "colors.primary.darker" }}
                onClick={handleOpenProfileModal}
              >
                Profile
              </Button>
            </DrawerFooter>
          )}
        </DrawerContent>
      </Drawer>

      {/* Profile modal */}
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={handleCloseProfileModal}
      />
    </>
  );
};

export default MobileNavDrawer;
