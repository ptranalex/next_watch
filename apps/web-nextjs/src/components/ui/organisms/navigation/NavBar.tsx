"use client";

import logoLight from "@/assets/logo-light.jpeg";
import logoDark from "@/assets/logo.jpeg";
import { LoginModal } from "@/components/features/auth";
import ColorModeSwitch from "@/components/ui/atoms/ColorModeSwitch";
import SearchInput from "@/components/ui/molecules/SearchInput";
import ProfileModal from "@/components/features/profile/ProfileModal";
import { useAuth } from "@/hooks";
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
import type { NavBarProps } from "../types";

// Create logger for this component
const logger = createLogger("NavBar");

/**
 * NavBar component using shared NavBarProps
 *
 * Desktop/tablet navigation bar with flexible customization options.
 * Mobile navigation is handled by a separate mobile component.
 *
 * @param logo - Custom logo element (defaults to Next Watch logo)
 * @param title - Navigation title (defaults to "Next Watch")
 * @param showSearch - Whether to show search input (default: true)
 * @param showUserActions - Whether to show user login/profile actions (default: true)
 * @param showColorMode - Whether to show color mode switch (default: true)
 * @param onLogoClick - Custom logo click handler (defaults to home navigation)
 * @param customActions - Additional action elements to display
 * @param className - CSS class name for styling
 */
const NavBar: React.FC<NavBarProps> = ({
  logo,
  title = "Next Watch",
  showSearch = true,
  showUserActions = true,
  showColorMode = true,
  onLogoClick,
  customActions,
  className,
}) => {
  const { colorMode } = useColorMode();
  const defaultLogo = colorMode === "light" ? logoLight : logoDark;
  const router = useRouter();
  const { isAuthenticated, user } = useAuth();

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  // Log component initialization and auth state
  useEffect(() => {
    logger.debug(
      `NavBar initialized: auth=${isAuthenticated}, colorMode=${colorMode}`
    );

    if (isAuthenticated && user) {
      logger.debug(`User authenticated: ${user.email}`);
    }
  }, [isAuthenticated, user, colorMode]);

  const handleLogoClick = useCallback(() => {
    if (onLogoClick) {
      onLogoClick();
    } else {
      // Default behavior: Navigate to home page
      logger.debug("Logo clicked, navigating to home page");
      router.push("/");
    }
  }, [onLogoClick, router]);

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

  // Render logo element
  const logoElement = logo || (
    <Image
      src={defaultLogo.src}
      alt="Next Watch Logo"
      boxSize="40px"
      objectFit="cover"
      borderRadius="full"
      margin="0"
      padding="0"
      onClick={handleLogoClick}
      cursor="pointer"
    />
  );

  return (
    <>
      <Box
        position="sticky"
        top="0"
        zIndex="sticky"
        backdropFilter="blur(10px)"
        backgroundColor="bg.primary"
        boxShadow="xl"
        opacity="0.95"
        width="100%"
        className={className}
      >
        <HStack padding="20px" spacing="10px">
          {logoElement}
          {title && (
            <Heading size="sm" marginRight={10} whiteSpace="nowrap">
              {title}
            </Heading>
          )}
          {showSearch && <SearchInput onFocus={() => {}} onBlur={() => {}} />}
          {showUserActions && (
            <>
              {isAuthenticated && user ? (
                <Box
                  cursor="pointer"
                  onClick={handleOpenProfileModal}
                  ml={{ base: 0, md: 2 }}
                >
                  <Avatar size="sm" name={user.username || user.email} />
                </Box>
              ) : (
                <IconButton
                  aria-label="Login"
                  icon={<HiArrowLeftOnRectangle />}
                  onClick={handleOpenLoginModal}
                  fontSize={25}
                  variant="ghost"
                  color="text.secondary"
                />
              )}
            </>
          )}
          {showColorMode && <ColorModeSwitch />}
          {customActions && <Box ml={2}>{customActions}</Box>}
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
