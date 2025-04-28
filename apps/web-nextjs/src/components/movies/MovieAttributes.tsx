"use client";

import {
  Box,
  SimpleGrid,
  Text,
  Icon,
  Flex,
  useColorModeValue,
  Tooltip,
} from "@chakra-ui/react";
import {
  HiClock,
  HiCalendar,
  HiLanguage,
  HiCurrencyDollar,
  HiStar,
} from "react-icons/hi2";
import { HiGlobeAlt } from "react-icons/hi";

interface MovieAttributesProps {
  runtime?: number; // in minutes
  releaseDate?: string;
  language?: string;
  countries?: string[];
  revenue?: number; // in dollars
  budget?: number; // in dollars
  voteCount?: number;
}

export default function MovieAttributes({
  runtime,
  releaseDate,
  language,
  countries,
  revenue,
  budget,
  voteCount,
}: MovieAttributesProps) {
  const bgColor = useColorModeValue("gray.50", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  // Format runtime from minutes to hours and minutes
  const formatRuntime = (minutes: number): string => {
    if (!minutes) return "N/A";
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  // Format date
  const formatDate = (dateString?: string): string => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  // Format currency
  const formatCurrency = (amount?: number): string => {
    if (!amount) return "N/A";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(amount);
  };

  // Format countries list
  const formatCountries = (countries?: string[]): string => {
    if (!countries || countries.length === 0) return "N/A";
    return countries.join(", ");
  };

  const attributes = [
    {
      icon: HiClock,
      label: "Runtime",
      value: runtime ? formatRuntime(runtime) : "N/A",
      tooltip: "Movie runtime",
    },
    {
      icon: HiCalendar,
      label: "Release Date",
      value: formatDate(releaseDate),
      tooltip: "Release date",
    },
    {
      icon: HiLanguage,
      label: "Language",
      value: language || "N/A",
      tooltip: "Original language",
    },
    {
      icon: HiGlobeAlt,
      label: "Countries",
      value: formatCountries(countries),
      tooltip: "Production countries",
    },
    {
      icon: HiCurrencyDollar,
      label: "Budget",
      value: formatCurrency(budget),
      tooltip: "Production budget",
    },
    {
      icon: HiCurrencyDollar,
      label: "Revenue",
      value: formatCurrency(revenue),
      tooltip: "Box office revenue",
    },
    {
      icon: HiStar,
      label: "Vote Count",
      value: voteCount ? voteCount.toLocaleString() : "N/A",
      tooltip: "Number of votes",
    },
  ];

  return (
    <SimpleGrid columns={{ base: 2, md: 3, lg: 6 }} spacing={4} my={6}>
      {attributes.map((attr, index) => (
        <Tooltip key={index} label={attr.tooltip} placement="top">
          <Box
            borderWidth="1px"
            borderColor={borderColor}
            borderRadius="md"
            bg={bgColor}
            p={3}
            textAlign="center"
          >
            <Flex direction="column" align="center">
              <Icon as={attr.icon} boxSize={6} color="blue.500" mb={2} />
              <Text fontSize="sm" color="gray.500" mb={1}>
                {attr.label}
              </Text>
              <Text fontWeight="medium" fontSize="sm">
                {attr.value}
              </Text>
            </Flex>
          </Box>
        </Tooltip>
      ))}
    </SimpleGrid>
  );
}
