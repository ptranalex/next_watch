import React, { useEffect, useState } from "react";
import { IconButton } from "@chakra-ui/react";
import { ArrowUpIcon } from "@chakra-ui/icons";

const ScrollToTopButton = () => {
  const [isVisible, setIsVisible] = useState(false);

  const toggleVisibility = () => {
    if (window.pageYOffset > 300) {
      setIsVisible(true);
    } else {
      setIsVisible(false);
    }
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  useEffect(() => {
    window.addEventListener("scroll", toggleVisibility);
    return () => {
      window.removeEventListener("scroll", toggleVisibility);
    };
  }, []);

  return (
    <IconButton
      aria-label="Scroll to top"
      icon={<ArrowUpIcon />}
      position="fixed"
      bottom={10}
      right={10}
      size="md"
      fontSize="xl"
      variant={"solid"}
      colorScheme="blue"
      onClick={scrollToTop}
      style={{ display: isVisible ? "inline" : "none" }}
    />
  );
};

export default ScrollToTopButton;
