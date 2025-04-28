"use client";

import { Box, VStack, Text, Divider, Icon, Link } from "@chakra-ui/react";
import NextLink from "next/link";
import { usePathname } from "next/navigation";
import {
  HiHome,
  HiFilm,
  HiUser,
  HiStar,
  HiClock,
  HiBookmark,
} from "react-icons/hi2";
import { IconType } from "react-icons";

interface NavItemProps {
  icon: IconType;
  href: string;
  label: string;
  isActive?: boolean;
}

const NavItem = ({ icon, href, label, isActive }: NavItemProps) => {
  return (
    <Link
      as={NextLink}
      href={href}
      display="flex"
      alignItems="center"
      p={2}
      borderRadius="md"
      _hover={{ bg: "gray.100", textDecoration: "none" }}
      bg={isActive ? "gray.100" : "transparent"}
      fontWeight={isActive ? "bold" : "normal"}
    >
      <Icon as={icon} boxSize={5} mr={3} />
      <Text>{label}</Text>
    </Link>
  );
};

export default function LeftNavBar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path;
  };

  return (
    <Box position="sticky" top="80px" w="full">
      <VStack align="stretch" spacing={2} w="full">
        <NavItem icon={HiHome} href="/" label="Home" isActive={isActive("/")} />

        <Divider my={2} />

        <Text fontSize="sm" color="gray.500" fontWeight="medium" px={2} mb={1}>
          Discover
        </Text>

        <NavItem
          icon={HiFilm}
          href="/movies"
          label="Movies"
          isActive={isActive("/movies")}
        />

        <NavItem
          icon={HiUser}
          href="/actors"
          label="Actors"
          isActive={pathname.startsWith("/actors")}
        />

        <Divider my={2} />

        <Text fontSize="sm" color="gray.500" fontWeight="medium" px={2} mb={1}>
          Personal
        </Text>

        <NavItem
          icon={HiStar}
          href="/favorites"
          label="Favorites"
          isActive={isActive("/favorites")}
        />

        <NavItem
          icon={HiClock}
          href="/watched"
          label="Watched"
          isActive={isActive("/watched")}
        />

        <NavItem
          icon={HiBookmark}
          href="/watchlist"
          label="Watchlist"
          isActive={isActive("/watchlist")}
        />

        <Divider my={2} />

        <NavItem
          icon={HiUser}
          href="/profile"
          label="Profile"
          isActive={isActive("/profile")}
        />
      </VStack>
    </Box>
  );
}
