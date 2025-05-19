"use client";

import ProfileModal from "@/components/profile/ProfileModal";
import GenreSection from "@/components/navigation/GenreSection";
import { useAuth } from "@/hooks";
import {
  Button,
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  Icon,
  Text,
  VStack,
  useDisclosure,
  Heading,
  Divider,
  Box,
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
      <Button
        variant="ghost"
        onClick={onOpen}
        leftIcon={<Icon as={HiOutlineBars3} />}
      >
        Menu
      </Button>

      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="xs">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerHeader borderBottomWidth="1px">Next Watch</DrawerHeader>
          <DrawerBody>
            <VStack spacing={3} align="stretch" pt={2}>
              {/* Main navigation */}
              <Heading fontSize="md" fontWeight="bold">
                Navigation
              </Heading>
              {renderNavGroup(mainNavItems)}

              {/* User navigation - only show if authenticated */}
              {userNavItems.length > 0 && (
                <>
                  <Divider my={2} />
                  <Heading fontSize="md" fontWeight="bold">
                    My Lists
                  </Heading>
                  {renderNavGroup(userNavItems)}
                </>
              )}

              {/* Top movies */}
              <Divider my={2} />
              <Heading fontSize="md" fontWeight="bold">
                Top Movies
              </Heading>
              {renderNavGroup(topNavItems)}

              {/* Genres section */}
              <Divider my={2} />
              <Heading fontSize="md" fontWeight="bold">
                Genres
              </Heading>
              <Box maxH="200px" overflowY="auto" pr={2}>
                <GenreSection />
              </Box>

              {/* Profile button - only show if authenticated */}
              {isAuthenticated && (
                <>
                  <Divider my={2} />
                  <Button
                    variant="ghost"
                    justifyContent="flex-start"
                    leftIcon={<Icon as={HiUser} />}
                    width="100%"
                    onClick={handleOpenProfileModal}
                  >
                    <Text>Profile</Text>
                  </Button>
                </>
              )}
            </VStack>
          </DrawerBody>
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
