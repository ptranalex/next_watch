import { Avatar, Flex, Heading, Stack, Text, VStack } from "@chakra-ui/react";
import React, { useState } from "react";
import { HiArrowRightOnRectangle, HiOutlineArrowUpTray } from "react-icons/hi2";
import { useAuth } from "@/hooks";
import { useRouter } from "next/navigation";
import ImportNetflixHistoryModal from "@/components/features/profile/ImportNetflixHistoryModal";
import BaseModal from "@/components/ui/organisms/BaseModal";
import {
  PrimaryCTA,
  TertiaryCTA,
  Divider,
} from "@/components/ui/molecules/form/FormCTA";
import type { ProfileModalProps } from "./types";

const ProfileModal: React.FC<ProfileModalProps> = ({
  isOpen,
  onClose,
  // activeTab functionality to be implemented
}) => {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);

  const handleLogout = () => {
    logout();
    onClose();
    router.push("/");
  };

  const openImportModal = () => {
    onClose(); // Close profile modal first
    setIsImportModalOpen(true);
  };

  const closeImportModal = () => {
    setIsImportModalOpen(false);
  };

  if (!user) {
    return null;
  }

  return (
    <>
      <BaseModal isOpen={isOpen} onClose={onClose} title="Profile">
        <Stack spacing={4}>
          <Flex justifyContent="center">
            <Avatar size="xl" name={user.username || user.email} mb={4} />
          </Flex>

          <VStack align="center" spacing={1}>
            <Heading as="h3" size="md">
              {user.username || "User"}
            </Heading>
            <Text color="gray.500">{user.email}</Text>
          </VStack>

          <Divider />

          <Heading as="h4" size="sm" alignSelf="center" mb={2}>
            Watch History
          </Heading>

          <PrimaryCTA onClick={openImportModal} icon={HiOutlineArrowUpTray}>
            Import Netflix History
          </PrimaryCTA>

          <TertiaryCTA onClick={handleLogout} icon={HiArrowRightOnRectangle}>
            Logout
          </TertiaryCTA>
        </Stack>
      </BaseModal>

      <ImportNetflixHistoryModal
        isOpen={isImportModalOpen}
        onClose={closeImportModal}
      />
    </>
  );
};

export default ProfileModal;
