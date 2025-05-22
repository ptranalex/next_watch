import {
  Box,
  Flex,
  FormControl,
  FormLabel,
  Icon,
  Input,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import React, { useEffect, useRef, useState } from "react";
import { HiCheck, HiXCircle } from "react-icons/hi2";

interface FileInputProps {
  id: string;
  label: string;
  accept?: string;
  onChange: (file: File | null) => void;
  error?: string | null;
  success?: string | null;
  isRequired?: boolean;
  validateFile?: (file: File) => string | null;
  placeholder?: string;
}

const FileInput: React.FC<FileInputProps> = ({
  id,
  label,
  accept = "*/*",
  onChange,
  error,
  success,
  isRequired = false,
  validateFile,
  placeholder = "Choose file...",
}) => {
  const [fileName, setFileName] = useState<string>("");
  const [internalError, setInternalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const errorColor = useColorModeValue("red.500", "red.300");
  const successColor = useColorModeValue("green.500", "green.300");

  // Display the passed error or the internal validation error
  const displayError = error || internalError;

  useEffect(() => {
    // Reset internal error when error prop changes
    if (error === null) {
      setInternalError(null);
    }
  }, [error]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;

    if (!file) {
      setFileName("");
      setInternalError("No file selected");
      onChange(null);
      return;
    }

    setFileName(file.name);

    // Validate the file if a validation function is provided
    if (validateFile) {
      const validationError = validateFile(file);
      if (validationError) {
        setInternalError(validationError);
        onChange(null);
        return;
      }
    }

    setInternalError(null);
    onChange(file);
  };

  const clearFile = () => {
    if (inputRef.current) {
      inputRef.current.value = "";
    }
    setFileName("");
    setInternalError(null);
    onChange(null);
  };

  return (
    <FormControl id={id} isRequired={isRequired}>
      <FormLabel>{label}</FormLabel>
      <Box position="relative">
        <Input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          p={1}
          height="auto"
          placeholder={placeholder}
        />

        {fileName && !displayError && (
          <Flex alignItems="center" mt={1}>
            <Icon as={HiCheck} color={successColor} mr={1} />
            <Text fontSize="sm" color={successColor}>
              {success || `${fileName} ready to upload`}
            </Text>
          </Flex>
        )}

        {displayError && (
          <Flex alignItems="center" mt={1}>
            <Icon as={HiXCircle} color={errorColor} mr={1} />
            <Text fontSize="sm" color={errorColor}>
              {displayError}
            </Text>
          </Flex>
        )}
      </Box>
    </FormControl>
  );
};

export default FileInput;
