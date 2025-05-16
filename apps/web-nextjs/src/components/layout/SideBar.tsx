"use client";

import { useAuth } from "@/hooks";
import useMovieFilterStore from "@/store/movieFilterStore";
import {
  Box,
  Link as ChakraLink,
  Heading,
  HStack,
  Icon,
  Text,
  VStack,
  useBreakpointValue,
  Divider,
} from "@chakra-ui/react";
import Link from "next/link";
import { memo, useCallback, useMemo } from "react";
import { GiCalendar, GiLaurelCrown, GiTrophy } from "react-icons/gi";
import {
  HiBookmark,
  HiCheckBadge,
  HiDocumentCheck,
  HiHeart,
  HiAdjustmentsHorizontal,
} from "react-icons/hi2";
import MovieFilter from "@/components/home/MovieFilter";
import GenreSection from "@/components/navigation/GenreSection";

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
}

// Memoized NavLink component to prevent unnecessary re-renders
const NavLink = memo<NavItem>(({ icon, label, path }) => (
  <ChakraLink as={Link} href={path}>
    <HStack marginBottom={3}>
      <Icon as={icon} boxSize={6} color="gray.500" />
      <Text>{label}</Text>
    </HStack>
  </ChakraLink>
));
NavLink.displayName = "NavLink";

// Filter section wrapper - DON'T memoize this component as it needs to respond to filter changes
const FilterSection = () => {
  // Get current filter values from store to force re-renders when they change
  const { filters } = useMovieFilterStore();

  return (
    <>
      <Heading fontSize="xl" marginTop={5} marginBottom={3}>
        Filter
      </Heading>
      <MovieFilter />
    </>
  );
};

// Memoized HomeLink component
const HomeLink = memo(() => (
  <Heading fontSize="xl" marginTop={10} marginBottom={3}>
    <ChakraLink as={Link} href="/">
      Home
    </ChakraLink>
  </Heading>
));
HomeLink.displayName = "HomeLink";

// Memoized UserNavSection component
const UserNavSection = memo(({ items }: { items: NavItem[] }) => {
  if (items.length === 0) return null;

  return (
    <>
      <Heading fontSize="xl" marginTop={5} marginBottom={3}>
        My Lists
      </Heading>
      {items.map((item) => (
        <NavLink key={item.path} {...item} />
      ))}
    </>
  );
});
UserNavSection.displayName = "UserNavSection";

// Memoized TopNavSection component
const TopNavSection = memo(({ items }: { items: NavItem[] }) => (
  <>
    <Heading fontSize="xl" marginTop={5} marginBottom={3}>
      Top
    </Heading>
    {items.map((item) => (
      <NavLink key={item.path} {...item} />
    ))}
  </>
));
TopNavSection.displayName = "TopNavSection";

const SideBar: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const isMobile = useBreakpointValue({ base: true, md: false });

  // Memoize navigation items to prevent recreating on every render
  const userNavItems = useMemo<NavItem[]>(() => {
    if (!isAuthenticated) return [];

    return [
      { icon: HiBookmark, label: "Watch List", path: "/watchlist" },
      { icon: HiHeart, label: "Favorites", path: "/favorites" },
      { icon: HiDocumentCheck, label: "History", path: "/history" },
      { icon: HiCheckBadge, label: "Our Picks", path: "/recommended" },
    ];
  }, [isAuthenticated]);

  const topNavItems = useMemo<NavItem[]>(
    () => [
      { icon: GiTrophy, label: "Best of Year", path: "/top/current-year" },
      { icon: GiCalendar, label: "Popular in 2024", path: "/top/2024" },
      { icon: GiCalendar, label: "Popular by 2023", path: "/top/2023" },
      { icon: GiLaurelCrown, label: "All time top", path: "/top/all-time" },
    ],
    []
  );

  // Don't render on mobile devices
  if (isMobile) {
    return null;
  }

  return (
    <Box>
      <HomeLink />
      <UserNavSection items={userNavItems} />
      <FilterSection />
      <TopNavSection items={topNavItems} />
      <GenreSection />
    </Box>
  );
};

export default memo(SideBar);
