// Dashboard grid — instruments grouped by sector in card boxes.

"use client";

import React, { useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Box, Typography, Paper } from "@mui/material";
import { InstrumentSummary } from "../lib/types";
import SparklineCell from "./SparklineCell";
import { CHART_COLORS } from "../theme/chartColors";

interface DashboardGridProps {
  data: InstrumentSummary[];
}

const sectors: { name: string; tickers: string[] }[] = [
  { name: "Equities", tickers: ["SPY", "IWM", "QQQ", "DIA"] },
  { name: "Volatility & FX", tickers: ["VIX", "DXY"] },
  { name: "Macro Indicators", tickers: ["INFLATION_5Y", "JOBLESS_CLAIMS"] },
  { name: "Commodities", tickers: ["CRUDE_OIL", "GOLD", "SILVER", "NATURAL_GAS", "COPPER", "WHEAT"] },
  { name: "Crypto", tickers: ["BTC", "ETH", "SOL"] },
  { name: "Fixed Income & Rates", tickers: ["US_10Y", "US_2Y", "YIELD_SPREAD_2S10S"] },
];

const InstrumentRow = React.memo(function InstrumentRow(
  { instrument, onNavigate }: { instrument: InstrumentSummary; onNavigate: (ticker: string) => void }
) {
  const changeColor = instrument.change >= 0 ? CHART_COLORS.positive : CHART_COLORS.negative;
  const sign = instrument.change >= 0 ? "+" : "";

  const handleClick = useCallback(() => onNavigate(instrument.ticker), [onNavigate, instrument.ticker]);
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onNavigate(instrument.ticker);
    }
  }, [onNavigate, instrument.ticker]);

  return (
    <Box
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={`View ${instrument.ticker} details, price ${instrument.close.toFixed(2)}`}
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        py: 1.5,
        px: 2,
        cursor: "pointer",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        "&:last-child": { borderBottom: "none" },
        "&:hover": { backgroundColor: "rgba(255,255,255,0.04)" },
        "&:focus-visible": { outline: "2px solid #90caf9", outlineOffset: -2 },
      }}
    >
      <Box sx={{ flex: 1, minWidth: 80 }}>
        <Typography variant="body2" fontWeight="bold">
          {instrument.ticker}
        </Typography>
      </Box>
      <Box sx={{ flex: 1, textAlign: "right" }}>
        <Typography variant="body2">
          {instrument.close.toFixed(2)}
        </Typography>
      </Box>
      <Box sx={{ flex: 1, textAlign: "right" }}>
        <Typography variant="body2" sx={{ color: changeColor }}>
          {sign}{instrument.change.toFixed(2)}
        </Typography>
      </Box>
      <Box sx={{ flex: 1, textAlign: "right" }}>
        <Typography variant="body2" sx={{ color: changeColor }}>
          {sign}{instrument.change_pct.toFixed(2)}%
        </Typography>
      </Box>
      <Box sx={{ flex: 1.5, pl: 2 }}>
        {instrument.sparkline && instrument.sparkline.length > 0 && <SparklineCell data={instrument.sparkline} />}
      </Box>
    </Box>
  );
});

export default function DashboardGrid({ data }: DashboardGridProps) {
  const router = useRouter();

  const dataMap = useMemo(() => new Map(data.map((d) => [d.ticker, d])), [data]);

  const handleNavigate = useCallback((ticker: string) => {
    router.push(`/instrument/${ticker}`);
  }, [router]);

  return (
    <Box
      sx={{
        columns: { xs: 1, md: 2 },
        columnGap: 3,
      }}
    >
      {sectors.map((sector) => {
        const instruments = sector.tickers
          .map((t) => dataMap.get(t))
          .filter((d): d is InstrumentSummary => d != null);

        if (instruments.length === 0) return null;

        return (
          <Box key={sector.name} sx={{ breakInside: "avoid", mb: 3 }}>
            <Paper
              elevation={0}
              sx={{
                backgroundColor: "#111827",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 2,
                overflow: "hidden",
              }}
            >
              <Box
                sx={{
                  px: 2,
                  py: 1.5,
                  borderBottom: "1px solid rgba(255,255,255,0.1)",
                }}
              >
                <Typography variant="subtitle1" fontWeight="bold">
                  {sector.name}
                </Typography>
              </Box>
              <Box>
                <Box
                  sx={{
                    display: "flex",
                    px: 2,
                    py: 1,
                    borderBottom: "1px solid rgba(255,255,255,0.06)",
                  }}
                >
                  <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
                    Ticker
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ flex: 1, textAlign: "right" }}>
                    Price
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ flex: 1, textAlign: "right" }}>
                    Change
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ flex: 1, textAlign: "right" }}>
                    Change %
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ flex: 1.5, pl: 2 }}>
                    30D Trend
                  </Typography>
                </Box>
                {instruments.map((instrument) => (
                  <InstrumentRow
                    key={instrument.ticker}
                    instrument={instrument}
                    onNavigate={handleNavigate}
                  />
                ))}
              </Box>
            </Paper>
          </Box>
        );
      })}
    </Box>
  );
}
