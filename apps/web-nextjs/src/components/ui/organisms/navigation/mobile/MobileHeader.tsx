"use client";

import React, { useState } from "react";
import {
  Box,
  Flex,
  Image,
  IconButton,
  Avatar,
  useColorMode,
  Tooltip,
  HStack,
} from "@chakra-ui/react";
import {
  HiArrowLeftOnRectangle,
  HiMagnifyingGlass,
  HiHome,
  HiHeart,
  HiBookmark,
  HiXMark,
} from "react-icons/hi2";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/hooks";
import MobileNavMenu from "@/components/ui/organisms/navigation/MobileNavMenu";
import LoginModal from "@/components/features/auth/LoginModal";
import ProfileModal from "@/components/features/profile/ProfileModal";
import SearchInput from "@/components/ui/molecules/SearchInput";
import { createLogger } from "@/utils/logging";
import logoLight from "@/assets/logo-light.jpeg";
import logoDark from "@/assets/logo.jpeg";

// Create logger for this component
const logger = createLogger("MobileHeader");

/**
 * MobileHeader component
 * Enhanced header bar for mobile with app icon, common navigation buttons, and user menu
 * Search icon now toggles an integrated search bar
 */
const MobileHeader: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const { colorMode } = useColorMode();
  const logo = colorMode === "light" ? logoLight : logoDark;
  const { isAuthenticated, user } = useAuth();

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [showSearchBar, setShowSearchBar] = useState(false);

  const handleLogoClick = () => {
    logger.debug("Logo clicked, navigating to home page");
    router.push("/");
  };

  const handleNavigation = (path: string) => {
    logger.debug(`Navigating to: ${path}`);
    router.push(path);
  };

  const toggleSearchBar = () => {
    logger.debug(`${showSearchBar ? "Closing" : "Opening"} search bar`);
    setShowSearchBar(!showSearchBar);
  };

  const handleOpenLoginModal = () => {
    logger.info("Opening login modal");
    setIsLoginModalOpen(true);
  };

  const handleCloseLoginModal = () => {
    logger.debug("Closing login modal");
    setIsLoginModalOpen(false);
  };

  const handleOpenProfileModal = () => {
    logger.info("Opening profile modal");
    setIsProfileModalOpen(true);
  };

  const handleCloseProfileModal = () => {
    logger.debug("Closing profile modal");
    setIsProfileModalOpen(false);
  };

  // Check if a navigation path is active
  const isActive = (path: string): boolean => {
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname?.startsWith(path)) return true;
    return false;
  };

  const handleSearchFocus = () => {
    // Just keep the search bar open when focused
  };

  const handleSearchBlur = () => {
    // Don't auto-close on blur to prevent accidental dismissal
  };

  return (
    <>
      <Box
        as="header"
        position="sticky"
        top="0"
        zIndex="sticky"
        backdropFilter="blur(10px)"
        backgroundColor="rgba(255, 255, 255, 0.8)"
        _dark={{ backgroundColor: "rgba(26, 32, 44, 0.8)" }}
        width="100%"
        boxShadow="sm"
        sx={{
          paddingTop: "env(safe-area-inset-top, 0px)",
        }}
      >
        {/* Main header bar */}
        <Flex
          align="center"
          justify="space-between"
          padding="16px"
          height="64px"
          display={showSearchBar ? "none" : "flex"}
        >
          <Flex align="center">
            <MobileNavMenu />
            <Image
              src={logo.src}
              alt="Next Watch Logo"
              boxSize="40px"
              objectFit="cover"
              borderRadius="full"
              ml={3}
              onClick={handleLogoClick}
              cursor="pointer"
            />
          </Flex>

          <HStack spacing={2}>
            <Tooltip label="Home" openDelay={500}>
              <IconButton
                aria-label="Home"
                icon={<HiHome />}
                fontSize={20}
                variant="ghost"
                color={isActive("/") ? "blue.500" : undefined}
                onClick={() => handleNavigation("/")}
              />
            </Tooltip>

            <Tooltip label="Search" openDelay={500}>
              <IconButton
                aria-label="Search"
                icon={<HiMagnifyingGlass />}
                fontSize={20}
                variant="ghost"
                color={isActive("/search") ? "blue.500" : undefined}
                onClick={toggleSearchBar}
              />
            </Tooltip>

            {isAuthenticated && (
              <>
                <Tooltip label="Watchlist" openDelay={500}>
                  <IconButton
                    aria-label="Watchlist"
                    icon={<HiBookmark />}
                    fontSize={20}
                    variant="ghost"
                    color={isActive("/watchlist") ? "blue.500" : undefined}
                    onClick={() => handleNavigation("/watchlist")}
                  />
                </Tooltip>

                <Tooltip label="Favorites" openDelay={500}>
                  <IconButton
                    aria-label="Favorites"
                    icon={<HiHeart />}
                    fontSize={20}
                    variant="ghost"
                    color={isActive("/favorites") ? "blue.500" : undefined}
                    onClick={() => handleNavigation("/favorites")}
                  />
                </Tooltip>
              </>
            )}

            {isAuthenticated && user ? (
              <Avatar
                size="sm"
                name={user.username || user.email}
                cursor="pointer"
                onClick={handleOpenProfileModal}
              />
            ) : (
              <IconButton
                aria-label="Login"
                icon={<HiArrowLeftOnRectangle />}
                onClick={handleOpenLoginModal}
                fontSize={20}
                variant="ghost"
              />
            )}
          </HStack>
        </Flex>

        {/* Search bar section - appears when search icon is clicked */}
        <Flex
          align="center"
          justify="space-between"
          padding="16px"
          height="64px"
          display={showSearchBar ? "flex" : "none"}
        >
          <IconButton
            aria-label="Close search"
            icon={<HiXMark />}
            fontSize={20}
            variant="ghost"
            onClick={toggleSearchBar}
          />
          <Box flex="1" mx={3}>
            <SearchInput
              onFocus={handleSearchFocus}
              onBlur={handleSearchBlur}
            />
          </Box>
        </Flex>
      </Box>

      {/* Modals */}
      <LoginModal isOpen={isLoginModalOpen} onClose={handleCloseLoginModal} />
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={handleCloseProfileModal}
      />
    </>
  );
};

export default MobileHeader;
