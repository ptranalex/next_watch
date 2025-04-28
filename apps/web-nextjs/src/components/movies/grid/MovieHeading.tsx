"use client";

import React, { useState, useEffect } from "react";
import { Heading } from "@chakra-ui/react";

interface Props {
  title: string;
}

const MovieHeading: React.FC<Props> = ({ title }) => {
  return (
    <Heading as="h1" marginY={5} fontSize="5xl">
      {title || "Movies"}
    </Heading>
  );
};

export default MovieHeading;
