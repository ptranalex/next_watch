"use client";

import React from "react";
import {
  Box,
  HStack,
  Text,
  IconButton,
  useColorModeValue,
} from "@chakra-ui/react";
import { HiChevronLeft, HiChevronRight } from "react-icons/hi2";

interface SearchPaginationProps {
  currentPage: number;
  totalResults: number;
  resultsPerPage: number;
  hasNext: boolean;
  onPageChange: (page: number) => void;
}

/**
 * SearchPagination - Pagination component for search results
 *
 * Provides navigation between pages of search results with
 * previous/next buttons and page information.
 */
export function SearchPagination({
  currentPage,
  totalResults,
  resultsPerPage,
  hasNext,
  onPageChange,
}: SearchPaginationProps): React.JSX.Element {
  const bgColor = useColorModeValue("bg.secondary", "bg.secondary");
  const borderColor = useColorModeValue("border.subtle", "border.subtle");

  const totalPages = Math.ceil(totalResults / resultsPerPage);
  const hasPrevious = currentPage > 1;

  const startResult = (currentPage - 1) * resultsPerPage + 1;
  const endResult = Math.min(currentPage * resultsPerPage, totalResults);

  const handlePreviousPage = () => {
    if (hasPrevious) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (hasNext) {
      onPageChange(currentPage + 1);
    }
  };

  return (
    <Box
      p={4}
      bg={bgColor}
      borderRadius="lg"
      border="1px"
      borderColor={borderColor}
    >
      <HStack justify="space-between" align="center">
        {/* Results info */}
        <Text fontSize="sm" color="text.secondary">
          Showing {startResult}-{endResult} of {totalResults} results
        </Text>

        {/* Pagination controls */}
        <HStack spacing={2}>
          <IconButton
            aria-label="Previous page"
            icon={<HiChevronLeft />}
            onClick={handlePreviousPage}
            isDisabled={!hasPrevious}
            variant="outline"
            size="sm"
          />

          <Text
            fontSize="sm"
            fontWeight="medium"
            minW="60px"
            textAlign="center"
          >
            Page {currentPage} of {totalPages}
          </Text>

          <IconButton
            aria-label="Next page"
            icon={<HiChevronRight />}
            onClick={handleNextPage}
            isDisabled={!hasNext}
            variant="outline"
            size="sm"
          />
        </HStack>
      </HStack>
    </Box>
  );
}
