"use client";

import { Genre } from "@/domain/entities";
import { MovieAPI } from "@/services/api";
import {
  Box,
  Link as ChakraLink,
  Heading,
  HStack,
  Icon,
  SkeletonText,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { memo, useCallback } from "react";
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
import { usePrefetch } from "@/hooks/performance/usePrefetch";

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
  id: number;
}

// Memoized NavLink component with prefetching to prevent unnecessary re-renders
const NavLink = memo<NavItem>(({ icon, label, path, id }) => {
  const { prefetchGenre } = usePrefetch();

  // Start prefetching on mouse hover
  const handleHover = useCallback(() => {
    prefetchGenre(id);
  }, [id, prefetchGenre]);

  return (
    <ChakraLink as={Link} href={path} onMouseEnter={handleHover}>
      <HStack marginBottom={3}>
        <Icon as={icon} boxSize={6} color="gray.500" />
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
          id={genre.id}
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
      <Heading fontSize="xl" marginTop={5} marginBottom={3}>
        Genre
      </Heading>
      <GenreContent />
    </VStack>
  );
});
GenreSection.displayName = "GenreSection";

export default GenreSection;
