"use client";

import React, { useEffect, useState } from "react";
import { Stack, Text, useToast } from "@chakra-ui/react";
import { HiArrowLeftOnRectangle } from "react-icons/hi2";
import { useAuth } from "@/hooks";
import { ValidationError } from "@/services/api";
import BaseModal from "@/components/ui/organisms/BaseModal";
import FormInput from "@/components/ui/molecules/form/FormInput";
import { PrimaryCTA } from "@/components/ui/molecules/form/FormCTA";

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SignupModal: React.FC<SignupModalProps> = ({ isOpen, onClose }) => {
  const { register, isLoading, error } = useAuth();
  const [full_name, setFull_name] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [verifiedPassword, setVerifiedPassword] = useState("");
  const [fullNameError, setFullNameError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [verifiedPasswordError, setVerifiedPasswordError] = useState<
    string | null
  >(null);
  const [signupError, setSignupError] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    if (!isOpen) {
      setUsername("");
      setPassword("");
      setVerifiedPassword("");
      setFull_name("");
      setFullNameError(null);
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
      setFullNameError(null);
      return true;
    } else {
      setFullNameError("Full name cannot be empty");
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

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="Create Your Account">
      <form onSubmit={handleSubmit}>
        <Stack spacing={4}>
          <Text fontSize="sm" color="gray.500" mt={-4} mb={2}>
            Register to unlock special features, save your favorites, and
            enhance your experience.
          </Text>

          <FormInput
            id="full_name"
            label="Full Name"
            type="text"
            placeholder="Firstname Lastname"
            value={full_name}
            onChange={setFull_name}
            onBlur={validateFullname}
            error={fullNameError}
            isRequired
          />

          <FormInput
            id="email"
            label="Email"
            type="email"
            placeholder="Email"
            value={username}
            onChange={setUsername}
            onBlur={validateEmail}
            error={emailError}
            isRequired
          />

          <FormInput
            id="password"
            label="Password"
            type="password"
            placeholder="Password"
            value={password}
            onChange={setPassword}
            onBlur={validatePassword}
            error={passwordError}
            isRequired
          />

          <FormInput
            id="verified_password"
            label="Re-enter Password"
            type="password"
            placeholder="Password"
            value={verifiedPassword}
            onChange={setVerifiedPassword}
            onBlur={validateVerifiedPassword}
            error={verifiedPasswordError}
            isRequired
          />

          <PrimaryCTA
            type="submit"
            isLoading={isLoading}
            icon={HiArrowLeftOnRectangle}
          >
            Sign up
          </PrimaryCTA>

          {signupError && (
            <Text as="sub" color="red.500">
              {signupError}
            </Text>
          )}
        </Stack>
      </form>
    </BaseModal>
  );
};

export default SignupModal;
