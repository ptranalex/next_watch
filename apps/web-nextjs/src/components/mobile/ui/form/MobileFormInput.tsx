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
import { ViewIcon, ViewOffIcon, CloseIcon } from "@chakra-ui/icons";
import React, { useState } from "react";
import { HiXCircle } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";

const logger = createLogger("MobileFormInput");

interface MobileFormInputProps {
  id: string;
  label: string;
  type?: "text" | "email" | "password" | "tel" | "number";
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  error?: string | null;
  isRequired?: boolean;
  onKeyDown?: (event: React.KeyboardEvent) => void;
  showClearButton?: boolean;
  autoComplete?: string;
}

/**
 * Mobile-optimized form input component
 * Features larger touch targets, clear button, and better spacing
 */
const MobileFormInput: React.FC<MobileFormInputProps> = ({
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
  showClearButton = true,
  autoComplete,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";
  const errorColor = useColorModeValue("red.500", "red.300");
  const placeholderColor = useColorModeValue("gray.400", "gray.500");
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.300", "gray.600");

  const handleClear = () => {
    onChange("");
    // Provide haptic feedback
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(20);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }
  };

  return (
    <FormControl id={id} isRequired={isRequired} mb={4}>
      <FormLabel mb={2} fontWeight="medium">
        {label}
      </FormLabel>
      <Box position="relative">
        <InputGroup size="lg">
          <Input
            height="56px"
            fontSize="md"
            placeholder={placeholder}
            type={isPassword && showPassword ? "text" : type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onBlur={onBlur}
            onKeyDown={onKeyDown}
            bg={bgColor}
            borderWidth="1px"
            borderColor={error ? errorColor : borderColor}
            borderRadius="md"
            px={4}
            _placeholder={{ color: placeholderColor }}
            _focus={{
              borderColor: "blue.400",
              boxShadow: "0 0 0 1px var(--chakra-colors-blue-400)",
            }}
            autoComplete={autoComplete}
          />

          {value && showClearButton && !isPassword && (
            <InputRightElement h="56px" w="56px">
              <Button
                variant="ghost"
                onClick={handleClear}
                h="32px"
                w="32px"
                minW="32px"
                p={0}
                borderRadius="full"
              >
                <Icon as={CloseIcon} boxSize={5} />
              </Button>
            </InputRightElement>
          )}

          {isPassword && (
            <InputRightElement h="56px" w="56px">
              <Button
                variant="ghost"
                onClick={() => setShowPassword(!showPassword)}
                h="32px"
                w="32px"
                minW="32px"
                p={0}
                borderRadius="full"
              >
                {showPassword ? (
                  <ViewOffIcon boxSize={4} />
                ) : (
                  <ViewIcon boxSize={4} />
                )}
              </Button>
            </InputRightElement>
          )}
        </InputGroup>

        <Box minH="24px" mt="8px">
          {error && (
            <Flex alignItems="center">
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

export default MobileFormInput;
