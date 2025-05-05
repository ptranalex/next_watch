"use client";

import type { FC } from "react";
import {
  Box,
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
import { FaHome, FaSearch, FaUser } from "react-icons/fa";
import { MdOutlineTheaterComedy } from "react-icons/md";
import { PiMaskSad } from "react-icons/pi";
import { HiOutlineBars3 } from "react-icons/hi2";
import Link from "next/link";
import { useAuth } from "@/hooks";
import { useMovieQuery } from "../../context/MovieQueryContext";
import type { IconType } from "react-icons";

interface NavItem {
  icon: IconType;
  label: string;
  path: string;
}

const MobileNavMenu: FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isAuthenticated, logout } = useAuth();
  const { reset } = useMovieQuery();

  const navItems: NavItem[] = [
    { icon: FaHome, label: "Home", path: "/" },
    { icon: FaSearch, label: "Search", path: "/search" },
    { icon: MdOutlineTheaterComedy, label: "Movies", path: "/movies" },
    { icon: PiMaskSad, label: "Actors", path: "/actors" },
  ];

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
                <Link href="/profile" onClick={onClose}>
                  <Button
                    variant="ghost"
                    justifyContent="flex-start"
                    leftIcon={<Icon as={FaUser} />}
                    width="100%"
                  >
                    <Text>Profile</Text>
                  </Button>
                </Link>
              ) : null}
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
};

export default MobileNavMenu;
