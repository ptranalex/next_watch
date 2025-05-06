import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import {
  Button,
  Center,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Stack,
  Text,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import React, { useEffect, useState } from "react";
import {
  HiArrowLeftOnRectangle,
  HiLifebuoy,
  HiMiniPlus,
} from "react-icons/hi2";
import SignupModal from "./SignupModal";
import { useAuth } from "@/hooks";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const textColor = useColorModeValue("black", "white");
  const modalBgColor = useColorModeValue("gray.100", "gray.800");
  const { login, error, clearError } = useAuth();
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const handleShowPassword = () => setShowPassword(!showPassword);
  const toast = useToast();

  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);

  const onSignup = () => {
    onClose();
    setIsSignupModalOpen(true);
  };

  const handleCloseSignupModal = () => {
    setIsSignupModalOpen(false);
  };

  useEffect(() => {
    if (isOpen) {
      clearError();
    }

    if (!isOpen) {
      setUsername("");
      setPassword("");
      setEmailError(null);
      setPasswordError(null);
    }
  }, [isOpen, clearError]);

  const validatePassword = (password: string) => {
    if (password.trim()) {
      setPasswordError(null);
      return true;
    } else {
      setPasswordError("Password is required");
      return false;
    }
  };

  const validateEmail = (email: string) => {
    const re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (re.test(String(email).toLowerCase())) {
      setEmailError(null);
      return true;
    } else {
      setEmailError("Invalid email address");
      return false;
    }
  };

  const onSignInPassword = async () => {
    if (!validateEmail(username) || !validatePassword(password)) {
      return;
    }

    const success = await login(username, password);
    if (success) {
      onClose();
      toast({
        title: "Signed in successfully.",
        description: "You have been signed in.",
        status: "success",
        duration: 4000,
        isClosable: true,
      });
    } else if (error) {
      setPasswordError(error);
    }
  };

  const onForgotPassword = () => {
    console.log("Forgot password");
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      onSignInPassword();
    }
  };

  return (
    <>
      <Modal isCentered isOpen={isOpen} onClose={onClose}>
        <ModalOverlay
          bg="blackAlpha.300"
          backdropFilter="auto"
          backdropBlur="4px"
        />
        <ModalContent bg={modalBgColor} color={textColor}>
          <ModalHeader>
            <Text fontSize="2xl">Sign In</Text>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody padding={6}>
            <Stack spacing={4}>
              <FormControl id="email">
                <FormLabel>Email</FormLabel>
                <Input
                  placeholder="Email"
                  type="email"
                  onChange={(e) => setUsername(e.target.value)}
                  onBlur={() => validateEmail(username)}
                  onKeyDown={handleKeyDown}
                  value={username}
                />
                {emailError && (
                  <Text as="sub" color="red.500">
                    {emailError}
                  </Text>
                )}
              </FormControl>

              <FormControl id="password">
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    placeholder="Password"
                    type={showPassword ? "text" : "password"}
                    onChange={(e) => setPassword(e.target.value)}
                    onBlur={() => validatePassword(password)}
                    onKeyDown={handleKeyDown}
                    value={password}
                  />
                  <InputRightElement h={"full"}>
                    <Button
                      variant={"ghost"}
                      onClick={handleShowPassword}
                      _hover={{ bg: "transparent" }}
                    >
                      {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                    </Button>
                  </InputRightElement>
                </InputGroup>
                {passwordError && (
                  <Text as="sub" color="red.500">
                    {passwordError}
                  </Text>
                )}
              </FormControl>

              <Button
                width="100%"
                colorScheme="blue"
                leftIcon={<HiArrowLeftOnRectangle fontSize="1.5rem" />}
                justifyContent="left"
                onClick={onSignInPassword}
              >
                Sign in with Password
              </Button>
              <Button
                variant="ghost"
                onClick={onForgotPassword}
                width="100%"
                leftIcon={<HiLifebuoy fontSize="1.5rem" />}
                justifyContent="left"
              >
                Forgot Password
              </Button>
              <Center width="100%">
                <Text>or</Text>
              </Center>

              <Button
                onClick={onSignup}
                colorScheme="teal"
                width="100%"
                leftIcon={<HiMiniPlus fontSize="1.5rem" />}
                justifyContent="left"
              >
                Sign up with Email
              </Button>
            </Stack>
          </ModalBody>
        </ModalContent>
      </Modal>
      <SignupModal
        isOpen={isSignupModalOpen}
        onClose={handleCloseSignupModal}
      />
    </>
  );
};

export default LoginModal;
