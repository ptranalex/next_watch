import { LinkIcon } from "@chakra-ui/icons";
import { Button } from "@chakra-ui/react";
import { useState } from "react";

interface Props {
  fshare_link: string;
}

const FshareButton = ({ fshare_link }: Props) => {
  const [isCopied, setIsCopied] = useState(false);

  return (
    <Button
      marginBottom={3}
      leftIcon={<LinkIcon />}
      colorScheme="red"
      onClick={() => {
        navigator.clipboard
          .writeText(fshare_link ?? "")
          .then(() => {
            setIsCopied(true);
          })
          .catch((err) => {
            console.error("Could not copy fshare link: ", err);
          });
      }}
    >
      {isCopied ? "Fshare Link...Copied" : "Fshare Link"}
    </Button>
  );
};

export default FshareButton;
