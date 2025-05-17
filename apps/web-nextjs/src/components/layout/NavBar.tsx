"use client";

import logoLight from "@/assets/logo-light.jpeg";
import logoDark from "@/assets/logo.jpeg";
import LoginModal from "@/components/auth/LoginModal";
import ColorModeSwitch from "@/components/layout/ColorModeSwitch";
import MobileNavMenu from "@/components/layout/MobileNavMenu";
import SearchInput from "@/components/layout/SearchInput";
import ProfileModal from "@/components/profile/ProfileModal";
import { useAuth, useDevice } from "@/hooks";
import {
  Avatar,
  Box,
  HStack,
  Heading,
  IconButton,
  Image,
  useColorMode,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { HiArrowLeftOnRectangle } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("NavBar");

const NavBar: React.FC = () => {
  const { colorMode } = useColorMode();
  const logo = colorMode === "light" ? logoLight : logoDark;
  const router = useRouter();
  const { isMobile } = useDevice();

  const { isAuthenticated, user } = useAuth();
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  // Log component initialization and auth state
  useEffect(() => {
    logger.debug(
      `NavBar initialized: auth=${isAuthenticated}, mobile=${isMobile}, colorMode=${colorMode}`
    );

    if (isAuthenticated && user) {
      logger.debug(`User authenticated: ${user.email}`);
    }
  }, [isAuthenticated, user, isMobile, colorMode]);

  const handleLogoClick = useCallback(() => {
    // Navigate to home page
    logger.debug("Logo clicked, navigating to home page");
    router.push("/");
  }, [router]);

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

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

  const handleSearchFocus = () => {
    logger.debug("Search input focused");
    setIsSearchFocused(true);
  };

  const handleSearchBlur = () => {
    logger.debug("Search input blurred");
    setIsSearchFocused(false);
  };

  // Log layout changes
  useEffect(() => {
    if (isSearchFocused) {
      logger.debug("Layout changed to search-focused mode");
    }
  }, [isSearchFocused]);

  // Element visibility based on combined conditions
  const showMobileNav = !isSearchFocused && isMobile;
  const showLogo = !isSearchFocused;
  const showHeading = !isSearchFocused && !isMobile;
  const showUserIcon = !isSearchFocused;

  return (
    <>
      <Box
        position="sticky"
        top="0"
        zIndex="sticky"
        backdropFilter="blur(10px)"
        backgroundColor="rgba(255, 255, 255, 0.8)" // Adjust color and opacity as needed
        _dark={{ backgroundColor: "rgba(26, 32, 44, 0.8)" }} // Adjust for dark mode
        width="100%"
      >
        <HStack padding="20px" spacing="10px">
          {showMobileNav && <MobileNavMenu />}
          {showLogo && (
            <Image
              src={logo.src}
              alt="Next Watch Logo"
              boxSize="40px"
              objectFit="cover"
              borderRadius="full"
              margin="0"
              padding="0"
              onClick={handleLogoClick}
              cursor="pointer"
            />
          )}
          {showHeading && (
            <Heading size="sm" marginRight={10} whiteSpace="nowrap">
              Next Watch
            </Heading>
          )}
          <SearchInput onFocus={handleSearchFocus} onBlur={handleSearchBlur} />
          {isAuthenticated && user && showUserIcon ? (
            <Box
              cursor="pointer"
              onClick={handleOpenProfileModal}
              ml={{ base: 0, md: 2 }}
            >
              <Avatar size="sm" name={user.username || user.email} />
            </Box>
          ) : !isSearchFocused ? (
            <IconButton
              aria-label="Login"
              icon={<HiArrowLeftOnRectangle />}
              onClick={handleOpenLoginModal}
              fontSize={25}
            />
          ) : (
            showUserIcon && (
              <Box ml={{ base: 0, md: 2 }}>
                <Avatar size="sm" />
              </Box>
            )
          )}
          {!isSearchFocused && <ColorModeSwitch />}
        </HStack>
      </Box>
      <LoginModal isOpen={isLoginModalOpen} onClose={handleCloseLoginModal} />
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={handleCloseProfileModal}
      />
    </>
  );
};

export default NavBar;
