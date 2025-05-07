"use client";

import ProfileModal from "@/components/profile/ProfileModal";
import { useMovieQuery } from "@/context/MovieQueryContext";
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
import { useState } from "react";
import type { IconType } from "react-icons";
import { FaHome, FaSearch, FaUser } from "react-icons/fa";
import { HiOutlineBars3 } from "react-icons/hi2";
import { MdOutlineTheaterComedy } from "react-icons/md";
import { PiMaskSad } from "react-icons/pi";

interface NavItem {
  icon: IconType;
  label: string;
  path: string;
}

const MobileNavMenu: FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isAuthenticated } = useAuth();
  const { reset } = useMovieQuery();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  const navItems: NavItem[] = [
    { icon: FaHome, label: "Home", path: "/" },
    { icon: FaSearch, label: "Search", path: "/search" },
    { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
    { icon: PiMaskSad, label: "Actors", path: "/actors" },
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
                <Link key={item.path} href={item.path} onClick={onClose}>
                  <Button
                    variant="ghost"
                    justifyContent="flex-start"
                    leftIcon={<Icon as={item.icon} />}
                    onClick={() => reset()}
                    width="100%"
                  >
                    <Text>{item.label}</Text>
                  </Button>
                </Link>
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
