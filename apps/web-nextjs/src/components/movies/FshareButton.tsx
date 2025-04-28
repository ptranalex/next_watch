"use client";

import {
  Button,
  ButtonProps,
  IconButton,
  Tooltip,
  useToast,
} from "@chakra-ui/react";
import { FiShare2 } from "react-icons/fi";

interface FshareButtonProps extends Omit<ButtonProps, "onClick"> {
  movieId: string;
  movieTitle: string;
  fshareUrl?: string;
  iconOnly?: boolean;
  size?: string;
  colorScheme?: string;
}

export default function FshareButton({
  movieId,
  movieTitle,
  fshareUrl,
  iconOnly = false,
  size = "md",
  colorScheme = "blue",
  ...rest
}: FshareButtonProps) {
  const toast = useToast();

  const handleShare = async () => {
    try {
      // Check if the Web Share API is available
      if (navigator.share) {
        await navigator.share({
          title: movieTitle,
          text: `Check out "${movieTitle}" on Next Watch`,
          url: fshareUrl || `${window.location.origin}/movies/${movieId}`,
        });

        toast({
          title: "Shared successfully",
          status: "success",
          duration: 2000,
          isClosable: true,
        });

        return;
      }

      // Fallback for browsers that don't support the Web Share API
      const shareUrl =
        fshareUrl || `${window.location.origin}/movies/${movieId}`;

      // Copy to clipboard as fallback
      await navigator.clipboard.writeText(shareUrl);

      toast({
        title: "Link copied to clipboard",
        description: "You can now share it manually",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch {
      toast({
        title: "Sharing failed",
        description: "Could not share the movie link",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (iconOnly) {
    return (
      <Tooltip label="Share this movie">
        <IconButton
          icon={<FiShare2 />}
          onClick={handleShare}
          aria-label="Share movie"
          size={size}
          colorScheme={colorScheme}
          {...rest}
        />
      </Tooltip>
    );
  }

  return (
    <Button
      leftIcon={<FiShare2 />}
      onClick={handleShare}
      size={size}
      colorScheme={colorScheme}
      {...rest}
    >
      Share
    </Button>
  );
}
