"use client";

import { Genre } from "@/domain/entities";
import {
  Box,
  Link as ChakraLink,
  Heading,
  HStack,
  Icon,
  SkeletonText,
  Text,
} from "@chakra-ui/react";
import Link from "next/link";
import { memo } from "react";
import {
  GiAlienSkull,
  GiFairyWand,
  GiGhost,
  GiMagnifyingGlass,
  GiPistolGun,
  GiPunch,
} from "react-icons/gi";
import { MdOutlineTheaterComedy } from "react-icons/md";
import { PiMaskSad } from "react-icons/pi";

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
  id: number;
}

// Memoized NavLink component with prefetching to prevent unnecessary re-renders
const NavLink = memo<NavItem>(({ icon, label, path }) => {
  return (
    <ChakraLink as={Link} href={path}>
      <HStack marginBottom={3}>
        <Icon as={icon} boxSize={6} color="text.tertiary" />
        <Text>{label}</Text>
      </HStack>
    </ChakraLink>
  );
});
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

interface GenreContentProps {
  genres: Genre[];
  isLoading?: boolean;
  error?: Error | null;
}

// Memoized genre content component - follows the pattern of other sections in SideBar
const GenreContent = memo<GenreContentProps>(({ genres, isLoading, error }) => {
  // Default icon for genres without a specific icon
  const defaultIcon = GiPunch;

  if (isLoading) {
    return (
      <Box>
        <SkeletonText noOfLines={6} spacing={3} skeletonHeight={3} />
      </Box>
    );
  }

  if (error) {
    return <Text color="feedback.error">Error loading genres</Text>;
  }

  if (!genres || genres.length === 0) {
    return <Text color="text.tertiary">No genres available</Text>;
  }

  return (
    <>
      {genres.map((genre: Genre) => (
        <NavLink
          key={genre.id}
          icon={genreIcons[genre.name] || defaultIcon}
          label={genre.name}
          path={`/genres/${genre.id}`}
          id={genre.id}
        />
      ))}
    </>
  );
});
GenreContent.displayName = "GenreContent";

interface GenreSectionProps {
  genres: Genre[];
  isLoading?: boolean;
  error?: Error | null;
}

// Genre section wrapper with consistent style matching other SideBar sections
const GenreSection = memo<GenreSectionProps>(({ genres, isLoading, error }) => {
  return (
    <>
      <Heading fontSize="xl" marginTop={5} marginBottom={3}>
        Genres
      </Heading>
      <GenreContent genres={genres} isLoading={isLoading} error={error} />
    </>
  );
});
GenreSection.displayName = "GenreSection";

export default GenreSection;
