"use client";

import React, { useState, useEffect } from "react";
import {
  Box,
  VStack,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Text,
} from "@chakra-ui/react";

const RatingSliderGroup: React.FC = () => {
  return (
    <VStack spacing={6} align="stretch" width="100%">
      <Box>
        <Text mb={2}>Minimum Rating: 0</Text>
        <Slider defaultValue={0} min={0} max={10} step={1}>
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb />
        </Slider>
      </Box>

      <Box>
        <Text mb={2}>Year Range: 1900 - 2023</Text>
        <Slider defaultValue={2023} min={1900} max={2023} step={1}>
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb />
        </Slider>
      </Box>
    </VStack>
  );
};

export default RatingSliderGroup;
