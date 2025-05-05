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
import useMovieQueryStore from "../../store/movieQuery";
import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";
import { Genre } from "@/domain/entities";
import { Suspense, lazy } from "react";

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
}

const NavLink: React.FC<NavItem> = ({ icon, label, path }) => (
  <ChakraLink as={Link} href={path}>
    <HStack marginBottom={3}>
      <Icon as={icon} boxSize={6} color="gray.500" />
      <Text>{label}</Text>
    </HStack>
  </ChakraLink>
);

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

// Lazy-loaded genre section component
const GenreContent = () => {
  const { data: genres, isLoading } = useQuery({
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
};

// Genre section wrapper with its own heading
const GenreSection = () => {
  return (
    <VStack align="stretch" spacing={0}>
      <Heading fontSize="2xl" marginTop={9} marginBottom={3}>
        Genre
      </Heading>
      <GenreContent />
    </VStack>
  );
};

const LeftNavBar: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const resetFilters = useMovieQueryStore((state) => state.resetFilters);

  const userNavItems: NavItem[] = isAuthenticated
    ? [
        { icon: HiBookmark, label: "Watch List", path: "/watchlist" },
        { icon: HiHeart, label: "Favourite", path: "/favourite" },
        { icon: HiDocumentCheck, label: "History", path: "/history" },
        { icon: HiCheckBadge, label: "Our Picks", path: "/recommended" },
      ]
    : [];

  const topNavItems: NavItem[] = [
    { icon: GiTrophy, label: "Best of Year", path: "/top-year" },
    { icon: GiCalendar, label: "Popular in 2023", path: "/top-year-2023" },
    { icon: GiCalendar, label: "Popular in 2022", path: "/top-year-2022" },
    {
      icon: GiLaurelCrown,
      label: "All time top 250",
      path: "/top-250-all-time",
    },
  ];

  return (
    <>
      <Heading fontSize="2xl" marginTop={9} marginBottom={3}>
        <ChakraLink as={Link} href="/" onClick={resetFilters}>
          Home
        </ChakraLink>
      </Heading>

      {isAuthenticated &&
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

export default LeftNavBar;
