// Regime label and confidence display using MUI Chip/Alert.

"use client";

import { Box, Chip, Typography } from "@mui/material";
import { RegimeResponse } from "../lib/types";
import { REGIME_COLORS } from "../theme/chartColors";

const regimeDescriptions: Record<string, string> = {
  Bull: "Growth expansion and risk-on environment. Equities trending up, credit spreads tight, and moderate volatility. Typically characterized by rising SPY/QQQ, low VIX, and stable or rising yields.",
  Bear: "Contraction and risk-off environment. Equities grinding lower, widening spreads, and rising defensive positioning. Typically characterized by declining SPY/QQQ, bonds bid, and mixed DXY.",
  Stagnation: "Sideways, low volatility, and low growth. Range-bound markets with muted returns and low conviction. Typically characterized by flat equities, low VIX, stable yields, and low volume.",
  Stagflation: "Low growth combined with rising inflation. Stocks and bonds both decline while commodities rise. Typically characterized by rising inflation expectations, gold/oil up, equities weak, and yields rising despite weak growth.",
  Crisis: "Acute stress with extreme volatility and liquidity breakdown. Correlations spike, violent drawdowns, and panic selling. Typically characterized by VIX above 35, sharp equity drops, and flight to cash/treasuries.",
};

interface RegimeBannerProps {
  regime: RegimeResponse;
}

export default function RegimeBanner({ regime }: RegimeBannerProps) {
  const color = REGIME_COLORS[regime.label] ?? "#90caf9";

  return (
    <Box mb={2}>
      <Box display="flex" alignItems="center" gap={2} mb={1}>
        <Chip
          label={regime.label}
          sx={{ backgroundColor: color, color: "#fff", fontWeight: "bold" }}
        />
        <Typography variant="body2" color="text.secondary">
          Confidence: {(regime.confidence * 100).toFixed(1)}%
        </Typography>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 800 }}>
        {regimeDescriptions[regime.label] ?? ""} The regime is determined by a Hidden Markov Model
        trained on 5 years of rolling data across equity returns (SPY, QQQ, IWM, DIA), volatility
        (VIX), dollar strength (DXY), yield curve spreads (2s10s), inflation expectations (5Y
        breakeven), and jobless claims. The confidence score of{" "}
        {(regime.confidence * 100).toFixed(1)}% represents the model's posterior probability of
        being in the current state.
      </Typography>
    </Box>
  );
}
