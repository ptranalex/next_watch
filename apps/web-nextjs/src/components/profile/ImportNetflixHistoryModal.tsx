import React, { useRef, useState } from "react";
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Stack,
  Text,
  useColorModeValue,
  useToast,
  Box,
  Progress,
  Icon,
  Flex,
  ListItem,
  UnorderedList,
} from "@chakra-ui/react";
import {
  HiDocumentArrowUp,
  HiInformationCircle,
  HiExclamationTriangle,
} from "react-icons/hi2";
import userAPI from "@/services/api/user/user-api";
import { NetflixImportResult } from "@/services/api/user/types";

interface ImportNetflixHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ImportNetflixHistoryModal: React.FC<ImportNetflixHistoryModalProps> = ({
  isOpen,
  onClose,
}) => {
  const textColor = useColorModeValue("black", "white");
  const modalBgColor = useColorModeValue("gray.100", "gray.800");
  const toast = useToast();

  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileName, setFileName] = useState("");
  const [fileError, setFileError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<NetflixImportResult | null>(
    null
  );

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) {
      setFileName("");
      setFileError("No file selected");
      return;
    }

    // Check file extension
    if (!file.name.endsWith(".csv")) {
      setFileName(file.name);
      setFileError("Please upload a CSV file");
      return;
    }

    setFileName(file.name);
    setFileError(null);
    setImportResult(null);
  };

  const handleUpload = async () => {
    if (!fileName || fileError) {
      toast({
        title: "Error",
        description: "Please select a valid CSV file",
        status: "error",
        duration: 4000,
        isClosable: true,
      });
      return;
    }

    if (!fileInputRef.current?.files?.[0]) {
      return;
    }

    const file = fileInputRef.current.files[0];
    setIsUploading(true);
    setUploadProgress(10);

    try {
      // Use the actual API service
      const result = await userAPI.importNetflixHistory(file);
      setUploadProgress(100);
      setImportResult(result);

      toast({
        title: "Import successful",
        description: `Successfully imported ${result.imported} items from Netflix history`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "Import failed",
        description:
          error instanceof Error
            ? error.message
            : "Failed to import Netflix history",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const clearFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    setFileName("");
    setFileError(null);
    setImportResult(null);
  };

  return (
    <Modal isCentered isOpen={isOpen} onClose={onClose}>
      <ModalOverlay
        bg="blackAlpha.300"
        backdropFilter="auto"
        backdropBlur="4px"
      />
      <ModalContent bg={modalBgColor} color={textColor}>
        <ModalHeader>
          <Text fontSize="2xl">Import Netflix History</Text>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody padding={6}>
          <Stack spacing={4}>
            <Box bg="blue.50" p={3} borderRadius="md" color="blue.700">
              <Flex alignItems="center">
                <Icon as={HiInformationCircle} boxSize={5} mr={2} />
                <Text fontSize="sm">
                  To export your Netflix watch history, go to your Netflix
                  account, select &quot;Viewing activity&quot;, and click on
                  &quot;Download all&quot;.
                </Text>
              </Flex>
            </Box>

            <FormControl id="csv-file">
              <FormLabel>Netflix History CSV</FormLabel>
              <Input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                p={1}
                height="auto"
              />
              {fileError && (
                <Text as="sub" color="red.500">
                  {fileError}
                </Text>
              )}
              {fileName && !fileError && (
                <Text as="sub" color="green.500">
                  {fileName} ready to upload
                </Text>
              )}
            </FormControl>

            {isUploading && (
              <Box>
                <Text mb={1} fontSize="sm">
                  Uploading...
                </Text>
                <Progress value={uploadProgress} size="sm" colorScheme="blue" />
              </Box>
            )}

            {importResult && (
              <Box bg="green.50" p={3} borderRadius="md" color="green.700">
                <Text fontWeight="bold" mb={2}>
                  Import Summary:
                </Text>
                <UnorderedList>
                  <ListItem>Total titles: {importResult.total}</ListItem>
                  <ListItem>
                    Successfully imported: {importResult.imported}
                  </ListItem>
                  <ListItem>
                    Matched with existing movies: {importResult.matched}
                  </ListItem>
                  <ListItem>
                    Skipped (not found): {importResult.skipped}
                  </ListItem>
                </UnorderedList>
              </Box>
            )}

            <Button
              width="100%"
              colorScheme="blue"
              leftIcon={<HiDocumentArrowUp fontSize="1.5rem" />}
              justifyContent="left"
              onClick={handleUpload}
              isLoading={isUploading}
              loadingText="Uploading..."
              isDisabled={!fileName || !!fileError || isUploading}
            >
              Upload Netflix History
            </Button>

            {fileName && (
              <Button
                variant="outline"
                colorScheme="red"
                width="100%"
                leftIcon={<HiExclamationTriangle fontSize="1.5rem" />}
                justifyContent="left"
                onClick={clearFileInput}
                isDisabled={isUploading}
              >
                Clear Selected File
              </Button>
            )}

            <Button
              variant="ghost"
              colorScheme="gray"
              width="100%"
              onClick={onClose}
              isDisabled={isUploading}
            >
              Close
            </Button>
          </Stack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default ImportNetflixHistoryModal;
