"use client";

import React from "react";
import { Box, Heading, Text } from "@chakra-ui/react";
import withPermission from "@/components/auth/withPermission";

/**
 * Admin page content - only displayed to users with admin access
 */
const AdminPage: React.FC = () => {
  return (
    <Box p={5} maxW="1200px" mx="auto">
      <Heading mb={4}>Admin Dashboard</Heading>
      <Text mb={4}>
        This page is protected by the withPermission HOC. Only users with the
        &quot;admin:access&quot; permission can see this content.
      </Text>

      <Box p={4} borderWidth={1} borderRadius="md">
        <Heading size="md" mb={2}>
          Admin Controls
        </Heading>
        <Text>These controls are only visible to administrators.</Text>
      </Box>
    </Box>
  );
};

// Wrap component with permission check
export default withPermission(AdminPage, {
  requiredPermission: "admin:access",
  redirectTo: "/",
  showLoading: true,
});
