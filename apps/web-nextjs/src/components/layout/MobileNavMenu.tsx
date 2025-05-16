"use client";

import ProfileModal from "@/components/profile/ProfileModal";
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
} from "@chakra-ui/react";
import Link from "next/link";
import type { FC } from "react";
import { useCallback, useState } from "react";
import type { IconType } from "react-icons";
import { FaHome, FaSearch, FaUser } from "react-icons/fa";
import { HiOutlineBars3 } from "react-icons/hi2";
import { MdOutlineTheaterComedy } from "react-icons/md";
import { PiMaskSad } from "react-icons/pi";
import { GiTrophy } from "react-icons/gi";
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

  const navItems: NavItem[] = [
    { icon: FaHome, label: "Home", path: "/" },
    { icon: FaSearch, label: "Search", path: "/search" },
    { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
    { icon: PiMaskSad, label: "Actors", path: "/actors" },
    {
      icon: GiTrophy,
      label: "Top Movies",
      path: `/top/${new Date().getFullYear()}`,
    },
  ];

  const handleOpenProfileModal = () => {
    onClose(); // Close the drawer first
    setIsProfileModalOpen(true);
  };

  const handleCloseProfileModal = () => {
    setIsProfileModalOpen(false);
  };

  return (
    <>
      <Button
        variant="ghost"
        onClick={onOpen}
        leftIcon={<Icon as={HiOutlineBars3} />}
      >
        Menu
      </Button>

      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerHeader>Menu</DrawerHeader>
          <DrawerBody>
            <VStack spacing={4} align="stretch">
              {navItems.map((item) => (
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
              ))}

              {isAuthenticated ? (
                <Button
                  variant="ghost"
                  justifyContent="flex-start"
                  leftIcon={<Icon as={FaUser} />}
                  width="100%"
                  onClick={handleOpenProfileModal}
                >
                  <Text>Profile</Text>
                </Button>
              ) : null}
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
