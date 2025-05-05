import { Menu, Button, MenuButton, MenuList, MenuItem } from "@chakra-ui/react";
import { BsChevronDown } from "react-icons/bs";
import { useMovieQuery } from "@/context/MovieQueryContext";
import { useEffect } from "react";

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

  // Add a console log to debug state changes
  console.log("SortSelector - Current sort state:", {
    sortOrder,
    sortDesc,
    currentLabel: currentSortOrder?.label || "None",
  });

  // Monitor for changes
  useEffect(() => {
    console.log("SortSelector - Sort changed to:", {
      sortOrder,
      sortDesc,
      currentLabel: currentSortOrder?.label || "None",
    });
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
              console.log(
                "SortSelector - Setting sort:",
                order.value,
                order.desc ?? false,
                order.label
              );
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
