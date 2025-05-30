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
  useColorModeValue,
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
import { useAuth } from "@/services/hooks";
import { useSidebarData } from "@/services/hooks/navigation/useSidebarData";
import { MobileNavMenu } from "@/components/mobile/navigation";
import { LoginModal } from "@/components/features/auth";
import ProfileModal from "@/components/features/profile/ProfileModal";
import SearchInput from "@/components/ui/molecules/SearchInput";
import { createLogger } from "@/utils/logging";
import type { MobileHeaderProps } from "@/components/mobile/types";
import logoLight from "@/assets/logo-light.jpeg";
import logoDark from "@/assets/logo.jpeg";

// Create logger for this component
const logger = createLogger("MobileHeader");

/**
 * Enhanced MobileHeader Props
 *
 * Extends shared MobileHeaderProps with app-specific features
 */
interface AppMobileHeaderProps extends MobileHeaderProps {
  /** Whether to show search functionality */
  showSearch?: boolean;
  /** Whether to show authenticated user navigation */
  showUserNav?: boolean;
  /** Custom logo source */
  logoSrc?: string;
  /** Custom logo dark mode source */
  logoSrcDark?: string;
  /** Callback when search is toggled */
  onSearchToggle?: (isOpen: boolean) => void;
}

/**
 * MobileHeader component using shared MobileHeaderProps
 *
 * Enhanced header bar for mobile with app icon, common navigation buttons, and user menu.
 * Search icon now toggles an integrated search bar.
 * Integrates with useSidebarData to provide dynamic navigation data to MobileNavMenu.
 *
 * Features:
 * - Logo click navigation to home
 * - Quick navigation buttons (Home, Search, Watchlist, Favorites)
 * - Authentication-aware user menu
 * - Integrated search bar toggle
 * - Dynamic navigation data from BFF API
 * - Safe area support for notched devices
 * - Configurable through shared mobile header props
 *
 * @param title - Header title (optional)
 * @param showBackButton - Whether to show back button (default: false)
 * @param onBackPress - Callback for back button press
 * @param rightAction - Custom right action component
 * @param leftAction - Custom left action component (overrides nav menu)
 * @param showSearch - Whether to show search functionality (default: true)
 * @param showUserNav - Whether to show user navigation (default: true)
 * @param logoSrc - Custom logo source
 * @param logoSrcDark - Custom logo dark mode source
 * @param onSearchToggle - Callback when search is toggled
 */
const MobileHeader: React.FC<AppMobileHeaderProps> = ({
  title,
  showBackButton = false,
  onBackPress,
  rightAction,
  leftAction,
  showSearch = true,
  showUserNav = true,
  logoSrc,
  logoSrcDark,
  onSearchToggle,
}) => {
  const router = useRouter();
  const pathname = usePathname();
  const { colorMode } = useColorMode();
  const defaultLogo = colorMode === "light" ? logoLight : logoDark;
  const customLogo = colorMode === "light" ? logoSrc : logoSrcDark;
  const selectedLogo = customLogo || defaultLogo;
  const logoSrcUrl =
    typeof selectedLogo === "string" ? selectedLogo : selectedLogo.src;
  const { isAuthenticated, user } = useAuth();

  // Fetch sidebar data for dynamic navigation
  const { data: sidebarData, isLoading: isSidebarLoading } = useSidebarData();

  // Use semantic color tokens
  const activeNavColor = useColorModeValue("colors.primary", "colors.primary");
  const headerBgLight = useColorModeValue("rgba(255, 255, 255, 0.8)", "");
  const headerBgDark = useColorModeValue("", "rgba(26, 32, 44, 0.8)");

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [showSearchBar, setShowSearchBar] = useState(false);

  const handleBackPress = () => {
    if (onBackPress) {
      onBackPress();
    } else {
      router.back();
    }
  };

  const handleLogoClick = () => {
    logger.debug("Logo clicked, navigating to home page");
    // Use dynamic home path from sidebar data or fallback to "/"
    const homePath = sidebarData?.home?.href || "/";
    router.push(homePath);
  };

  const handleNavigation = (path: string) => {
    logger.debug(`Navigating to: ${path}`);
    router.push(path);
  };

  const toggleSearchBar = () => {
    const newState = !showSearchBar;
    logger.debug(`${showSearchBar ? "Closing" : "Opening"} search bar`);
    setShowSearchBar(newState);
    onSearchToggle?.(newState);
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
        backgroundColor={headerBgLight}
        _dark={{ backgroundColor: headerBgDark }}
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
            {leftAction ? (
              leftAction
            ) : showBackButton ? (
              <IconButton
                aria-label="Go back"
                icon={<HiArrowLeftOnRectangle />}
                fontSize={20}
                variant="ghost"
                onClick={handleBackPress}
                mr={2}
              />
            ) : (
              <MobileNavMenu
                sidebarData={sidebarData}
                isLoading={isSidebarLoading}
              />
            )}

            {!leftAction && (
              <Image
                src={logoSrcUrl}
                alt="Next Watch Logo"
                boxSize="40px"
                objectFit="cover"
                borderRadius="full"
                ml={showBackButton ? 2 : 3}
                onClick={handleLogoClick}
                cursor="pointer"
              />
            )}

            {title && (
              <Box
                ml={3}
                fontSize="lg"
                fontWeight="semibold"
                color="text.primary"
              >
                {title}
              </Box>
            )}
          </Flex>

          {rightAction ? (
            rightAction
          ) : (
            <HStack spacing={2}>
              {showSearch && (
                <Tooltip label="Search" openDelay={500}>
                  <IconButton
                    aria-label="Search"
                    icon={<HiMagnifyingGlass />}
                    fontSize={20}
                    variant="ghost"
                    color={isActive("/search") ? activeNavColor : undefined}
                    onClick={toggleSearchBar}
                  />
                </Tooltip>
              )}

              {showUserNav && (
                <>
                  <Tooltip label="Home" openDelay={500}>
                    <IconButton
                      aria-label="Home"
                      icon={<HiHome />}
                      fontSize={20}
                      variant="ghost"
                      color={
                        isActive(sidebarData?.home?.href || "/")
                          ? activeNavColor
                          : undefined
                      }
                      onClick={() =>
                        handleNavigation(sidebarData?.home?.href || "/")
                      }
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
                          color={
                            isActive("/watchlist") ? activeNavColor : undefined
                          }
                          onClick={() => handleNavigation("/watchlist")}
                        />
                      </Tooltip>

                      <Tooltip label="Favorites" openDelay={500}>
                        <IconButton
                          aria-label="Favorites"
                          icon={<HiHeart />}
                          fontSize={20}
                          variant="ghost"
                          color={
                            isActive("/favorites") ? activeNavColor : undefined
                          }
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
                </>
              )}
            </HStack>
          )}
        </Flex>

        {/* Search bar section - appears when search icon is clicked */}
        {showSearch && (
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
        )}
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
