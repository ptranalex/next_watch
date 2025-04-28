"use client";

import { useState } from "react";
import {
  IconButton,
  IconButtonProps,
  Tooltip,
  useClipboard,
  useToast,
} from "@chakra-ui/react";
import { HiClipboard, HiClipboardCheck } from "react-icons/hi";

interface CopyToClipBoardButtonProps
  extends Omit<IconButtonProps, "aria-label"> {
  textToCopy: string;
  tooltipText?: string;
  successMessage?: string;
  errorMessage?: string;
  "aria-label"?: string;
}

export default function CopyToClipBoardButton({
  textToCopy,
  tooltipText = "Copy to clipboard",
  successMessage = "Copied to clipboard!",
  errorMessage = "Failed to copy",
  "aria-label": ariaLabel = "Copy to clipboard",
  size = "sm",
  variant = "ghost",
  ...rest
}: CopyToClipBoardButtonProps) {
  const [isCopied, setIsCopied] = useState(false);
  const { onCopy } = useClipboard(textToCopy);
  const toast = useToast();

  const handleCopy = () => {
    try {
      onCopy();
      setIsCopied(true);

      toast({
        title: successMessage,
        status: "success",
        duration: 2000,
        isClosable: true,
      });

      // Reset the icon after 2 seconds
      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    } catch {
      toast({
        title: errorMessage,
        status: "error",
        duration: 2000,
        isClosable: true,
      });
    }
  };

  return (
    <Tooltip label={tooltipText}>
      <IconButton
        icon={isCopied ? <HiClipboardCheck /> : <HiClipboard />}
        onClick={handleCopy}
        aria-label={ariaLabel}
        size={size}
        variant={variant}
        {...rest}
      />
    </Tooltip>
  );
}
