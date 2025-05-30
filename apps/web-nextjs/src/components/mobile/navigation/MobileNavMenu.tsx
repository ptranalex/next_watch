"use client";

import ProfileModal from "@/components/features/profile/ProfileModal";
import { useAuth } from "@/services/hooks";
import {
  Button,
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  DrawerCloseButton,
  DrawerFooter,
  Icon,
  Text,
  VStack,
  useDisclosure,
  Heading,
  Divider,
  Box,
  IconButton,
  Skeleton,
} from "@chakra-ui/react";
import type { FC } from "react";
import { useCallback, useState, useMemo } from "react";
import type { IconType } from "react-icons";
import { FaHome, FaSearch } from "react-icons/fa";
import { HiOutlineBars3 } from "react-icons/hi2";
import { MdOutlineTheaterComedy } from "react-icons/md";
import { PiMaskSad } from "react-icons/pi";
import { GiTrophy, GiCalendar, GiLaurelCrown } from "react-icons/gi";
import {
  HiBookmark,
  HiCheckBadge,
  HiDocumentCheck,
  HiHeart,
  HiUser,
} from "react-icons/hi2";
import { useRouter } from "next/navigation";
import { createLogger } from "@/utils/logging";

// Create a logger for this component
const logger = createLogger("MobileNavMenu");

// Import SidebarData types
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

interface NavItem {
  icon: IconType;
  label: string;
  path: string;
}

interface MobileNavMenuProps {
  sidebarData?: SidebarData;
  isLoading?: boolean;
}

// Icon mapping for dynamic navigation items
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

const MobileNavMenu: FC<MobileNavMenuProps> = ({
  sidebarData,
  isLoading = false,
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isAuthenticated } = useAuth();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const router = useRouter();

  // Handle navigation with filter reset
  const handleNavigation = useCallback(
    (path: string) => {
      logger.debug(`Navigating to ${path}`);
      onClose();
      router.push(path);
    },
    [router, onClose]
  );

  // Fallback main navigation items (used when loading or no data)
  const fallbackMainNavItems: NavItem[] = [
    { icon: FaHome, label: "Home", path: "/" },
    { icon: FaSearch, label: "Search", path: "/search" },
    { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
    { icon: PiMaskSad, label: "Actors", path: "/actors" },
  ];

  // Convert sidebar data to navigation items
  const dynamicMainNavItems = useMemo<NavItem[]>(() => {
    if (!sidebarData) return fallbackMainNavItems;

    const items: NavItem[] = [
      {
        icon: FaHome,
        label: sidebarData.home.label,
        path: sidebarData.home.href,
      },
      // Add default items that might not be in sidebar data
      { icon: FaSearch, label: "Search", path: "/search" },
      { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
      { icon: PiMaskSad, label: "Actors", path: "/actors" },
    ];

    return items;
  }, [sidebarData, fallbackMainNavItems]);

  // User-specific navigation items from sidebar data
  const userNavItems = useMemo<NavItem[]>(() => {
    if (!isAuthenticated || !sidebarData?.user_links) return [];

    return sidebarData.user_links.map((link) => ({
      icon: getIconForPath(link.href, link.label),
      label: link.label,
      path: link.href,
    }));
  }, [isAuthenticated, sidebarData?.user_links]);

  // Top movies navigation items from sidebar data
  const topNavItems = useMemo<NavItem[]>(() => {
    if (!sidebarData?.top_links) {
      // Fallback top movies items
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

  const handleOpenProfileModal = () => {
    onClose(); // Close the drawer first
    setIsProfileModalOpen(true);
  };

  const handleCloseProfileModal = () => {
    setIsProfileModalOpen(false);
  };

  // Render a group of navigation items
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

  // Render loading skeleton for navigation sections
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
      <IconButton
        key="mobile-nav-menu"
        aria-label="Open menu"
        icon={<HiOutlineBars3 />}
        onClick={onOpen}
        fontSize={25}
        variant="ghost"
        color="text.secondary"
      />

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
                {/* Main navigation */}
                <Box>
                  <Heading fontSize="md" fontWeight="bold" mb={2}>
                    Browse
                  </Heading>
                  {renderNavGroup(dynamicMainNavItems)}
                </Box>

                {/* User navigation - only show if authenticated and has links */}
                {userNavItems.length > 0 && (
                  <Box>
                    <Divider mb={2} />
                    <Heading fontSize="md" fontWeight="bold" mb={2}>
                      My Lists
                    </Heading>
                    {renderNavGroup(userNavItems)}
                  </Box>
                )}

                {/* Top movies */}
                <Box>
                  <Divider mb={2} />
                  <Heading fontSize="md" fontWeight="bold" mb={2}>
                    Top Movies
                  </Heading>
                  {renderNavGroup(topNavItems)}
                </Box>

                {/* Genres section - using dynamic or static data */}
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
                    <Text>No genres found</Text>
                  )}
                </Box>
              </VStack>
            )}
          </DrawerBody>

          {/* Footer with profile button if authenticated */}
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

      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={handleCloseProfileModal}
      />
    </>
  );
};

export default MobileNavMenu;
