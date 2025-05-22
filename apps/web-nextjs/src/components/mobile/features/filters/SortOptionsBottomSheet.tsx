import React from "react";
import { useColorModeValue, Text, VStack, Flex, Box } from "@chakra-ui/react";
import useMovieFilterStore from "@/store/movieFilterStore";
import { BottomSheet } from "@/components/mobile/ui/bottom-sheet";
import { createLogger } from "@/utils/logging";
import { HiCheck } from "react-icons/hi";

// Create logger for this component
const logger = createLogger("SortOptionsBottomSheet");

interface SortOptionsBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

// Same sort options as the original component
const sortOrders = [
  { value: "title", label: "Name", desc: false },
  { value: "release_date", label: "Release date", desc: true },
  { value: "imdb_rating", label: "IMDB rating", desc: true },
  { value: "imdb_rating", label: "IMDB rating (Asc)", desc: false },
  {
    value: "rotten_tomatoes_rating",
    label: "Rotten Tomatoes rating",
    desc: true,
  },
  { value: "metacritic_rating", label: "Metacritic rating", desc: true },
  { value: "vote_count", label: "Popularity", desc: true },
];

/**
 * SortOptionsBottomSheet component
 * A mobile-optimized sort interface using the BottomSheet pattern
 * Replaces the dropdown-based approach for a more touch-friendly experience
 */
const SortOptionsBottomSheet: React.FC<SortOptionsBottomSheetProps> = ({
  isOpen,
  onClose,
}) => {
  const textColor = useColorModeValue("black", "white");
  const activeColor = useColorModeValue("blue.500", "blue.300");
  const hoverBg = useColorModeValue("gray.100", "gray.700");

  // Get filters and the setSorting method from the store
  const { filters, setSorting } = useMovieFilterStore();
  const { sortOrder, sortDesc } = filters;

  // Find the current sort order for display
  const currentSortOrder = sortOrders.find(
    (order) => order.value === sortOrder && order.desc === sortDesc
  );

  const handleSortChange = (value: string, desc: boolean) => {
    logger.info(`Setting sort to: ${value}, desc: ${desc}`);
    setSorting(value, desc);
    onClose();
  };

  return (
    <BottomSheet
      isOpen={isOpen}
      onClose={onClose}
      title="Sort By"
      enableHaptics={true}
      minHeight="auto"
    >
      <VStack spacing={0} align="stretch" color={textColor} pt={2}>
        {sortOrders.map((order) => {
          const isActive =
            order.value === currentSortOrder?.value &&
            order.desc === currentSortOrder?.desc;

          return (
            <Flex
              key={`${order.value}-${order.desc ? "desc" : "asc"}`}
              px={4}
              py={4}
              alignItems="center"
              justifyContent="space-between"
              borderBottomWidth="1px"
              borderColor="gray.200"
              _dark={{ borderColor: "gray.700" }}
              onClick={() => handleSortChange(order.value, order.desc ?? true)}
              cursor="pointer"
              bg={isActive ? hoverBg : "transparent"}
              _hover={{ bg: hoverBg }}
              transition="background 0.2s"
              borderRadius="md"
            >
              <Text
                fontWeight={isActive ? "bold" : "normal"}
                color={isActive ? activeColor : "inherit"}
                fontSize="lg"
              >
                {order.label}
              </Text>

              {isActive && (
                <Box color={activeColor} fontSize="xl">
                  <HiCheck />
                </Box>
              )}
            </Flex>
          );
        })}
      </VStack>
    </BottomSheet>
  );
};

export default SortOptionsBottomSheet;
