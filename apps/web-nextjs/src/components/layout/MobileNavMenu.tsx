"use client";

import { ReactNode } from "react";
import {
  IconButton,
  Box,
  CloseButton,
  Flex,
  Icon,
  useColorModeValue,
  Drawer,
  DrawerContent,
  Text,
  useDisclosure,
  BoxProps,
  FlexProps,
  VStack,
} from "@chakra-ui/react";
import { HiMenu, HiHome, HiFilm, HiStar, HiUser } from "react-icons/hi";
import { IconType } from "react-icons";
import { usePathname } from "next/navigation";
import Link from "next/link";
import ColorModeSwitch from "../common/ColorModeSwitch";

interface NavItemProps extends FlexProps {
  icon: IconType;
  children: ReactNode;
  href: string;
  isActive: boolean;
}

interface MobileNavMenuProps extends BoxProps {
  onClose?: () => void;
}

interface SidebarProps extends BoxProps {
  onClose: () => void;
}

const NavItems = [
  { name: "Home", icon: HiHome, href: "/" },
  { name: "Movies", icon: HiFilm, href: "/movies" },
  { name: "Actors", icon: HiStar, href: "/actors" },
  { name: "Profile", icon: HiUser, href: "/profile" },
];

const NavItem = ({ icon, children, href, isActive, ...rest }: NavItemProps) => {
  const activeColor = useColorModeValue("blue.500", "blue.300");
  const inactiveColor = useColorModeValue("gray.600", "gray.300");
  const activeBg = useColorModeValue("blue.50", "blue.900");
  const hoverBg = useColorModeValue("gray.100", "gray.700");

  return (
    <Link href={href} passHref style={{ width: "100%" }}>
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        bg={isActive ? activeBg : "transparent"}
        color={isActive ? activeColor : inactiveColor}
        _hover={{
          bg: isActive ? activeBg : hoverBg,
        }}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
            color={isActive ? activeColor : inactiveColor}
          />
        )}
        {children}
      </Flex>
    </Link>
  );
};

const SidebarContent = ({ onClose, ...rest }: SidebarProps) => {
  const pathname = usePathname();

  return (
    <Box
      transition="3s ease"
      bg={useColorModeValue("white", "gray.900")}
      borderRight="1px"
      borderRightColor={useColorModeValue("gray.200", "gray.700")}
      w={{ base: "full", md: 60 }}
      pos="fixed"
      h="full"
      {...rest}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontWeight="bold">
          NextWatch
        </Text>
        <CloseButton display={{ base: "flex", md: "none" }} onClick={onClose} />
      </Flex>

      <VStack spacing={2} align="stretch">
        {NavItems.map((item) => (
          <NavItem
            key={item.name}
            icon={item.icon}
            href={item.href}
            isActive={
              pathname === item.href ||
              (item.href !== "/" && pathname?.startsWith(item.href))
            }
          >
            {item.name}
          </NavItem>
        ))}
      </VStack>

      <Flex position="absolute" bottom="5" width="100%" px="8">
        <ColorModeSwitch showLabel />
      </Flex>
    </Box>
  );
};

export default function MobileNavMenu({
  onClose,
  ...rest
}: MobileNavMenuProps) {
  const { isOpen, onOpen, onClose: onDrawerClose } = useDisclosure();

  const handleClose = () => {
    onDrawerClose();
    if (onClose) onClose();
  };

  return (
    <Box display={{ base: "block", md: "none" }} {...rest}>
      <IconButton
        variant="outline"
        onClick={onOpen}
        aria-label="Open navigation menu"
        icon={<HiMenu />}
      />

      <Drawer
        autoFocus={false}
        isOpen={isOpen}
        placement="left"
        onClose={handleClose}
        returnFocusOnClose={false}
        onOverlayClick={handleClose}
        size="full"
      >
        <DrawerContent>
          <SidebarContent onClose={handleClose} />
        </DrawerContent>
      </Drawer>
    </Box>
  );
}
