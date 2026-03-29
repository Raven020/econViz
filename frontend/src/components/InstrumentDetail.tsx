// Price info panel — current price, high, low, volume, daily change.

"use client";

import { Box, Typography, Grid } from "@mui/material";
import { InstrumentDetail as InstrumentDetailType } from "../lib/types";
import { CHART_COLORS } from "../theme/chartColors";

interface InstrumentDetailProps {
  data: InstrumentDetailType;
}

// Tickers that are indexes/levels, not dollar-denominated prices
const INDEX_TICKERS = new Set(["VIX", "DXY"]);

function formatPrice(value: number, ticker: string): string {
  if (INDEX_TICKERS.has(ticker)) return value.toFixed(2);
  return `$${value.toFixed(2)}`;
}

function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h6">{value}</Typography>
    </Box>
  );
}

export default function InstrumentDetail({ data }: InstrumentDetailProps) {
  const changeColor = data.change >= 0 ? CHART_COLORS.positive : CHART_COLORS.negative;
  const sign = data.change >= 0 ? "+" : "";

  return (
    <Box mb={3}>
      <Typography variant="h4" gutterBottom>
        {data.ticker}
      </Typography>
      <Typography variant="h3" gutterBottom>
        {formatPrice(data.close, data.ticker)}
      </Typography>
      <Typography variant="h6" sx={{ color: changeColor, mb: 3 }}>
        {sign}{data.change.toFixed(2)} ({sign}{data.change_pct.toFixed(2)}%)
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={6} sm={3}>
          <StatItem label="High" value={formatPrice(data.high, data.ticker)} />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatItem label="Low" value={formatPrice(data.low, data.ticker)} />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatItem label="Volume" value={data.volume.toLocaleString()} />
        </Grid>
      </Grid>
    </Box>
  );
}
