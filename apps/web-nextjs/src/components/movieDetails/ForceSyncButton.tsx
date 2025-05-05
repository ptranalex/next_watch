import { SunIcon } from "@chakra-ui/icons";
import { Button } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import axios from "axios";
import { APIClient } from "@/services/api";
import { Movie } from "@/services/api";

const apiClient = new APIClient<Movie>("/movies");

interface Props {
  id: number;
  onRefresh: () => void;
}

const ForceSyncButton = ({ id, onRefresh }: Props) => {
  const [triggered, setTriggered] = useState(false);
  const [dots, setDots] = useState("");

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    if (triggered) {
      intervalId = setInterval(() => {
        setDots((prevDots) => (prevDots.length < 3 ? prevDots + "." : ""));
      }, 500);
    }
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [triggered]);

  return (
    <Button
      marginBottom={3}
      leftIcon={<SunIcon />}
      colorScheme="blue"
      onClick={() => {
        setTriggered(true);
        apiClient.query(`${id}/force_sync`).then(() => {
          setTimeout(() => {
            onRefresh();
            setTriggered(false); // Reset the triggered state
            setDots(""); // Reset the dots
          }, 4000);
        });
      }}
    >
      {triggered ? `Force Sync Triggered${dots}` : "Force Sync"}
    </Button>
  );
};

export default ForceSyncButton;
