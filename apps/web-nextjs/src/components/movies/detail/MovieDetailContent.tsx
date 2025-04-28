"use client";

import {
  Box,
  Heading,
  Text,
  Stack,
  Image,
  Spinner,
  Flex,
  Divider,
  Alert,
  AlertIcon,
} from "@chakra-ui/react";
import TrailerCard from "../TrailerCard";
import MovieAttributes from "../MovieAttributes";
import ActorsGallery from "../ActorsGallery";
import CriticScore from "../CriticScore";
import RatingGroup from "../RatingGroup";
import ForceSyncButton from "../ForceSyncButton";
import RelatedMovies from "./RelatedMovies";
import useMovie from "@/src/hooks/useMovie";
import useMovieCast from "@/src/hooks/useMovieCast";
import config from "@/src/config";
import { Movie as MovieType } from "@/src/services/movie-service";

interface MovieDetailContentProps {
  movieId: string;
}

// Extended movie interface to include additional fields we need
interface ExtendedMovie extends MovieType {
  // Video data type
  videos?: {
    id: string;
    key: string;
    name: string;
    site: "YouTube" | "Vimeo";
    type: string;
  }[];
  // External ratings not in the Movie interface
  rt_rating?: number;
  metacritic_rating?: number;
  // Additional fields for the UI
  rated?: string;
}

export default function MovieDetailContent({
  movieId,
}: MovieDetailContentProps) {
  // Fetch movie data using the hooks
  const {
    data: movieData,
    isLoading: isMovieLoading,
    error: movieError,
    refetch: refetchMovie,
  } = useMovie(movieId);

  // Fetch cast data using the hooks
  const { data: castData, isLoading: isCastLoading } = useMovieCast(movieId);

  // Handle loading state
  if (isMovieLoading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    );
  }

  // Handle error state
  if (movieError || !movieData) {
    return (
      <Alert status="error">
        <AlertIcon />
        {movieError
          ? `Error loading movie: ${
              movieError instanceof Error ? movieError.message : "Unknown error"
            }`
          : "Movie not found"}
      </Alert>
    );
  }

  // Cast movieData to our extended type that includes videos and external ratings
  const movie = movieData as ExtendedMovie;

  // Convert API ratings format to RatingGroup component format
  const formatRatings = () => {
    const ratings = [];

    if (movie.imdb_rating) {
      ratings.push({
        source: "IMDb",
        value: movie.imdb_rating,
        maxValue: 10,
        logo: "https://upload.wikimedia.org/wikipedia/commons/6/69/IMDB_Logo_2016.svg",
      });
    }

    if (movie.rt_rating) {
      ratings.push({
        source: "Rotten Tomatoes",
        value: movie.rt_rating,
        maxValue: 100,
        logo: "https://upload.wikimedia.org/wikipedia/commons/5/5b/Rotten_Tomatoes.svg",
      });
    }

    if (movie.metacritic_rating) {
      ratings.push({
        source: "Metacritic",
        value: movie.metacritic_rating,
        maxValue: 100,
        logo: "https://upload.wikimedia.org/wikipedia/commons/2/20/Metacritic.svg",
      });
    }

    return ratings;
  };

  // Format cast data for ActorsGallery component
  const formatCast = () => {
    if (!castData || !castData.cast) return [];

    return castData.cast.map((member) => ({
      id: member.actor_id.toString(),
      name: member.name,
      character: member.character || "Unknown Character",
      profile_path: member.profile_path
        ? `${config.cdn.imagesCdnUrl}/${config.cdn.profileSize}${member.profile_path}`
        : "https://via.placeholder.com/150x225?text=No+Image",
    }));
  };

  // Format trailer data
  const formatTrailer = () => {
    if (!movie.videos || movie.videos.length === 0) return null;

    const trailer =
      movie.videos.find((video) => video.type === "Trailer") || movie.videos[0];
    return {
      id: trailer.key,
      title: trailer.name || "Official Trailer",
      site: trailer.site as "YouTube" | "Vimeo",
    };
  };

  const ratings = formatRatings();
  const cast = formatCast();
  const trailer = formatTrailer();

  // Safe date extraction to avoid errors with undefined dates
  const releaseYear = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : "Unknown";

  return (
    <Box>
      <Flex direction={{ base: "column", md: "row" }} gap={6} mb={8}>
        <Box flexShrink={0}>
          <Image
            src={
              movie.poster_path
                ? `${config.cdn.imagesCdnUrl}/${config.cdn.posterSize}${movie.poster_path}`
                : "https://via.placeholder.com/300x450"
            }
            alt={movie.title}
            borderRadius="md"
            objectFit="cover"
            maxW={{ base: "100%", md: "300px" }}
          />
        </Box>

        <Stack spacing={4}>
          <Flex justify="space-between" align="center">
            <Heading as="h2" size="xl">
              {movie.title}
            </Heading>
            <ForceSyncButton
              movieId={movieId}
              iconOnly
              size="sm"
              colorScheme="teal"
              onSuccess={() => {
                refetchMovie();
              }}
            />
          </Flex>

          <Flex align="center" gap={2}>
            <Text fontSize="md">
              {releaseYear} • {movie.rated || "N/R"} • {movie.runtime || 0} min
            </Text>
            <CriticScore score={Math.round((movie.vote_average || 0) * 10)} />
          </Flex>

          <Text fontSize="md" fontWeight="medium">
            {movie.genres && movie.genres.length > 0
              ? movie.genres.map((g) => g.name).join(", ")
              : ""}
          </Text>

          <Box>
            <Heading as="h3" size="md" mb={2}>
              Overview
            </Heading>
            <Text>{movie.overview || "No overview available."}</Text>
          </Box>

          {ratings.length > 0 && (
            <Box mt={4}>
              <Heading as="h3" size="sm" mb={3}>
                Ratings
              </Heading>
              <RatingGroup ratings={ratings} />
            </Box>
          )}
        </Stack>
      </Flex>

      {/* Movie attributes */}
      <MovieAttributes
        runtime={movie.runtime || 0}
        releaseDate={movie.release_date || ""}
        language={movie.original_language || "Unknown"}
        countries={movie.production_countries?.map((c) => c.name) || []}
        revenue={movie.revenue || 0}
        budget={movie.budget || 0}
        voteCount={movie.vote_count || 0}
      />

      <Divider my={8} />

      {/* Trailer */}
      {trailer && (
        <Box mb={8}>
          <Heading as="h3" size="md" mb={4}>
            Trailer
          </Heading>
          <Box maxW="600px">
            <TrailerCard
              id={trailer.id}
              title={trailer.title}
              site={trailer.site}
            />
          </Box>
        </Box>
      )}

      <Divider my={8} />

      {/* Cast */}
      {!isCastLoading && cast.length > 0 && (
        <ActorsGallery actors={cast} title="Cast" />
      )}

      {/* Related Movies */}
      <Divider my={8} />
      <RelatedMovies movieId={movieId} />
    </Box>
  );
}
