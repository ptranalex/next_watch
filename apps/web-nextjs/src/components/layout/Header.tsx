import React from "react";
import {
  Box,
  Flex,
  Button,
  Heading,
  HStack,
  IconButton,
  useColorMode,
} from "@chakra-ui/react";
import { MoonIcon, SunIcon, SearchIcon } from "@chakra-ui/icons";
import Link from "next/link";
import { useRouter } from "next/router";

const Header: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const router = useRouter();

  return (
    <Box as="header" bg="gray.800" px={4} py={2} shadow="md">
      <Flex
        justify="space-between"
        align="center"
        maxW="container.xl"
        mx="auto"
      >
        <Flex align="center">
          <Link href="/" passHref>
            <Heading as="h1" size="lg" cursor="pointer">
              NextWatch
            </Heading>
          </Link>

          <HStack spacing={4} ml={8} display={{ base: "none", md: "flex" }}>
            <Link href="/" passHref>
              <Button variant={router.pathname === "/" ? "solid" : "ghost"}>
                Home
              </Button>
            </Link>
            <Link href="/genre/action" passHref>
              <Button
                variant={
                  router.pathname.includes("/genre/action") ? "solid" : "ghost"
                }
              >
                Action
              </Button>
            </Link>
            <Link href="/genre/comedy" passHref>
              <Button
                variant={
                  router.pathname.includes("/genre/comedy") ? "solid" : "ghost"
                }
              >
                Comedy
              </Button>
            </Link>
          </HStack>
        </Flex>

        <HStack spacing={2}>
          <IconButton
            aria-label="Search"
            icon={<SearchIcon />}
            variant="ghost"
            onClick={() => router.push("/search")}
          />
          <IconButton
            aria-label="Toggle color mode"
            icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
            onClick={toggleColorMode}
            variant="ghost"
          />
          <Link href="/profile" passHref>
            <Button colorScheme="blue" size="sm">
              Profile
            </Button>
          </Link>
        </HStack>
      </Flex>
    </Box>
  );
};

export default Header;
