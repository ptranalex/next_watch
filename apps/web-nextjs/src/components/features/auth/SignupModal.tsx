"use client";

import React, { useEffect, useState } from "react";
import { Stack, Text, useToast } from "@chakra-ui/react";
import { HiArrowLeftOnRectangle } from "react-icons/hi2";
import { useAuth } from "@/services/hooks";
import { ValidationError } from "@/services/api";
import BaseModal from "@/components/ui/organisms/BaseModal";
import FormInput from "@/components/ui/molecules/form/FormInput";
import { PrimaryCTA } from "@/components/ui/molecules/form/FormCTA";
import type { SignupModalProps, AuthFormValidation } from "./types";

const SignupModal: React.FC<SignupModalProps> = ({
  isOpen,
  onClose,
  requireEmailVerification = false,
  allowLogin = true,
  onSuccess,
}) => {
  const { register, isLoading, error } = useAuth();
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [validation, setValidation] = useState<AuthFormValidation>({});
  const toast = useToast();

  useEffect(() => {
    if (!isOpen) {
      setUsername("");
      setPassword("");
      setConfirmPassword("");
      setFullName("");
      setValidation({});
    }
  }, [isOpen]);

  const validatePassword = (password: string) => {
    const re = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    if (re.test(password)) {
      setValidation((prev) => ({ ...prev, password: undefined }));
      return true;
    } else {
      setValidation((prev) => ({
        ...prev,
        password:
          "Password should be at least 8 characters long, contain at least one number, one lowercase and one uppercase letter",
      }));
      return false;
    }
  };

  const validateConfirmPassword = (confirmPass: string) => {
    if (password === confirmPass) {
      setValidation((prev) => ({ ...prev, confirmPassword: undefined }));
      return true;
    } else {
      setValidation((prev) => ({
        ...prev,
        confirmPassword:
          "Re-entered password does not match the first password",
      }));
      return false;
    }
  };

  const validateFullName = (name: string) => {
    if (name.trim().length > 0) {
      setValidation((prev) => ({ ...prev, fullName: undefined }));
      return true;
    } else {
      setValidation((prev) => ({
        ...prev,
        fullName: "Full name cannot be empty",
      }));
      return false;
    }
  };

  const validateEmail = (email: string) => {
    const re = /^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (re.test(String(email).toLowerCase())) {
      setValidation((prev) => ({ ...prev, email: undefined }));
      return true;
    } else {
      setValidation((prev) => ({ ...prev, email: "Invalid email address" }));
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear general error
    setValidation((prev) => ({ ...prev, general: undefined }));

    // Validate all fields
    const isEmailValid = validateEmail(username);
    const isPasswordValid = validatePassword(password);
    const isConfirmPasswordValid = validateConfirmPassword(confirmPassword);
    const isFullNameValid = validateFullName(fullName);

    if (
      !isEmailValid ||
      !isPasswordValid ||
      !isConfirmPasswordValid ||
      !isFullNameValid
    ) {
      return;
    }

    try {
      const success = await register({
        email: username,
        password: password,
        password_confirm: confirmPassword,
        username: fullName || undefined,
      });

      if (success) {
        onClose();

        const successMessage = requireEmailVerification
          ? "Account created! Please check your email to verify your account."
          : "Your account has been created successfully!";

        toast({
          title: "Account created!",
          description: successMessage,
          status: "success",
          duration: 5000,
          isClosable: true,
        });

        onSuccess?.();
      } else if (error) {
        setValidation((prev) => ({ ...prev, general: error }));
      }
    } catch (err: unknown) {
      let errorMessage = "An unexpected error occurred";

      // Handle different error types with proper type guards
      if (err instanceof ValidationError) {
        errorMessage = err.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === "object" && err !== null && "message" in err) {
        errorMessage = String(err.message);
      }

      setValidation((prev) => ({ ...prev, general: errorMessage }));
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !isLoading) {
      handleSubmit(event as React.FormEvent);
    }
  };

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="Create Your Account">
      <form onSubmit={handleSubmit}>
        <Stack spacing={4}>
          <Text fontSize="sm" color="text.secondary" mt={-4} mb={2}>
            Register to unlock special features, save your favorites, and
            enhance your experience.
          </Text>

          <FormInput
            id="full_name"
            label="Full Name"
            type="text"
            placeholder="Firstname Lastname"
            value={fullName}
            onChange={setFullName}
            onBlur={() => validateFullName(fullName)}
            onKeyDown={handleKeyDown}
            error={validation.fullName}
            isRequired
          />

          <FormInput
            id="email"
            label="Email"
            type="email"
            placeholder="Email"
            value={username}
            onChange={setUsername}
            onBlur={() => validateEmail(username)}
            onKeyDown={handleKeyDown}
            error={validation.email}
            isRequired
          />

          <FormInput
            id="password"
            label="Password"
            type="password"
            placeholder="Password"
            value={password}
            onChange={setPassword}
            onBlur={() => validatePassword(password)}
            onKeyDown={handleKeyDown}
            error={validation.password}
            isRequired
          />

          <FormInput
            id="confirm_password"
            label="Re-enter Password"
            type="password"
            placeholder="Password"
            value={confirmPassword}
            onChange={setConfirmPassword}
            onBlur={() => validateConfirmPassword(confirmPassword)}
            onKeyDown={handleKeyDown}
            error={validation.confirmPassword}
            isRequired
          />

          <PrimaryCTA
            type="submit"
            isLoading={isLoading}
            icon={HiArrowLeftOnRectangle}
            isDisabled={
              !fullName ||
              !username ||
              !password ||
              !confirmPassword ||
              isLoading
            }
          >
            Create Account
          </PrimaryCTA>

          {validation.general && (
            <Text as="sub" color="feedback.error">
              {validation.general}
            </Text>
          )}

          {allowLogin && (
            <Text fontSize="sm" color="text.secondary" textAlign="center">
              Already have an account?{" "}
              <Text as="span" color="colors.primary" cursor="pointer">
                Sign in here
              </Text>
            </Text>
          )}
        </Stack>
      </form>
    </BaseModal>
  );
};

export default SignupModal;
