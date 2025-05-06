import {
  Heading,
  Icon,
  Text,
  HStack,
  Link as ChakraLink,
  Box,
  SkeletonText,
  VStack,
} from "@chakra-ui/react";
import {
  GiAlienSkull,
  GiCalendar,
  GiFairyWand,
  GiGhost,
  GiLaurelCrown,
  GiMagnifyingGlass,
  GiPistolGun,
  GiPunch,
  GiTrophy,
} from "react-icons/gi";
import {
  HiBookmark,
  HiCheckBadge,
  HiDocumentCheck,
  HiHeart,
} from "react-icons/hi2";
import { MdOutlineTheaterComedy } from "react-icons/md";
import { PiMaskSad } from "react-icons/pi";
import Link from "next/link";
import { useAuth } from "@/hooks";
import useMovieQueryStore from "@/store/movieQuery";
import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";
import { Genre } from "@/domain/entities";
import { useCallback, useMemo, memo } from "react";

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

// Map of genre names to their icons
const genreIcons: Record<string, React.ElementType> = {
  Action: GiPunch,
  Thriller: GiPistolGun,
  Comedy: MdOutlineTheaterComedy,
  Drama: PiMaskSad,
  Fantasy: GiFairyWand,
  Horror: GiGhost,
  Mystery: GiMagnifyingGlass,
  "Sci-Fi": GiAlienSkull,
};

// Memoized genre content component
const GenreContent = memo(() => {
  const {
    data: genres,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["genres"],
    queryFn: () => MovieAPI.getAllGenres(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Default icon for genres without a specific icon
  const defaultIcon = GiPunch;

  if (isLoading) {
    return (
      <Box pl={6} pr={6}>
        <SkeletonText noOfLines={6} spacing={3} skeletonHeight={3} />
      </Box>
    );
  }

  if (error) {
    return <Text color="red.400">Error loading genres</Text>;
  }

  if (!genres || genres.length === 0) {
    return <Text color="gray.500">No genres available</Text>;
  }

  return (
    <>
      {genres.map((genre: Genre) => (
        <NavLink
          key={genre.id}
          icon={genreIcons[genre.name] || defaultIcon}
          label={genre.name}
          path={`/genres/${genre.id}`}
        />
      ))}
    </>
  );
});
GenreContent.displayName = "GenreContent";

// Genre section wrapper with its own heading - memoized
const GenreSection = memo(() => {
  return (
    <VStack align="stretch" spacing={0}>
      <Heading fontSize="2xl" marginTop={9} marginBottom={3}>
        Genre
      </Heading>
      <GenreContent />
    </VStack>
  );
});
GenreSection.displayName = "GenreSection";

const LeftNavBar: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const resetFilters = useMovieQueryStore((state) => state.resetFilters);

  // Memoize the reset filters function
  const handleResetFilters = useCallback(() => {
    resetFilters();
  }, [resetFilters]);

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
      { icon: GiTrophy, label: "Best of Year", path: "/top-year" },
      { icon: GiCalendar, label: "Popular in 2023", path: "/top-year-2023" },
      { icon: GiCalendar, label: "Popular in 2022", path: "/top-year-2022" },
      {
        icon: GiLaurelCrown,
        label: "All time top 250",
        path: "/top-250-all-time",
      },
    ],
    []
  );

  return (
    <>
      <Heading fontSize="2xl" marginTop={9} marginBottom={3}>
        <ChakraLink as={Link} href="/" onClick={handleResetFilters}>
          Home
        </ChakraLink>
      </Heading>

      {userNavItems.length > 0 &&
        userNavItems.map((item) => <NavLink key={item.path} {...item} />)}

      <Heading fontSize="2xl" marginTop={9} marginBottom={3}>
        Top
      </Heading>
      {topNavItems.map((item) => (
        <NavLink key={item.path} {...item} />
      ))}

      {/* Genre section loads independently of the rest of the navigation */}
      <GenreSection />
    </>
  );
};

export default memo(LeftNavBar);
