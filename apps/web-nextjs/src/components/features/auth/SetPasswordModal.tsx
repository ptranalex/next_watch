import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import {
  Button,
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
} from "@chakra-ui/react";
import React, { useState } from "react";
import { HiKey } from "react-icons/hi2";
import { APIClient } from "@/services/api";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const apiClient = new APIClient("/users/set_password");

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const textColor = useColorModeValue("text.primary", "text.primary");
  const modalBgColor = useColorModeValue("bg.secondary", "bg.tertiary");
  const [password, setPassword] = useState("");
  const [verifiedPassword, setVerifiedPassword] = useState("");
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [verifiedPasswordError, setVerifiedPasswordError] = useState<
    string | null
  >(null);
  const [showPassword, setShowPassword] = useState(false);
  const handleShowPassword = () => setShowPassword(!showPassword);

  const validatePassword = () => {
    // Password should be at least 8 characters long, contain at least one number, one lowercase and one uppercase letter
    const re = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    if (re.test(password)) {
      setPasswordError(null);
    } else {
      setPasswordError(
        "Password should be at least 8 characters long, contain at least one number, one lowercase and one uppercase letter"
      );
    }
  };

  const validateVerifiedPassword = () => {
    // Verify if the password is the same as the first password
    if (password === verifiedPassword) {
      setVerifiedPasswordError(null);
    } else {
      setVerifiedPasswordError(
        "Re-entered password does not match the first password"
      );
    }
  };

  const onPasswordSubmit = () => {
    validatePassword();
    validateVerifiedPassword();

    if (passwordError || verifiedPasswordError) {
      return;
    }

    apiClient
      .create({ password })
      .then(() => {})
      .catch(() => {
        console.error("Error setting password");
      });
  };

  return (
    <Modal isCentered isOpen={isOpen} onClose={onClose}>
      <ModalOverlay
        bg="blackAlpha.300"
        backdropFilter="auto"
        backdropBlur="4px"
      />
      <ModalContent bg={modalBgColor} color={textColor}>
        <ModalHeader>
          <Text fontSize="2xl">Set Password</Text>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody padding={6}>
          <Stack spacing={4}>
            <FormControl id="password" isRequired>
              <FormLabel>Password</FormLabel>
              <InputGroup>
                <Input
                  placeholder="Password"
                  type={showPassword ? "text" : "password"}
                  onChange={(e) => setPassword(e.target.value)}
                  onBlur={validatePassword}
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
                <Text as="sub" color="feedback.error">
                  {passwordError}
                </Text>
              )}
            </FormControl>

            <FormControl id="verified_password" isRequired>
              <FormLabel>Re-enter Password</FormLabel>
              <InputGroup>
                <Input
                  placeholder="Password"
                  type={showPassword ? "text" : "password"}
                  onChange={(e) => setVerifiedPassword(e.target.value)}
                  onBlur={validateVerifiedPassword}
                />
              </InputGroup>
              {verifiedPasswordError && (
                <Text as="sub" color="feedback.error">
                  {verifiedPasswordError}
                </Text>
              )}
            </FormControl>

            <Button
              width="100%"
              bg="colors.primary"
              color="text.inverse"
              _hover={{ bg: "colors.secondary" }}
              leftIcon={<HiKey fontSize="1.5rem" />}
              justifyContent="left"
              onClick={onPasswordSubmit}
            >
              Submit Password
            </Button>
          </Stack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default LoginModal;
