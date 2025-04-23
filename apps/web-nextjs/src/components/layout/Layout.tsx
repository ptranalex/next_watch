import React, { ReactNode } from "react";
import { Box, Container, Flex } from "@chakra-ui/react";
import Header from "./Header";
import Sidebar from "./Sidebar";

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box minH="100vh" bg="gray.900" color="white">
      <Header />
      <Flex>
        <Sidebar />
        <Container maxW="container.xl" py={8} px={{ base: 4, md: 8 }}>
          <main>{children}</main>
        </Container>
      </Flex>
    </Box>
  );
};

export default Layout;
