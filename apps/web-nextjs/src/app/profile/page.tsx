"use client";

import { useState } from "react";
import {
  Avatar,
  Box,
  Button,
  Center,
  Grid,
  GridItem,
  Show,
  Stack,
  Text,
  useToast,
} from "@chakra-ui/react";
import { HiArrowRightOnRectangle, HiKey } from "react-icons/hi2";
import { useRouter } from "next/navigation";
import LeftNavBar from "@/src/components/layout/LeftNavBar";
import { useAuth } from "@/src/context/AuthContext";
import SetPasswordModal from "@/src/components/auth/SetPasswordModal";

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const router = useRouter();
  const toast = useToast();
  const [isSetPasswordModalOpen, setIsSetPasswordModalOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/");
    toast({
      title: "Signed out",
      description: "You have been signed out",
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };

  const handleSetPassword = () => {
    setIsSetPasswordModalOpen(true);
  };

  const handleCloseSetPasswordModal = () => {
    setIsSetPasswordModalOpen(false);
  };

  return (
    <Box px={{ base: 0, xl: 32 }} maxW="1600px" mx="auto" py={8}>
      <Grid
        templateAreas={{
          base: `"main"`,
          lg: `"aside main"`,
        }}
        templateColumns={{ base: "1fr", lg: "200px 1fr" }}
      >
        <Show above="lg">
          <GridItem area="aside" paddingX={5}>
            <LeftNavBar />
          </GridItem>
        </Show>
        <GridItem area="main">
          <Box paddingLeft={0}>
            {user ? (
              <>
                <Center>
                  <Stack width={{ base: "100%", md: "400px" }}>
                    <Box paddingBottom={20}>
                      <Center>
                        <Stack spacing={4} align="center">
                          <Avatar src={user.name} name={user.name} size="xl" />
                          <Text fontSize="xl" fontWeight="bold">
                            {user.name}
                          </Text>
                          <Text>{user.email}</Text>
                        </Stack>
                      </Center>
                    </Box>
                    <Button
                      leftIcon={<HiKey />}
                      onClick={handleSetPassword}
                      justifyContent="left"
                      mb={2}
                    >
                      Set Password
                    </Button>
                    <Button
                      leftIcon={<HiArrowRightOnRectangle />}
                      onClick={handleLogout}
                      justifyContent="left"
                      colorScheme="red"
                      variant="outline"
                    >
                      Sign out
                    </Button>
                  </Stack>
                </Center>
              </>
            ) : (
              <Center h="50vh">
                <Stack spacing={4} align="center">
                  <Text fontSize="xl">You are not signed in</Text>
                  <Button colorScheme="blue" onClick={() => router.push("/")}>
                    Go to Home
                  </Button>
                </Stack>
              </Center>
            )}
          </Box>
        </GridItem>
      </Grid>
      <SetPasswordModal
        isOpen={isSetPasswordModalOpen}
        onClose={handleCloseSetPasswordModal}
      />
    </Box>
  );
};

export default ProfilePage;
