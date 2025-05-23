import { CircularProgress, CircularProgressLabel } from "@chakra-ui/react";
import type { CriticScoreProps } from "./types";

const CriticScore = ({ source, value, scale_up = 1 }: CriticScoreProps) => {
  const getColor = (source: string, value: number | null | undefined) => {
    let color: string;
    let progress_display: number;
    let score_display: string;

    if (value === null || value === undefined) {
      score_display = "•";
      color = "transparent";
      progress_display = 0;
    } else {
      if (source === "imdb") {
        // Format: "6.5/10"
        progress_display = value * 10;
        score_display = value.toFixed(1);
        if (value >= 8.0) {
          color = "feedback.success.emphasis";
        } else if (value >= 7.0) {
          color = "feedback.success";
        } else if (value >= 6.0) {
          color = "colors.primary";
        } else {
          color = "text.tertiary";
        }
      } else if (source === "rotten_tomatoes") {
        // Format: "74%"
        score_display = value.toString();
        progress_display = value;
        if (value >= 90) {
          color = "feedback.success.emphasis";
        } else if (value >= 70) {
          color = "feedback.success";
        } else if (value >= 50) {
          color = "colors.primary";
        } else {
          color = "text.tertiary";
        }
      } else if (source === "metacritic") {
        // Format: "74/100"
        score_display = value.toString();
        progress_display = value;
        if (value >= 90) {
          color = "feedback.success.emphasis";
        } else if (value >= 70) {
          color = "feedback.success";
        } else if (value >= 50) {
          color = "colors.primary";
        } else {
          color = "text.tertiary";
        }
      } else {
        throw new Error(`Unknown rating source: ${source}`);
      }
    }
    return [score_display, progress_display, color];
  };

  const [score_display, progress_display, color] = getColor(source, value);

  return (
    <>
      <CircularProgress
        value={Number(progress_display)}
        color={color as string}
        size={`${40 * scale_up}px`}
        thickness={value === null || value === undefined ? "1px" : "10px"}
      >
        <CircularProgressLabel fontSize={`${12 * scale_up}px`}>
          {score_display}
        </CircularProgressLabel>
      </CircularProgress>
    </>
  );
};

export default CriticScore;
