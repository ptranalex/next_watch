"use client";

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
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Stack,
  Text,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import React, { useEffect, useState } from "react";
import { HiArrowLeftOnRectangle } from "react-icons/hi2";
import { useAuth } from "@/hooks";
import { ValidationError } from "@/services/api";

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SignupModal: React.FC<SignupModalProps> = ({ isOpen, onClose }) => {
  const textColor = useColorModeValue("black", "white");
  const modalBgColor = useColorModeValue("gray.100", "gray.800");
  const { register, isLoading, error } = useAuth();
  const [full_name, setFull_name] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [verifiedPassword, setVerifiedPassword] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [verifiedPasswordError, setVerifiedPasswordError] = useState<
    string | null
  >(null);
  const [signupError, setSignupError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (!isOpen) {
      setUsername("");
      setPassword("");
      setVerifiedPassword("");
      setFull_name("");
      setEmailError(null);
      setPasswordError(null);
      setVerifiedPasswordError(null);
      setSignupError(null);
    }
  }, [isOpen]);

  const validatePassword = () => {
    const re = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    if (re.test(password)) {
      setPasswordError(null);
      return true;
    } else {
      setPasswordError(
        "Password should be at least 8 characters long, contain at least one number, one lowercase and one uppercase letter"
      );
      return false;
    }
  };

  const validateVerifiedPassword = () => {
    if (password === verifiedPassword) {
      setVerifiedPasswordError(null);
      return true;
    } else {
      setVerifiedPasswordError(
        "Re-entered password does not match the first password"
      );
      return false;
    }
  };

  const validateFullname = () => {
    if (full_name.length > 0) {
      setEmailError(null);
      return true;
    } else {
      setEmailError("Full name cannot be empty");
      return false;
    }
  };

  const validateEmail = () => {
    const re = /^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (re.test(String(username).toLowerCase())) {
      setEmailError(null);
      return true;
    } else {
      setEmailError("Invalid email address");
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !validateEmail() ||
      !validatePassword() ||
      !validateVerifiedPassword() ||
      !validateFullname()
    ) {
      return;
    }

    if (password !== verifiedPassword) {
      setPasswordError("Passwords do not match");
      return;
    }

    try {
      const success = await register({
        email: username,
        password: password,
        password_confirm: verifiedPassword,
        username: full_name || undefined,
      });

      if (success) {
        onClose();
        toast({
          title: "Account created!",
          description: "Your account has been created successfully",
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      } else if (error) {
        setSignupError(error);
      }
    } catch (err) {
      if (err instanceof ValidationError) {
        setSignupError(err.message);
      } else {
        setSignupError("An unexpected error occurred");
      }
    }
  };

  const handleShowPassword = () => setShowPassword(!showPassword);

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent bg={modalBgColor} color={textColor}>
        <ModalHeader>
          <Text fontSize="2xl">Create Your Account</Text>
          <Text fontSize="sm" color="gray.500" mt={3} mb={0}>
            Register to unlock special features, save your favorites, and
            enhance your experience.
          </Text>
        </ModalHeader>
        <ModalCloseButton />
        <form onSubmit={handleSubmit}>
          <ModalBody padding={6}>
            <Stack spacing={4}>
              <FormControl id="full_name" isRequired>
                <FormLabel>Full Name</FormLabel>
                <Input
                  placeholder="Firstname Lastname"
                  type="text"
                  onChange={(e) => setFull_name(e.target.value)}
                  onBlur={validateFullname}
                  value={full_name}
                />
                {emailError && <Text as="sub">{emailError}</Text>}
              </FormControl>
              <FormControl id="email" isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  placeholder="Email"
                  type="email"
                  onChange={(e) => setUsername(e.target.value)}
                  onBlur={validateEmail}
                  value={username}
                />
                {emailError && <Text as="sub">{emailError}</Text>}
              </FormControl>

              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    placeholder="Password"
                    type={showPassword ? "text" : "password"}
                    onChange={(e) => setPassword(e.target.value)}
                    onBlur={validatePassword}
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
                {passwordError && <Text as="sub">{passwordError}</Text>}
              </FormControl>
              <FormControl id="verified_password" isRequired>
                <FormLabel>Re-enter Password</FormLabel>
                <InputGroup>
                  <Input
                    placeholder="Password"
                    type={showPassword ? "text" : "password"}
                    onChange={(e) => setVerifiedPassword(e.target.value)}
                    onBlur={validateVerifiedPassword}
                    value={verifiedPassword}
                  />
                </InputGroup>
                {verifiedPasswordError && (
                  <Text as="sub">{verifiedPasswordError}</Text>
                )}
              </FormControl>
              <Button
                width="100%"
                colorScheme="blue"
                leftIcon={<HiArrowLeftOnRectangle fontSize="1.5rem" />}
                justifyContent="left"
                type="submit"
                isLoading={isLoading}
              >
                Sign up
              </Button>
              {signupError && (
                <Text as="sub" color="red.500">
                  {signupError}
                </Text>
              )}
            </Stack>
          </ModalBody>

          <ModalFooter>
            <Button
              colorScheme="blue"
              mr={3}
              type="submit"
              isLoading={isLoading}
            >
              Sign up
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};

export default SignupModal;
