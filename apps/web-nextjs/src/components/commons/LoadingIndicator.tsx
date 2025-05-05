import { Box, Spinner } from "@chakra-ui/react";
import React from "react";

const LoadingIndicator = () => {
  return (
    <Box
      position="fixed"
      top="0"
      left="0"
      right="0"
      zIndex="9999"
      height="3px"
      bg="transparent"
      _after={{
        content: '""',
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        background:
          "linear-gradient(to right, transparent, blue.500, transparent)",
        animation: "loading 1s infinite",
      }}
      sx={{
        "@keyframes loading": {
          "0%": {
            transform: "translateX(-100%)",
          },
          "100%": {
            transform: "translateX(100%)",
          },
        },
      }}
    />
  );
};

export default LoadingIndicator;
