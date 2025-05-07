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
  useColorModeValue,
} from "@chakra-ui/react";
import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import React, { useState } from "react";
import { HiXCircle } from "react-icons/hi2";

interface FormInputProps {
  id: string;
  label: string;
  type?: "text" | "email" | "password";
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  error?: string | null;
  isRequired?: boolean;
  onKeyDown?: (event: React.KeyboardEvent) => void;
}

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
  onKeyDown,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";
  const errorColor = useColorModeValue("red.500", "red.300");

  return (
    <FormControl id={id} isRequired={isRequired}>
      <FormLabel>{label}</FormLabel>
      <Box position="relative">
        <InputGroup>
          <Input
            placeholder={placeholder}
            type={isPassword && showPassword ? "text" : type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onBlur={onBlur}
            onKeyDown={onKeyDown}
          />
          {isPassword && (
            <InputRightElement h={"full"}>
              <Button
                variant={"ghost"}
                onClick={() => setShowPassword(!showPassword)}
                _hover={{ bg: "transparent" }}
              >
                {showPassword ? <ViewOffIcon /> : <ViewIcon />}
              </Button>
            </InputRightElement>
          )}
        </InputGroup>
        <Box h="18px" mt="6px">
          {error && (
            <Flex alignItems="center" h="100%">
              <Icon as={HiXCircle} color={errorColor} mr={1} boxSize={4} />
              <Text fontSize="sm" color={errorColor} lineHeight="1.2">
                {error}
              </Text>
            </Flex>
          )}
        </Box>
      </Box>
    </FormControl>
  );
};

export default FormInput;
