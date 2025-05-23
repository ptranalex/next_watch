import React, { useEffect, useState } from "react";
import {
  HiArrowLeftOnRectangle,
  HiLifebuoy,
  HiMiniPlus,
} from "react-icons/hi2";
import { Stack } from "@chakra-ui/react";
import { useAuth } from "@/hooks";
import { useToast } from "@chakra-ui/react";
import SignupModal from "./SignupModal";
import BaseModal from "@/components/ui/organisms/BaseModal";
import FormInput from "@/components/ui/molecules/form/FormInput";
import {
  PrimaryCTA,
  SecondaryCTA,
  TertiaryCTA,
  Divider,
} from "@/components/ui/molecules/form/FormCTA";
import type { LoginModalProps, AuthFormValidation } from "./types";

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const { login, error, clearError } = useAuth();
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [validation, setValidation] = useState<AuthFormValidation>({});
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (isOpen) {
      clearError();
    }

    if (!isOpen) {
      setUsername("");
      setPassword("");
      setValidation({});
    }
  }, [isOpen, clearError]);

  const validatePassword = (password: string) => {
    if (password.trim()) {
      setValidation((prev) => ({ ...prev, password: undefined }));
      return true;
    } else {
      setValidation((prev) => ({ ...prev, password: "Password is required" }));
      return false;
    }
  };

  const validateEmail = (email: string) => {
    const re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (re.test(String(email).toLowerCase())) {
      setValidation((prev) => ({ ...prev, email: undefined }));
      return true;
    } else {
      setValidation((prev) => ({ ...prev, email: "Invalid email address" }));
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
      setValidation((prev) => ({ ...prev, general: error }));
    }
  };

  const onForgotPassword = () => {
    // Handle forgot password
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      onSignInPassword();
    }
  };

  const onSignup = () => {
    onClose();
    setIsSignupModalOpen(true);
  };

  const handleCloseSignupModal = () => {
    setIsSignupModalOpen(false);
  };

  return (
    <>
      <BaseModal isOpen={isOpen} onClose={onClose} title="Sign In">
        <Stack spacing={4}>
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
            error={validation.password || validation.general}
          />

          <PrimaryCTA onClick={onSignInPassword} icon={HiArrowLeftOnRectangle}>
            Sign in with Password
          </PrimaryCTA>

          <TertiaryCTA onClick={onForgotPassword} icon={HiLifebuoy}>
            Forgot Password
          </TertiaryCTA>

          <Divider text="or" />

          <SecondaryCTA onClick={onSignup} icon={HiMiniPlus}>
            Sign up with Email
          </SecondaryCTA>
        </Stack>
      </BaseModal>

      <SignupModal
        isOpen={isSignupModalOpen}
        onClose={handleCloseSignupModal}
      />
    </>
  );
};

export default LoginModal;
