"use client";

import ProfileModal from "@/components/features/profile/ProfileModal";
import { MobileGenreSection } from "@/components/ui/organisms/navigation/sections";
import { useAuth } from "@/hooks";
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
  HStack,
} from "@chakra-ui/react";
import Link from "next/link";
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

interface NavItem {
  icon: IconType;
  label: string;
  path: string;
}

const MobileNavMenu: FC = () => {
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

  // Main navigation items
  const mainNavItems: NavItem[] = [
    { icon: FaHome, label: "Home", path: "/" },
    { icon: FaSearch, label: "Search", path: "/search" },
    { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
    { icon: PiMaskSad, label: "Actors", path: "/actors" },
  ];

  // User-specific navigation items - same as SideBar
  const userNavItems = useMemo<NavItem[]>(() => {
    if (!isAuthenticated) return [];

    return [
      { icon: HiBookmark, label: "Watch List", path: "/watchlist" },
      { icon: HiHeart, label: "Favorites", path: "/favorites" },
      { icon: HiDocumentCheck, label: "History", path: "/history" },
      { icon: HiCheckBadge, label: "Our Picks", path: "/recommended" },
    ];
  }, [isAuthenticated]);

  // Top movies navigation items - same as SideBar
  const topNavItems = useMemo<NavItem[]>(
    () => [
      { icon: GiTrophy, label: "Best of Year", path: "/top/current-year" },
      { icon: GiCalendar, label: "Popular in 2024", path: "/top/2024" },
      { icon: GiCalendar, label: "Popular by 2023", path: "/top/2023" },
      { icon: GiLaurelCrown, label: "All time top", path: "/top/all-time" },
    ],
    []
  );

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
        leftIcon={<Icon as={item.icon} />}
        onClick={() => handleNavigation(item.path)}
        width="100%"
      >
        <Text>{item.label}</Text>
      </Button>
    ));

  return (
    <>
      <IconButton
        key="mobile-nav-menu"
        aria-label="Open menu"
        icon={<HiOutlineBars3 />}
        onClick={onOpen}
        fontSize={25}
      />

      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="xs">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton size="lg" />
          <DrawerHeader borderBottomWidth="1px">Next Watch</DrawerHeader>
          <DrawerBody>
            <VStack spacing={4} align="stretch" pt={2}>
              {/* Main navigation */}
              <Box>
                <Heading fontSize="md" fontWeight="bold" mb={2}>
                  Browse
                </Heading>
                {renderNavGroup(mainNavItems)}
              </Box>

              {/* User navigation - only show if authenticated */}
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

              {/* Genres section - now using MobileGenreSection */}
              <Box>
                <Divider mb={2} />
                <Heading fontSize="md" fontWeight="bold" mb={2}>
                  Genres
                </Heading>
                <MobileGenreSection layout="grid" onClose={onClose} />
              </Box>
            </VStack>
          </DrawerBody>

          {/* Footer with profile button if authenticated */}
          {isAuthenticated && (
            <DrawerFooter borderTopWidth="1px">
              <Button
                leftIcon={<Icon as={HiUser} />}
                width="100%"
                colorScheme="blue"
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
