import {
  Avatar,
  Box,
  HStack,
  Heading,
  IconButton,
  Image,
  useColorMode,
} from "@chakra-ui/react";
import { useState } from "react";
import { HiArrowLeftOnRectangle } from "react-icons/hi2";
import { useRouter } from "next/navigation";
import logoLight from "../../assets/logo-light.jpeg";
import logoDark from "../../assets/logo.jpeg";
import { useAuth, useDevice } from "@/hooks";
import useMovieQueryStore from "../../store/movieQuery";
import ColorModeSwitch from "./ColorModeSwitch";
import LoginModal from "../auth/LoginModal";
import MobileNavMenu from "./MobileNavMenu";
import SearchInput from "./SearchInput";

const NavBar: React.FC = () => {
  const { colorMode } = useColorMode();
  const logo = colorMode === "light" ? logoLight : logoDark;
  const router = useRouter();
  const { isMobile } = useDevice();

  const resetFilters = useMovieQueryStore((state) => state.resetFilters);
  const { isAuthenticated, user } = useAuth();
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  const handleLogoClick = () => {
    resetFilters();
    router.push("/");
  };

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSearchFocus = () => {
    setIsSearchFocused(true);
  };

  const handleSearchBlur = () => {
    setIsSearchFocused(false);
  };

  // Element visibility based on combined conditions
  const showMobileNav = !isSearchFocused && isMobile;
  const showLogo = !isSearchFocused;
  const showHeading = !isSearchFocused && !isMobile;
  const showUserIcon = !isSearchFocused;

  return (
    <>
      <Box
        position="sticky"
        top="0"
        zIndex="sticky"
        backdropFilter="blur(10px)"
        backgroundColor="rgba(255, 255, 255, 0.8)" // Adjust color and opacity as needed
        _dark={{ backgroundColor: "rgba(26, 32, 44, 0.8)" }} // Adjust for dark mode
        width="100%"
      >
        <HStack padding="20px" spacing="10px">
          {showMobileNav && <MobileNavMenu />}
          {showLogo && (
            <Image
              src={logo.src}
              alt="Box Office Logo"
              boxSize="40px"
              objectFit="cover"
              borderRadius="full"
              margin="0"
              padding="0"
              onClick={handleLogoClick}
              cursor="pointer"
            />
          )}
          {showHeading && (
            <Heading size="sm" marginRight={10} whiteSpace="nowrap">
              Box Office
            </Heading>
          )}
          <SearchInput onFocus={handleSearchFocus} onBlur={handleSearchBlur} />
          {isAuthenticated && user && showUserIcon ? (
            <Box
              cursor="pointer"
              onClick={() => router.push("/profile")}
              ml={{ base: 0, md: 2 }}
            >
              <Avatar size="sm" name={user.username || user.email} />
            </Box>
          ) : !isSearchFocused ? (
            <IconButton
              aria-label="Login"
              icon={<HiArrowLeftOnRectangle />}
              onClick={handleOpenModal}
              fontSize={25}
            />
          ) : (
            showUserIcon && (
              <Box ml={{ base: 0, md: 2 }}>
                <Avatar size="sm" />
              </Box>
            )
          )}
          {!isSearchFocused && <ColorModeSwitch />}
        </HStack>
      </Box>
      <LoginModal isOpen={isModalOpen} onClose={handleCloseModal} />
    </>
  );
};

export default NavBar;
