import { IconButton } from "@chakra-ui/react";
import React, { useState } from "react";
import { HiCloudArrowDown, HiLink } from "react-icons/hi2";

interface CopyToClipboardButtonProps {
  textToCopy: string;
  label: string; // Aria label for the button
  size?: "sm" | "md" | "lg";
}

const CopyToClipboardButton: React.FC<CopyToClipboardButtonProps> = ({
  textToCopy,
  label,
  size = "sm",
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(textToCopy).then(() => {});
  };

  return (
    <IconButton
      aria-label={label}
      size={size}
      height="100%"
      width="100%"
      borderRadius={0}
      flexGrow={1}
      variant="ghost"
      colorScheme={isHovered ? "orange" : "gray"}
      icon={isHovered ? <HiLink /> : <HiCloudArrowDown />}
      fontSize={20}
      onClick={copyToClipboard}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    />
  );
};

export default CopyToClipboardButton;
