import {
  Box,
  Flex,
  FormControl,
  FormLabel,
  Icon,
  Text,
  useColorModeValue,
  Button,
} from "@chakra-ui/react";
import React, { useRef, useState } from "react";
import {
  HiCheck,
  HiXCircle,
  HiPhoto,
  HiDocumentText,
  HiTrash,
} from "react-icons/hi2";
import { createLogger } from "@/utils/logging";

const logger = createLogger("MobileFileInput");

interface MobileFileInputProps {
  id: string;
  label: string;
  accept?: string;
  onChange: (file: File | null) => void;
  error?: string | null;
  success?: string | null;
  isRequired?: boolean;
  validateFile?: (file: File) => string | null;
  placeholder?: string;
  captureMode?: "user" | "environment" | ""; // For camera access
}

/**
 * Mobile-optimized file input component
 * Features:
 * - Large touch targets
 * - Camera capture support
 * - Native file picker integration
 * - Haptic feedback
 * - Visual feedback during selection
 */
const MobileFileInput: React.FC<MobileFileInputProps> = ({
  id,
  label,
  accept = "*/*",
  onChange,
  error,
  success,
  isRequired = false,
  validateFile,
  placeholder = "Choose file...",
  captureMode = "", // Empty string means no camera capture
}) => {
  const [fileName, setFileName] = useState<string>("");
  const [internalError, setInternalError] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<string>("");
  const inputRef = useRef<HTMLInputElement>(null);

  const errorColor = useColorModeValue("red.500", "red.300");
  const successColor = useColorModeValue("green.500", "green.300");
  const bgColor = useColorModeValue("gray.50", "gray.700");
  const borderColor = useColorModeValue("gray.200", "gray.600");
  const textColor = useColorModeValue("gray.700", "gray.200");
  const hoverBgColor = useColorModeValue("gray.100", "gray.600");

  // Display the passed error or the internal validation error
  const displayError = error || internalError;

  // Helper for haptic feedback
  const triggerHaptics = (pattern: number | number[] = 50) => {
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(pattern);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }
  };

  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " bytes";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;

    if (!file) {
      setFileName("");
      setFileSize("");
      setInternalError("No file selected");
      onChange(null);
      triggerHaptics([30, 50, 30]); // Error pattern
      return;
    }

    setFileName(file.name);
    setFileSize(formatFileSize(file.size));

    // Validate the file if a validation function is provided
    if (validateFile) {
      const validationError = validateFile(file);
      if (validationError) {
        setInternalError(validationError);
        onChange(null);
        triggerHaptics([30, 50, 30]); // Error pattern
        return;
      }
    }

    setInternalError(null);
    onChange(file);
    triggerHaptics(50); // Success pattern
  };

  const clearFile = () => {
    if (inputRef.current) {
      inputRef.current.value = "";
    }
    setFileName("");
    setFileSize("");
    setInternalError(null);
    onChange(null);
    triggerHaptics(20);
  };

  const triggerFilePicker = () => {
    inputRef.current?.click();
  };

  // Determine which icon to show based on file type
  const getFileIcon = () => {
    if (!fileName) return null;

    const extension = fileName.split(".").pop()?.toLowerCase() || "";

    if (["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(extension)) {
      return HiPhoto;
    }

    return HiDocumentText;
  };

  const FileIcon = getFileIcon();

  return (
    <FormControl id={id} isRequired={isRequired} mb={4}>
      <FormLabel mb={2} fontWeight="medium">
        {label}
      </FormLabel>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        style={{ display: "none" }}
        capture={captureMode || undefined}
      />

      {!fileName ? (
        // File selection button
        <Button
          onClick={triggerFilePicker}
          width="100%"
          height="56px"
          bg={bgColor}
          border="1px dashed"
          borderColor={borderColor}
          borderRadius="md"
          justifyContent="center"
          _hover={{ bg: hoverBgColor }}
        >
          {placeholder}
        </Button>
      ) : (
        // File selected view
        <Box
          width="100%"
          borderWidth="1px"
          borderColor={displayError ? errorColor : borderColor}
          borderRadius="md"
          bg={bgColor}
          p={3}
        >
          <Flex justify="space-between" align="center">
            <Flex align="center" flex={1} mr={2}>
              {FileIcon && (
                <Icon as={FileIcon} boxSize={5} color={textColor} mr={3} />
              )}
              <Box>
                <Text
                  fontSize="sm"
                  fontWeight="medium"
                  noOfLines={1}
                  maxWidth="200px"
                >
                  {fileName}
                </Text>
                {fileSize && (
                  <Text fontSize="xs" color="gray.500">
                    {fileSize}
                  </Text>
                )}
              </Box>
            </Flex>

            <Button
              variant="ghost"
              colorScheme="red"
              size="sm"
              p={1}
              onClick={clearFile}
              aria-label="Remove file"
            >
              <Icon as={HiTrash} boxSize={5} />
            </Button>
          </Flex>
        </Box>
      )}

      <Box minH="24px" mt="8px">
        {fileName && !displayError && (
          <Flex alignItems="center">
            <Icon as={HiCheck} color={successColor} mr={1} boxSize={4} />
            <Text fontSize="sm" color={successColor}>
              {success || `File ready to upload`}
            </Text>
          </Flex>
        )}

        {displayError && (
          <Flex alignItems="center">
            <Icon as={HiXCircle} color={errorColor} mr={1} boxSize={4} />
            <Text fontSize="sm" color={errorColor}>
              {displayError}
            </Text>
          </Flex>
        )}
      </Box>
    </FormControl>
  );
};

export default MobileFileInput;
