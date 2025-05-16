import {
  Box,
  HStack,
  Icon,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Text,
} from "@chakra-ui/react";
import React, { useState, useEffect } from "react";
import { MdGraphicEq, MdLock } from "react-icons/md";
import { RiLock2Line } from "react-icons/ri";

interface RatingSliderProps {
  step: number;
  max: number;
  min: number;
  value?: number;
  setValue: (val: number) => void;
  icon: React.ElementType;
  isLocked?: boolean;
}

const RatingSlider = ({
  value,
  step,
  max,
  setValue,
  icon,
  min,
  isLocked = false,
}: RatingSliderProps) => {
  // Local state for slider value
  const [sliderValue, setSliderValue] = useState(value);

  // Track if we're currently dragging to prevent prop updates during drag
  const [isDragging, setIsDragging] = useState(false);

  // Update local state when props change (but not during dragging)
  useEffect(() => {
    if (!isDragging) {
      setSliderValue(value);
    }
  }, [value, isDragging]);

  // Handle slider drag start
  const handleChange = (val: number) => {
    if (isLocked) return;

    setIsDragging(true);
    setSliderValue(val);
  };

  // Handle slider release
  const handleChangeEnd = (val: number) => {
    if (isLocked) return;

    // Only update URL params if value actually changed
    if (val !== value) {
      setValue(val);
    }
    setIsDragging(false);
  };

  return (
    <HStack marginBottom={3}>
      <Icon as={icon} boxSize={6} color={isLocked ? "blue.500" : "gray.500"} />
      <HStack width={10} position="relative">
        {sliderValue !== undefined ? (
          <Text>{sliderValue}</Text>
        ) : (
          <Text>-</Text>
        )}
      </HStack>
      <Slider
        aria-label="rating-slider"
        value={sliderValue !== undefined ? sliderValue : min}
        onChange={handleChange}
        onChangeEnd={handleChangeEnd}
        step={step}
        max={max}
        min={min}
        // isDisabled={isLocked}
      >
        <SliderTrack bg={"blue.100"}>
          <SliderFilledTrack bg={"blue.500"} />
        </SliderTrack>
        <SliderThumb boxSize={5}>
          <Box color="blue" as={isLocked ? RiLock2Line : MdGraphicEq} />
        </SliderThumb>
      </Slider>
    </HStack>
  );
};

export default RatingSlider;
