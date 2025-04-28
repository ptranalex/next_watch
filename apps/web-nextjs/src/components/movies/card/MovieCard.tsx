"use client";

import React, { useState, useEffect } from "react";
import { Box, Image, Text, Badge, Flex, IconButton } from "@chakra-ui/react";
import { FaHeart, FaStar, FaBookmark } from "react-icons/fa";
import Link from "next/link";

interface Movie {
  id: number;
  title: string;
  posterPath: string;
  releaseDate: string;
  rating: number;
}

interface Props {
  movie: Movie;
}

const MovieCard: React.FC<Props> = ({ movie }) => {
  const posterUrl = movie.posterPath
    ? `https://image.tmdb.org/t/p/w500${movie.posterPath}`
    : "/placeholder-poster.jpg";

  return (
    <Box
      borderRadius="lg"
      overflow="hidden"
      bg="gray.700"
      transition="transform 0.2s"
      _hover={{ transform: "scale(1.03)" }}
    >
      <Link href={`/movies/${movie.id}`}>
        <Image src={posterUrl} alt={movie.title} width="100%" height="auto" />
      </Link>

      <Box p={3}>
        <Flex justify="space-between" align="center" mb={2}>
          <Badge colorScheme="teal" fontSize="0.8em">
            {new Date(movie.releaseDate).getFullYear()}
          </Badge>
          <Flex align="center">
            <FaStar color="gold" style={{ marginRight: "5px" }} />
            <Text fontSize="sm">{movie.rating.toFixed(1)}</Text>
          </Flex>
        </Flex>

        <Text fontWeight="semibold" noOfLines={2} mb={2}>
          {movie.title}
        </Text>

        <Flex justify="space-between">
          <IconButton
            aria-label="Add to favorites"
            icon={<FaHeart />}
            size="sm"
            variant="ghost"
            colorScheme="red"
          />
          <IconButton
            aria-label="Add to watchlist"
            icon={<FaBookmark />}
            size="sm"
            variant="ghost"
            colorScheme="blue"
          />
        </Flex>
      </Box>
    </Box>
  );
};

export default MovieCard;
