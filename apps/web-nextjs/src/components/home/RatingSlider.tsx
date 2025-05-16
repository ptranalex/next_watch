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
import { MdGraphicEq } from "react-icons/md";

interface RatingSliderProps {
  step: number;
  max: number;
  min: number;
  value?: number;
  setValue: (val: number) => void;
  icon: React.ElementType;
}

const RatingSlider = ({
  value,
  step,
  max,
  setValue,
  icon,
  min,
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
    setIsDragging(true);
    setSliderValue(val);
  };

  // Handle slider release
  const handleChangeEnd = (val: number) => {
    // Only update URL params if value actually changed
    if (val !== value) {
      setValue(val);
    }
    setIsDragging(false);
  };

  return (
    <HStack marginBottom={3}>
      <Icon as={icon} boxSize={6} color="gray.500" />
      {sliderValue !== undefined ? (
        <Text width={10}>{sliderValue}</Text>
      ) : (
        <Text width={10}>-</Text>
      )}
      <Slider
        aria-label="rating-slider"
        value={sliderValue !== undefined ? sliderValue : min}
        onChange={handleChange}
        onChangeEnd={handleChangeEnd}
        step={step}
        max={max}
        min={min}
      >
        <SliderTrack bg="blue.500">
          <SliderFilledTrack bg="blue.100" />
        </SliderTrack>
        <SliderThumb boxSize={4}>
          <Box color="blue" as={MdGraphicEq} />
        </SliderThumb>
      </Slider>
    </HStack>
  );
};

export default RatingSlider;
