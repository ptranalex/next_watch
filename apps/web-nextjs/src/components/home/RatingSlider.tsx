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
import React, { useEffect, useState, useCallback } from "react";
import { MdGraphicEq } from "react-icons/md";
import { useDebounce } from "@/hooks";

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
  // Local state for immediate UI updates
  const [sliderValue, setSliderValue] = useState(value);

  // Debounced value to limit API calls
  const debouncedValue = useDebounce(sliderValue, 500);

  // Update local state when props change
  useEffect(() => {
    setSliderValue(value);
  }, [value]);

  // Update global state (and trigger URL change) only when debounced value changes
  useEffect(() => {
    if (debouncedValue !== undefined && debouncedValue !== value) {
      setValue(debouncedValue);
    }
  }, [debouncedValue, setValue, value]);

  // Handle local changes without triggering API calls immediately
  const handleSliderChange = useCallback((val: number) => {
    setSliderValue(val);
  }, []);

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
        onChange={handleSliderChange}
        step={step}
        max={max}
        defaultValue={min}
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
