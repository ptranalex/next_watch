"use client";

import logoLight from "@/assets/logo-light.jpeg";
import logoDark from "@/assets/logo.jpeg";
import { LoginModal } from "@/components/features/auth";
import ColorModeSwitch from "@/components/ui/atoms/ColorModeSwitch";
import SearchInput from "@/components/ui/molecules/SearchInput";
import ProfileModal from "@/components/features/profile/ProfileModal";
import { useAuth } from "@/services/hooks";
import { useResponsive } from "@/providers/ResponsiveContext";
import { useColorModeValueSafe } from "@/services/hooks";
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
import type { HeaderProps } from "../types";

// Create logger for this component
const logger = createLogger("Header");

/**
 * Header component using shared HeaderProps
 *
 * Desktop/tablet navigation header with flexible customization options.
 * Mobile navigation is handled by a separate mobile component.
 *
 * Now uses hydration-safe color mode values to prevent SSR/client flash
 * during skeleton loading in the header background.
 *
 * @param logo - Custom logo element (defaults to Next Watch logo)
 * @param title - Navigation title (defaults to "Next Watch")
 * @param showSearch - Whether to show search input (default: true)
 * @param showUserActions - Whether to show user login/profile actions (default: true)
 * @param showColorMode - Whether to show color mode switch (default: true)
 * @param onLogoClick - Custom logo click handler (defaults to home navigation)
 * @param customActions - Additional action elements to display
 * @param className - CSS class name for styling
 * @param isSearchFocused - Whether search input is currently focused (affects opacity)
 * @param onSearchFocusChange - Callback when search focus state changes
 */
const Header: React.FC<HeaderProps> = ({
  logo,
  title = "Next Watch",
  showSearch = true,
  showUserActions = true,
  showColorMode = true,
  onLogoClick,
  customActions,
  className,
  isSearchFocused: controlledSearchFocused,
  onSearchFocusChange,
}) => {
  const { colorMode } = useColorMode();
  const { isHydrated } = useResponsive();

  // Use hydration-safe logo selection to prevent flash during SSR
  const defaultLogo = isHydrated
    ? colorMode === "light"
      ? logoLight
      : logoDark
    : logoDark; // Default to dark logo during SSR to match dark theme preference

  const router = useRouter();
  const { isAuthenticated, user } = useAuth();

  // Use hydration-safe color mode values to prevent SSR/client flash
  const headerBgColor = useColorModeValueSafe("gray.50", "gray.800");

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  // Internal search focus state management
  const [internalSearchFocused, setInternalSearchFocused] = useState(false);

  // Determine if component is controlled for search focus
  const isSearchFocusControlled = controlledSearchFocused !== undefined;
  const isSearchFocused = isSearchFocusControlled
    ? controlledSearchFocused
    : internalSearchFocused;

  // Log component initialization and auth state
  useEffect(() => {
    logger.debug(
      `Header initialized: auth=${isAuthenticated}, colorMode=${colorMode}, searchFocused=${isSearchFocused}`
    );

    if (isAuthenticated && user) {
      logger.debug(`User authenticated: ${user.email}`);
    }
  }, [isAuthenticated, user, colorMode, isSearchFocused]);

  const handleLogoClick = useCallback(() => {
    if (onLogoClick) {
      onLogoClick();
    } else {
      // Default behavior: Navigate to home page
      logger.debug("Logo clicked, navigating to home page");
      router.push("/");
    }
  }, [onLogoClick, router]);

  // Handle search focus state changes
  const handleSearchFocusChange = useCallback(
    (isFocused: boolean) => {
      logger.debug(`Search focus changed: ${isFocused}`);

      if (onSearchFocusChange) {
        onSearchFocusChange(isFocused);
      }

      if (!isSearchFocusControlled) {
        setInternalSearchFocused(isFocused);
      }
    },
    [onSearchFocusChange, isSearchFocusControlled]
  );

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

  // Calculate opacity based on search focus state - hydration-safe
  const headerOpacity = isHydrated ? (isSearchFocused ? 1.0 : 0.95) : 0.95; // Default opacity during SSR to match most common state

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
        backgroundColor={headerBgColor}
        boxShadow="xl"
        opacity={headerOpacity}
        width="100%"
        className={className}
        transition="opacity 0.2s ease-in-out"
      >
        <HStack padding="20px" spacing="10px">
          {logoElement}
          {title && (
            <Heading size="sm" marginRight={10} whiteSpace="nowrap">
              {title}
            </Heading>
          )}
          {showSearch && (
            <SearchInput
              onFocus={() => handleSearchFocusChange(true)}
              onBlur={() => handleSearchFocusChange(false)}
            />
          )}
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
          {customActions}
        </HStack>
      </Box>

      {/* Login Modal */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={handleCloseLoginModal}
        onSuccess={handleCloseLoginModal}
      />

      {/* Profile Modal */}
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={handleCloseProfileModal}
      />
    </>
  );
};

export default Header;
