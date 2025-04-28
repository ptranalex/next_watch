"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Box, Flex, Button, HStack, useColorMode } from "@chakra-ui/react";
import SearchInput from "@/src/components/common/SearchInput";
import { useAuth } from "@/src/context/AuthContext";
import { useMovieQuery } from "@/src/context/MovieQueryContext";

const NavBar: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { user, logout } = useAuth();
  const { reset } = useMovieQuery();
  const router = useRouter();

  const handleLogoClick = () => {
    reset();
    router.push("/");
  };

  return (
    <Box
      as="nav"
      bg={colorMode === "dark" ? "gray.800" : "blue.500"}
      py={4}
      px={6}
    >
      <Flex justify="space-between" align="center">
        <Box
          fontWeight="bold"
          fontSize="xl"
          color="white"
          cursor="pointer"
          onClick={handleLogoClick}
        >
          MovieWatch
        </Box>

        <SearchInput />

        <HStack spacing={4}>
          <Button
            size="sm"
            onClick={toggleColorMode}
            variant="ghost"
            color="white"
          >
            {colorMode === "dark" ? "Light" : "Dark"} Mode
          </Button>

          {user ? (
            <>
              <Link href="/profile">
                <Button size="sm" colorScheme="blue">
                  Profile
                </Button>
              </Link>
              <Button size="sm" onClick={logout} colorScheme="red">
                Logout
              </Button>
            </>
          ) : (
            <Link href="/login">
              <Button size="sm" colorScheme="green">
                Login
              </Button>
            </Link>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default NavBar;
