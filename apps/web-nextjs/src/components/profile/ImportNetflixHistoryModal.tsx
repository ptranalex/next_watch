import React, { useRef, useState } from "react";
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  Stack,
  Text,
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
import BaseModal from "@/components/layout/BaseModal";
import { PrimaryCTA, SecondaryCTA } from "@/components/form/FormCTA";
import InfoBanner from "@/components/common/InfoBanner";
import FileInput from "@/components/form/FileInput";

interface ImportNetflixHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ImportNetflixHistoryModal: React.FC<ImportNetflixHistoryModalProps> = ({
  isOpen,
  onClose,
}) => {
  const toast = useToast();

  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<NetflixImportResult | null>(
    null
  );

  const validateCsvFile = (file: File) => {
    if (!file.name.endsWith(".csv")) {
      return "Please upload a CSV file";
    }
    return null;
  };

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setFileError(null);
    setImportResult(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast({
        title: "Error",
        description: "Please select a valid CSV file",
        status: "error",
        duration: 4000,
        isClosable: true,
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(10);

    try {
      // Use the actual API service
      const result = await userAPI.importNetflixHistory(selectedFile);
      setUploadProgress(100);
      setImportResult(result);

      const totalImported = result.newly_marked_watched;

      toast({
        title: "Import successful",
        description: `Successfully imported ${totalImported} movies from Netflix history`,
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
    setSelectedFile(null);
    setImportResult(null);
  };

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="Import Netflix History">
      <Stack spacing={4}>
        <InfoBanner variant="info">
          To export your Netflix watch history, go to your Netflix account,
          select &quot;Viewing activity&quot;, and click on &quot;Download
          all&quot;.
        </InfoBanner>

        <FileInput
          id="csv-file"
          label="Netflix History CSV"
          accept=".csv"
          onChange={handleFileChange}
          error={fileError}
          validateFile={validateCsvFile}
          isRequired={true}
        />

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
              <ListItem>Total entries: {importResult.total_entries}</ListItem>
              <ListItem>Matches found: {importResult.matched_movies}</ListItem>
              <ListItem>
                Already watched: {importResult.already_marked_watched}
              </ListItem>
              <ListItem>
                Newly marked as watched: {importResult.newly_marked_watched}
              </ListItem>
              {importResult.unmatched_titles.length > 0 && (
                <ListItem>
                  Titles not found: {importResult.unmatched_titles.length}
                </ListItem>
              )}
            </UnorderedList>

            {importResult.unmatched_titles.length > 0 && (
              <Box mt={4}>
                <Text fontWeight="bold" mb={2}>
                  Unmatched Titles:
                </Text>
                <Box maxH="150px" overflowY="auto" fontSize="sm">
                  <UnorderedList>
                    {importResult.unmatched_titles.map((title, index) => (
                      <ListItem key={index}>{title}</ListItem>
                    ))}
                  </UnorderedList>
                </Box>
              </Box>
            )}
          </Box>
        )}

        <PrimaryCTA
          width="100%"
          icon={HiDocumentArrowUp}
          onClick={handleUpload}
          isLoading={isUploading}
        >
          Upload Netflix History
        </PrimaryCTA>

        {selectedFile && (
          <SecondaryCTA
            variant="outline"
            width="100%"
            icon={HiExclamationTriangle}
            onClick={clearFileInput}
          >
            Clear Selected File
          </SecondaryCTA>
        )}
      </Stack>
    </BaseModal>
  );
};

export default ImportNetflixHistoryModal;
