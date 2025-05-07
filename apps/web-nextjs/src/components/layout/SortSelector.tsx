import { useMovieQuery } from "@/context/MovieQueryContext";
import { Button, Menu, MenuButton, MenuItem, MenuList } from "@chakra-ui/react";
import { useEffect } from "react";
import { BsChevronDown } from "react-icons/bs";

const SortSelector = () => {
  const sortOrders = [
    { value: "title", label: "Name" },
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

  const { movieQuery, setSorting } = useMovieQuery();
  const sortOrder = movieQuery.sortOrder;
  const sortDesc = movieQuery.sortDesc;

  // Debug current selection
  const currentSortOrder = sortOrders.find(
    (order) => order.value === sortOrder && order.desc === sortDesc
  );

  // Monitor for changes
  useEffect(() => {
    // No console.log needed here
  }, [sortOrder, sortDesc, currentSortOrder]);

  return (
    <Menu>
      <MenuButton as={Button} rightIcon={<BsChevronDown />}>
        Order by: {currentSortOrder?.label || "Release date"}
      </MenuButton>
      <MenuList>
        {sortOrders.map((order) => (
          <MenuItem
            onClick={() => {
              setSorting(order.value, order.desc ?? false);
            }}
            key={`${order.value}-${order.desc ? "desc" : "asc"}`}
          >
            {order.label}
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
};

export default SortSelector;
