"use client";

import { useState } from "react";
import { Button, Tooltip, useToast, Icon, ButtonProps } from "@chakra-ui/react";
import { HiArrowPath } from "react-icons/hi2";

interface ForceSyncButtonProps {
  movieId: string;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  tooltipText?: string;
  displayText?: string;
  iconOnly?: boolean;
  colorScheme?: string;
  size?: "sm" | "md" | "lg";
  variant?: string;
}

export default function ForceSyncButton({
  movieId,
  onSuccess,
  onError,
  tooltipText = "Force sync movie data from external APIs",
  displayText = "Sync Now",
  iconOnly = false,
  colorScheme = "blue",
  size = "md",
  variant = "outline",
  ...buttonProps
}: ForceSyncButtonProps & Omit<ButtonProps, "onClick" | "onError">) {
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleSync = async () => {
    if (isLoading) return;

    setIsLoading(true);

    try {
      // In a real implementation, this would be an API call to initiate a sync
      // Example: await apiClient.post(`/movies/${movieId}/sync`);
      console.log(`Initiating sync for movie ID: ${movieId}`);

      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Show success toast
      toast({
        title: "Sync initiated",
        description: "The movie data will be updated in the background.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      // Show error toast
      toast({
        title: "Sync failed",
        description:
          error instanceof Error ? error.message : "An unknown error occurred",
        status: "error",
        duration: 5000,
        isClosable: true,
      });

      // Call onError callback if provided
      if (onError && error instanceof Error) {
        onError(error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const button = (
    <Button
      leftIcon={!iconOnly ? <Icon as={HiArrowPath} /> : undefined}
      isLoading={isLoading}
      loadingText={iconOnly ? undefined : "Syncing..."}
      onClick={handleSync}
      colorScheme={colorScheme}
      size={size}
      variant={variant}
      aria-label="Force sync movie data"
      {...(iconOnly && {
        p: 0,
        minW: "auto",
        w: size === "sm" ? "32px" : size === "lg" ? "48px" : "40px",
        h: size === "sm" ? "32px" : size === "lg" ? "48px" : "40px",
        borderRadius: "full",
      })}
      {...buttonProps}
    >
      {iconOnly ? <Icon as={HiArrowPath} /> : displayText}
    </Button>
  );

  return tooltipText ? <Tooltip label={tooltipText}>{button}</Tooltip> : button;
}
