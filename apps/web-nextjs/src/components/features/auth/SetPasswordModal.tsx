import React, { useState, useEffect } from "react";
import { Stack, useToast } from "@chakra-ui/react";
import { HiKey } from "react-icons/hi2";
import { APIClient } from "@/services/api";
import BaseModal from "@/components/ui/organisms/BaseModal";
import FormInput from "@/components/ui/molecules/form/FormInput";
import { PrimaryCTA } from "@/components/ui/molecules/form/FormCTA";
import type { SetPasswordModalProps, AuthFormValidation } from "./types";

const apiClient = new APIClient("/users/set_password");

const SetPasswordModal: React.FC<SetPasswordModalProps> = ({
  isOpen,
  onClose,
  token,
  email,
  onSuccess,
}) => {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [validation, setValidation] = useState<AuthFormValidation>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (!isOpen) {
      setPassword("");
      setConfirmPassword("");
      setValidation({});
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const validatePassword = (password: string) => {
    // Password should be at least 8 characters long, contain at least one number, one lowercase and one uppercase letter
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

  const onPasswordSubmit = async () => {
    if (
      !validatePassword(password) ||
      !validateConfirmPassword(confirmPassword)
    ) {
      return;
    }

    setIsSubmitting(true);
    setValidation((prev) => ({ ...prev, general: undefined }));

    try {
      const payload: Record<string, string> = { password };

      // Include token and email if provided
      if (token) payload.token = token;
      if (email) payload.email = email;

      await apiClient.create(payload);

      toast({
        title: "Password set successfully.",
        description: "Your password has been updated.",
        status: "success",
        duration: 4000,
        isClosable: true,
      });

      onClose();
      onSuccess?.();
    } catch (error) {
      console.error("Error setting password:", error);
      setValidation((prev) => ({
        ...prev,
        general: "Failed to set password. Please try again.",
      }));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !isSubmitting) {
      onPasswordSubmit();
    }
  };

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="Set Password">
      <Stack spacing={4}>
        <FormInput
          id="password"
          label="Password"
          type="password"
          placeholder="Enter your password"
          value={password}
          onChange={setPassword}
          onBlur={() => validatePassword(password)}
          onKeyDown={handleKeyDown}
          error={validation.password}
          isRequired
        />

        <FormInput
          id="confirmPassword"
          label="Re-enter Password"
          type="password"
          placeholder="Confirm your password"
          value={confirmPassword}
          onChange={setConfirmPassword}
          onBlur={() => validateConfirmPassword(confirmPassword)}
          onKeyDown={handleKeyDown}
          error={validation.confirmPassword}
          isRequired
        />

        {validation.general && (
          <div style={{ color: "var(--chakra-colors-feedback-error)" }}>
            {validation.general}
          </div>
        )}

        <PrimaryCTA
          onClick={onPasswordSubmit}
          icon={HiKey}
          isLoading={isSubmitting}
          isDisabled={!password || !confirmPassword || isSubmitting}
        >
          Set Password
        </PrimaryCTA>
      </Stack>
    </BaseModal>
  );
};

export default SetPasswordModal;
