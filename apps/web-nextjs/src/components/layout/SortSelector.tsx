"use client";

import { Menu, Button, MenuButton, MenuList, MenuItem } from "@chakra-ui/react";
import { BsChevronDown } from "react-icons/bs";
import { useMovieQuery } from "@/src/context/MovieQueryContext";

const SortSelector = () => {
  const sortOrders = [
    { value: "title", label: "Name" },
    { value: "released", label: "Release date" },
    { value: "-rating_imdb", label: "IMDB rating" },
    { value: "rating_imdb", label: "IMDB rating (Asc)" },
    { value: "-rating_rotten_tomatoes", label: "Rotten Tomatoes rating" },
    { value: "-rating_metacritic", label: "Metacritic rating" },
  ];

  const { movieQuery, setSortOrder } = useMovieQuery();
  const sortOrder = movieQuery.sortOrder;

  const currentSortOrder = sortOrders.find(
    (order) => order.value === sortOrder
  );

  return (
    <Menu>
      <MenuButton as={Button} rightIcon={<BsChevronDown />}>
        Order by: {currentSortOrder?.label || "Release date"}
      </MenuButton>
      <MenuList>
        {sortOrders.map((order) => (
          <MenuItem onClick={() => setSortOrder(order.value)} key={order.value}>
            {order.label}
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
};

export default SortSelector;
