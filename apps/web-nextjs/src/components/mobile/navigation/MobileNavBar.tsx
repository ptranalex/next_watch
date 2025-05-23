import React, { useEffect } from "react";
import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import { usePathname, useRouter } from "next/navigation";
import { HiHome, HiHeart, HiBookmark, HiSearch, HiUser } from "react-icons/hi";
import { motion } from "framer-motion";
import { createLogger } from "@/utils/logging";
import type { MobileTabBarProps, MobileTab } from "@/components/mobile/types";

// Create logger for this component
const logger = createLogger("MobileNavBar");

// Motion Box for animations
const MotionBox = motion(Box);
const MotionFlex = motion(Flex);

/**
 * MobileNavBar Props
 *
 * Extends the shared MobileTabBarProps with additional mobile-specific features
 */
interface MobileNavBarProps
  extends Omit<MobileTabBarProps, "tabs" | "activeTab" | "onTabChange"> {
  /** Custom navigation tabs (defaults to standard app tabs) */
  customTabs?: MobileTab[];
  /** Whether to show haptic feedback on tab press */
  enableHapticFeedback?: boolean;
  /** Whether to show animations */
  enableAnimations?: boolean;
}

/**
 * MobileNavBar component using shared MobileTabBarProps
 *
 * Mobile-optimized bottom navigation bar with large touch-friendly tabs.
 *
 * Features:
 * - Native app-like animations
 * - Haptic feedback
 * - Safe area padding for iOS devices
 * - Optimized touch targets
 * - Configurable tabs using shared MobileTab type
 *
 * @param customTabs - Custom navigation tabs (defaults to standard app tabs)
 * @param position - Tab bar position (defaults to "bottom")
 * @param enableHapticFeedback - Whether to enable haptic feedback (default: true)
 * @param enableAnimations - Whether to enable animations (default: true)
 */
const MobileNavBar: React.FC<MobileNavBarProps> = ({
  customTabs,
  position = "bottom",
  enableHapticFeedback = true,
  enableAnimations = true,
}) => {
  const router = useRouter();
  const pathname = usePathname();
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  // Default navigation tabs using MobileTab type
  const defaultTabs: MobileTab[] = [
    { id: "home", label: "Home", icon: HiHome },
    { id: "search", label: "Search", icon: HiSearch },
    { id: "watchlist", label: "Watchlist", icon: HiBookmark },
    { id: "favorites", label: "Favorites", icon: HiHeart },
    { id: "profile", label: "Profile", icon: HiUser },
  ];

  const tabs = customTabs || defaultTabs;

  // Map tab IDs to paths
  const getPathForTab = (tabId: string): string => {
    const pathMap: Record<string, string> = {
      home: "/",
      search: "/search",
      watchlist: "/watchlist",
      favorites: "/favorites",
      profile: "/profile",
    };
    return pathMap[tabId] || `/${tabId}`;
  };

  // Apply haptic feedback when buttons are pressed
  const applyHapticFeedback = () => {
    if (!enableHapticFeedback) return;

    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(20);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }
  };

  // Handle navigation
  const handleTabPress = (tab: MobileTab) => {
    if (tab.isDisabled) return;

    applyHapticFeedback();
    const path = getPathForTab(tab.id);
    router.push(path);
  };

  // Check if tab is active
  const isTabActive = (tab: MobileTab): boolean => {
    const path = getPathForTab(tab.id);
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname.startsWith(path)) return true;
    return false;
  };

  useEffect(() => {
    logger.debug(`Current pathname: ${pathname}`);
  }, [pathname]);

  const containerProps = enableAnimations
    ? {
        initial: { y: 100 },
        animate: { y: 0 },
        transition: { duration: 0.3 },
      }
    : {};

  return (
    <MotionBox
      position="fixed"
      bottom={position === "bottom" ? 0 : undefined}
      top={position === "top" ? 0 : undefined}
      left={0}
      right={0}
      zIndex={1000}
      bg={bgColor}
      borderTop={position === "bottom" ? "1px" : undefined}
      borderBottom={position === "top" ? "1px" : undefined}
      borderColor={borderColor}
      paddingBottom={
        position === "bottom" ? "env(safe-area-inset-bottom, 8px)" : 2
      }
      paddingTop={position === "top" ? "env(safe-area-inset-top, 8px)" : 2}
      display={{ base: "block", md: "none" }} // Only show on mobile
      {...containerProps}
    >
      <Flex justify="space-around" align="center" width="100%">
        {tabs.map((tab) => {
          const active = isTabActive(tab);
          const disabled = tab.isDisabled;

          const tabProps = enableAnimations
            ? { whileTap: disabled ? {} : { scale: 0.95 } }
            : {};

          return (
            <MotionFlex
              key={tab.id}
              direction="column"
              align="center"
              justify="center"
              py={2}
              px={1}
              cursor={disabled ? "not-allowed" : "pointer"}
              onClick={() => handleTabPress(tab)}
              flex={1}
              color={disabled ? "gray.400" : active ? "blue.500" : "gray.500"}
              opacity={disabled ? 0.5 : 1}
              position="relative"
              {...tabProps}
            >
              {tab.icon && <Icon as={tab.icon} boxSize={6} mb={1} />}
              <Text fontSize="xs" fontWeight={active ? "semibold" : "normal"}>
                {tab.label}
              </Text>

              {tab.badge && (
                <Box
                  position="absolute"
                  top={1}
                  right="25%"
                  bg="red.500"
                  color="white"
                  borderRadius="full"
                  minW={5}
                  h={5}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  fontSize="xs"
                  fontWeight="bold"
                >
                  {tab.badge}
                </Box>
              )}

              {active && enableAnimations && (
                <MotionBox
                  position="absolute"
                  bottom="0"
                  height="2px"
                  width="50%"
                  bg="blue.500"
                  layoutId="activeTab"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2 }}
                  borderRadius="full"
                />
              )}
            </MotionFlex>
          );
        })}
      </Flex>
    </MotionBox>
  );
};

export default MobileNavBar;
