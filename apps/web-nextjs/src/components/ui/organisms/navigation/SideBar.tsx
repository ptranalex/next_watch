"use client";

import useMovieFilterStore from "@/store/movieFilterStore";
import {
  Box,
  Link as ChakraLink,
  Heading,
  HStack,
  Icon,
  Text,
  useBreakpointValue,
  Spinner,
  Center,
} from "@chakra-ui/react";
import Link from "next/link";
import { memo } from "react";
import { useSidebarData } from "@/services/hooks/navigation/useSidebarData";
import { MovieFilter } from "@/components/features/movies/filter";
import { GenreSection } from "./sections";
import { IconType } from "react-icons";
import { FaTrophy, FaCalendar, FaHeart } from "react-icons/fa";
import { MdBookmark, MdHistory, MdCheckCircle } from "react-icons/md";
import { HiDocumentCheck } from "react-icons/hi2";
import { BsCheck2Circle } from "react-icons/bs";

interface FilterDefaults {
  rating_imdb: number | null;
  year: number | null;
}

interface NavLinkProps {
  icon: IconType;
  label: string;
  path: string;
}

interface FilterSectionProps {
  show: boolean;
  defaults: FilterDefaults;
  locked: string[];
}

interface HomeLinkProps {
  label: string;
  href: string;
}

interface NavSectionProps {
  items: Array<{
    id: string;
    label: string;
    href: string;
    icon: IconType;
  }>;
}

// Map of icon string names to IconType components
const iconMap: Record<string, IconType> = {
  trophy: FaTrophy,
  calendar: FaCalendar,
  heart: FaHeart,
  bookmark: MdBookmark,
  "document-check": HiDocumentCheck,
  "check-badge": BsCheck2Circle,
  history: MdHistory,
  recommended: MdCheckCircle,
};
const defaultIcon: IconType = FaTrophy;

// Memoized NavLink component to prevent unnecessary re-renders
const NavLink = memo<NavLinkProps>(({ icon, label, path }) => (
  <ChakraLink as={Link} href={path}>
    <HStack marginBottom={3}>
      <Icon as={icon} boxSize={6} color="text.tertiary" />
      <Text>{label}</Text>
    </HStack>
  </ChakraLink>
));
NavLink.displayName = "NavLink";

// Filter section wrapper - DON'T memoize this component as it needs to respond to filter changes
export const FilterSection: React.FC<FilterSectionProps> =
  function FilterSection({ show }) {
    // Access store to force re-renders when filters change
    useMovieFilterStore();

    if (!show) return null;

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
const HomeLink = memo<HomeLinkProps>(({ label, href }) => (
  <Heading fontSize="xl" marginTop={10} marginBottom={3}>
    <ChakraLink as={Link} href={href}>
      {label}
    </ChakraLink>
  </Heading>
));
HomeLink.displayName = "HomeLink";

// Memoized UserNavSection component
const UserNavSection = memo<NavSectionProps>(({ items }) => {
  if (items.length === 0) return null;

  return (
    <>
      <Heading fontSize="xl" marginTop={5} marginBottom={3}>
        My Lists
      </Heading>
      {items.map((item) => (
        <NavLink key={item.id} {...item} path={item.href} />
      ))}
    </>
  );
});
UserNavSection.displayName = "UserNavSection";

// Memoized TopNavSection component
const TopNavSection = memo<NavSectionProps>(({ items }) => (
  <>
    <Heading fontSize="xl" marginTop={5} marginBottom={3}>
      Top
    </Heading>
    {items.map((item) => (
      <NavLink key={item.id} {...item} path={item.href} />
    ))}
  </>
));
TopNavSection.displayName = "TopNavSection";

const SideBar: React.FC = () => {
  const { data: sidebarData, isLoading, error } = useSidebarData();
  const isMobile = useBreakpointValue({ base: true, md: false });

  // Don't render on mobile devices
  if (isMobile) {
    return null;
  }

  if (isLoading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (error || !sidebarData) {
    return null;
  }

  // Convert icon string to IconType component using iconMap
  const userLinks = sidebarData.user_links.map((link) => ({
    ...link,
    icon: iconMap[link.icon ?? ""] || defaultIcon,
  }));

  const topLinks = sidebarData.top_links.map((link) => ({
    ...link,
    icon: iconMap[link.icon ?? ""] || defaultIcon,
  }));

  return (
    <Box>
      <HomeLink {...sidebarData.home} />
      <UserNavSection items={userLinks} />
      <FilterSection
        show={sidebarData.filters.show}
        defaults={sidebarData.filters.defaults}
        locked={sidebarData.filters.locked}
      />
      <TopNavSection items={topLinks} />
      <GenreSection genres={sidebarData.genres} />
    </Box>
  );
};

export default memo(SideBar);
