import {
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Button,
  Text,
  Box,
  Flex,
  Icon,
} from "@chakra-ui/react";
import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import React, { useState } from "react";
import { HiXCircle } from "react-icons/hi2";
import type { BaseFormInputProps, ChangeHandler } from "../types";

/**
 * FormInput Props
 *
 * Extends the shared BaseFormInputProps with specific form input functionality
 */
interface FormInputProps extends Omit<BaseFormInputProps, "onChange"> {
  id: string;
  label: string;
  type?: "text" | "email" | "password";
  placeholder?: string;
  value: string;
  onChange: ChangeHandler<string>;
  onBlur?: () => void;
  error?: string | null;
  isRequired?: boolean;
  helpText?: string;
  size?: "sm" | "md" | "lg";
  onKeyDown?: (event: React.KeyboardEvent) => void;
}

/**
 * FormInput - A comprehensive form input component with validation
 *
 * @param id - Unique identifier for the input
 * @param label - Input label text
 * @param type - Input type (text, email, password)
 * @param placeholder - Placeholder text
 * @param value - Current input value
 * @param onChange - Value change handler using shared ChangeHandler type
 * @param onBlur - Blur event handler
 * @param error - Error message from shared ErrorStateProps
 * @param isRequired - Whether the field is required
 * @param helpText - Optional help text
 * @param size - Size variant from ComponentSize
 * @param onKeyDown - Keyboard event handler
 */
const FormInput: React.FC<FormInputProps> = ({
  id,
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  onBlur,
  error,
  isRequired = false,
  helpText,
  size = "md",
  onKeyDown,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";

  return (
    <FormControl id={id} isRequired={isRequired}>
      <FormLabel>{label}</FormLabel>
      <Box position="relative">
        <InputGroup size={size}>
          <Input
            placeholder={placeholder}
            type={isPassword && showPassword ? "text" : type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onBlur={onBlur}
            onKeyDown={onKeyDown}
            size={size}
          />
          {isPassword && (
            <InputRightElement h={"full"}>
              <Button
                variant={"ghost"}
                onClick={() => setShowPassword(!showPassword)}
                _hover={{ bg: "transparent" }}
                size="sm"
              >
                {showPassword ? <ViewOffIcon /> : <ViewIcon />}
              </Button>
            </InputRightElement>
          )}
        </InputGroup>
        <Box h="18px" mt="6px">
          {error && (
            <Flex alignItems="center" h="100%">
              <Icon as={HiXCircle} color="feedback.error" mr={1} boxSize={4} />
              <Text fontSize="sm" color="feedback.error" lineHeight="1.2">
                {error}
              </Text>
            </Flex>
          )}
          {helpText && !error && (
            <Text fontSize="sm" color="text.secondary" lineHeight="1.2">
              {helpText}
            </Text>
          )}
        </Box>
      </Box>
    </FormControl>
  );
};

export default FormInput;
