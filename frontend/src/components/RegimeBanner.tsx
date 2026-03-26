// Regime label and confidence display using MUI Chip/Alert.

"use client";

import { Box, Chip, Typography } from "@mui/material";
import { RegimeResponse } from "../lib/types";

const regimeColors: Record<string, string> = {
  Bull: "#4caf50",
  Bear: "#f44336",
  Stagnation: "#ff9800",
  Stagflation: "#e91e63",
  Crisis: "#9c27b0",
};

interface RegimeBannerProps {
  regime: RegimeResponse;
}

export default function RegimeBanner({ regime }: RegimeBannerProps) {
  const color = regimeColors[regime.label] ?? "#90caf9";

  return (
    <Box display="flex" alignItems="center" gap={2} mb={2}>
      <Chip
        label={regime.label}
        sx={{ backgroundColor: color, color: "#fff", fontWeight: "bold" }}
      />
      <Typography variant="body2" color="text.secondary">
        Confidence: {(regime.confidence * 100).toFixed(1)}%
      </Typography>
    </Box>
  );
}
