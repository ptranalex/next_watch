import React, { useEffect } from "react";
import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import { usePathname, useRouter } from "next/navigation";
import { HiHome, HiHeart, HiBookmark, HiSearch, HiUser } from "react-icons/hi";
import { motion } from "framer-motion";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MobileNavBar");

interface NavItem {
  name: string;
  icon: React.ElementType;
  path: string;
}

// Motion Box for animations
const MotionBox = motion(Box);
const MotionFlex = motion(Flex);

/**
 * MobileNavBar component
 * Mobile-optimized bottom navigation bar with large touch-friendly tabs
 * Features:
 * - Native app-like animations
 * - Haptic feedback
 * - Safe area padding for iOS devices
 * - Optimized touch targets
 */
const MobileNavBar: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  // Define navigation items
  const navItems: NavItem[] = [
    { name: "Home", icon: HiHome, path: "/" },
    { name: "Search", icon: HiSearch, path: "/search" },
    { name: "Watchlist", icon: HiBookmark, path: "/watchlist" },
    { name: "Favorites", icon: HiHeart, path: "/favorites" },
    { name: "Profile", icon: HiUser, path: "/profile" },
  ];

  // Apply haptic feedback when buttons are pressed
  const applyHapticFeedback = () => {
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(20);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }
  };

  // Handle navigation
  const handleNavigation = (path: string) => {
    applyHapticFeedback();
    router.push(path);
  };

  // Check if nav item is active
  const isActive = (path: string): boolean => {
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname.startsWith(path)) return true;
    return false;
  };

  useEffect(() => {
    logger.debug(`Current pathname: ${pathname}`);
  }, [pathname]);

  return (
    <MotionBox
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      zIndex={1000}
      bg={bgColor}
      borderTop="1px"
      borderColor={borderColor}
      paddingBottom="env(safe-area-inset-bottom, 8px)"
      paddingTop={2}
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3 }}
      display={{ base: "block", md: "none" }} // Only show on mobile
    >
      <Flex justify="space-around" align="center" width="100%">
        {navItems.map((item) => {
          const active = isActive(item.path);
          return (
            <MotionFlex
              key={item.name}
              direction="column"
              align="center"
              justify="center"
              py={2}
              px={1}
              cursor="pointer"
              onClick={() => handleNavigation(item.path)}
              flex={1}
              color={active ? "blue.500" : "gray.500"}
              whileTap={{ scale: 0.95 }}
              position="relative"
            >
              <Icon as={item.icon} boxSize={6} mb={1} />
              <Text fontSize="xs" fontWeight={active ? "semibold" : "normal"}>
                {item.name}
              </Text>

              {active && (
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
