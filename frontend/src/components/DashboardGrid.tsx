// Dashboard grid — instruments grouped by sector + macro indicators card.

"use client";

import React, { useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Box, Typography, Paper } from "@mui/material";
import { InstrumentSummary, MacroSummary } from "../lib/types";
import SparklineCell from "./SparklineCell";
import { CHART_COLORS } from "../theme/chartColors";

interface DashboardGridProps {
  data: InstrumentSummary[];
  macro?: MacroSummary[];
}

const sectors: { name: string; tickers: string[] }[] = [
  { name: "Equities", tickers: ["SPY", "IWM", "QQQ", "DIA"] },
  { name: "Volatility & FX", tickers: ["VIX", "DXY"] },
  { name: "Commodities", tickers: ["CRUDE_OIL", "GOLD", "SILVER", "NATURAL_GAS", "COPPER", "WHEAT"] },
  { name: "Crypto", tickers: ["BTC", "ETH", "SOL"] },
];

const MACRO_DISPLAY_NAMES: Record<string, string> = {
  FED_FUNDS: "Fed Funds Rate",
  INFLATION_5Y: "5Y Inflation Exp.",
  JOBLESS_CLAIMS: "Initial Claims",
  YIELD_SPREAD_2S10S: "2s10s Spread",
};

const MACRO_FORMAT: Record<string, (v: number) => string> = {
  FED_FUNDS: (v) => `${v.toFixed(2)}%`,
  INFLATION_5Y: (v) => `${v.toFixed(2)}%`,
  JOBLESS_CLAIMS: (v) => v.toLocaleString(undefined, { maximumFractionDigits: 0 }),
  YIELD_SPREAD_2S10S: (v) => `${(v * 100).toFixed(0)} bps`,
};

function formatMacroValue(indicator: string, value: number): string {
  return (MACRO_FORMAT[indicator] ?? ((v: number) => v.toFixed(2)))(value);
}

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

function MacroRow({ item }: { item: MacroSummary }) {
  const changeColor = item.change >= 0 ? CHART_COLORS.positive : CHART_COLORS.negative;
  const sign = item.change >= 0 ? "+" : "";
  const displayName = MACRO_DISPLAY_NAMES[item.indicator] ?? item.indicator;

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        py: 1.5,
        px: 2,
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        "&:last-child": { borderBottom: "none" },
      }}
    >
      <Box sx={{ flex: 1, minWidth: 80 }}>
        <Typography variant="body2" fontWeight="bold">
          {displayName}
        </Typography>
      </Box>
      <Box sx={{ flex: 1, textAlign: "right" }}>
        <Typography variant="body2">
          {formatMacroValue(item.indicator, item.value)}
        </Typography>
      </Box>
      <Box sx={{ flex: 1, textAlign: "right" }}>
        <Typography variant="body2" sx={{ color: changeColor }}>
          {sign}{item.change.toFixed(4)}
        </Typography>
      </Box>
      <Box sx={{ flex: 1, textAlign: "right" }}>
        <Typography variant="body2" sx={{ color: changeColor }}>
          {sign}{item.change_pct.toFixed(2)}%
        </Typography>
      </Box>
      <Box sx={{ flex: 1.5, pl: 2 }}>
        {item.sparkline && item.sparkline.length > 0 && <SparklineCell data={item.sparkline} />}
      </Box>
    </Box>
  );
}

function SectorCard({ title, headers, children }: { title: string; headers: string[]; children: React.ReactNode }) {
  return (
    <Box sx={{ breakInside: "avoid", mb: 3 }}>
      <Paper
        elevation={0}
        sx={{
          backgroundColor: "#111827",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        <Box sx={{ px: 2, py: 1.5, borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
          <Typography variant="subtitle1" fontWeight="bold">{title}</Typography>
        </Box>
        <Box>
          <Box sx={{ display: "flex", px: 2, py: 1, borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
            {headers.map((h, i) => (
              <Typography
                key={h}
                variant="caption"
                color="text.secondary"
                sx={{
                  flex: i === headers.length - 1 ? 1.5 : 1,
                  textAlign: i === 0 ? "left" : i === headers.length - 1 ? "left" : "right",
                  pl: i === headers.length - 1 ? 2 : 0,
                }}
              >
                {h}
              </Typography>
            ))}
          </Box>
          {children}
        </Box>
      </Paper>
    </Box>
  );
}

export default function DashboardGrid({ data, macro }: DashboardGridProps) {
  const router = useRouter();

  const dataMap = useMemo(() => new Map(data.map((d) => [d.ticker, d])), [data]);

  const handleNavigate = useCallback((ticker: string) => {
    router.push(`/instrument/${ticker}`);
  }, [router]);

  return (
    <Box sx={{ columns: { xs: 1, md: 2 }, columnGap: 3 }}>
      {sectors.map((sector) => {
        const instruments = sector.tickers
          .map((t) => dataMap.get(t))
          .filter((d): d is InstrumentSummary => d != null);

        if (instruments.length === 0) return null;

        return (
          <SectorCard key={sector.name} title={sector.name} headers={["Ticker", "Price", "Change", "Change %", "30D Trend"]}>
            {instruments.map((instrument) => (
              <InstrumentRow
                key={instrument.ticker}
                instrument={instrument}
                onNavigate={handleNavigate}
              />
            ))}
          </SectorCard>
        );
      })}

      {macro && macro.length > 0 && (
        <SectorCard title="Macro Indicators" headers={["Indicator", "Value", "Change", "Change %", "30D Trend"]}>
          {macro.map((item) => (
            <MacroRow key={item.indicator} item={item} />
          ))}
        </SectorCard>
      )}
    </Box>
  );
}
