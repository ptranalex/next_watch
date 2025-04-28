"use client";

import React, { useState } from "react";
import { Input, InputGroup, InputRightElement, Icon } from "@chakra-ui/react";
import { FaSearch } from "react-icons/fa";
import { useRouter } from "next/navigation";

const SearchInput: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const router = useRouter();

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    if (searchText) {
      router.push(`/search?q=${encodeURIComponent(searchText)}`);
    }
  };

  return (
    <form onSubmit={handleSearch} style={{ width: "100%", maxWidth: "400px" }}>
      <InputGroup>
        <Input
          placeholder="Search for movies..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          bg="whiteAlpha.200"
          color="white"
          border="none"
          _placeholder={{ color: "whiteAlpha.700" }}
        />
        <InputRightElement>
          <Icon
            as={FaSearch}
            color="whiteAlpha.700"
            cursor="pointer"
            onClick={handleSearch}
          />
        </InputRightElement>
      </InputGroup>
    </form>
  );
};

export default SearchInput;
