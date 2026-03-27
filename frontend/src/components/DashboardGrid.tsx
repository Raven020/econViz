// Dashboard grid — instruments grouped by sector in card boxes.

"use client";

import { useRouter } from "next/navigation";
import { Box, Typography, Grid, Paper } from "@mui/material";
import { InstrumentSummary } from "../lib/types";
import SparklineCell from "./SparklineCell";

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

function InstrumentRow({ instrument, onClick }: { instrument: InstrumentSummary; onClick: () => void }) {
  const changeColor = instrument.change >= 0 ? "#4caf50" : "#f44336";
  const sign = instrument.change >= 0 ? "+" : "";

  return (
    <Box
      onClick={onClick}
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
        {instrument.sparkline && <SparklineCell data={instrument.sparkline} />}
      </Box>
    </Box>
  );
}

export default function DashboardGrid({ data }: DashboardGridProps) {
  const router = useRouter();

  const dataMap = new Map(data.map((d) => [d.ticker, d]));

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
                    onClick={() => router.push(`/instrument/${instrument.ticker}`)}
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
