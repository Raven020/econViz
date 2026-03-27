// Monte Carlo projection cone chart using Recharts AreaChart.
// Renders percentile bands (10/25/50/75/90).

"use client";

import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { PercentilePath, ChartDataPoint } from "../lib/types";

interface MonteCarloChartProps {
  paths: PercentilePath[];
  history?: ChartDataPoint[];
}

export default function MonteCarloChart({ paths, history }: MonteCarloChartProps) {
  if (paths.length === 0) return null;

  const days = paths[0].values.length;

  // Build historical data (last 30 days, shown as negative day numbers)
  const histSlice = history ? history.slice(-30) : [];
  const histData = histSlice.map((point, i) => {
    const row: Record<string, number | undefined> = { day: i - histSlice.length };
    row.actual = point.close;
    return row;
  });

  // Build projection data (day 1..30)
  const projData = Array.from({ length: days }, (_, i) => {
    const row: Record<string, number | undefined> = { day: i + 1 };
    for (const path of paths) {
      row[`p${path.percentile}`] = path.values[i];
    }
    return row;
  });

  // Bridge point: last actual price also appears at day 0 connecting to projections
  const bridgeRow: Record<string, number | undefined> = { day: 0 };
  if (histSlice.length > 0) {
    bridgeRow.actual = histSlice[histSlice.length - 1].close;
    for (const path of paths) {
      bridgeRow[`p${path.percentile}`] = histSlice[histSlice.length - 1].close;
    }
  }

  const chartData = [...histData, bridgeRow, ...projData];

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis
          dataKey="day"
          stroke="#888"
          tick={{ fontSize: 12 }}
          label={{ value: "Days (← Past | Future →)", position: "insideBottom", offset: -5, fill: "#888" }}
        />
        <YAxis stroke="#888" tick={{ fontSize: 12 }} domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{ backgroundColor: "#111827", border: "1px solid #333" }}
        />
        <Line
          type="monotone"
          dataKey="actual"
          stroke="#ffffff"
          strokeWidth={2}
          strokeDasharray="4 4"
          dot={false}
          name="Actual Price"
        />
        <Area
          type="monotone"
          dataKey="p10"
          stroke="#f44336"
          fill="#f44336"
          fillOpacity={0.1}
          strokeWidth={1}
          name="10th"
        />
        <Area
          type="monotone"
          dataKey="p25"
          stroke="#ff9800"
          fill="#ff9800"
          fillOpacity={0.15}
          strokeWidth={1}
          name="25th"
        />
        <Area
          type="monotone"
          dataKey="p50"
          stroke="#90caf9"
          fill="#90caf9"
          fillOpacity={0.2}
          strokeWidth={2}
          name="50th (Median)"
        />
        <Area
          type="monotone"
          dataKey="p75"
          stroke="#ff9800"
          fill="#ff9800"
          fillOpacity={0.15}
          strokeWidth={1}
          name="75th"
        />
        <Area
          type="monotone"
          dataKey="p90"
          stroke="#4caf50"
          fill="#4caf50"
          fillOpacity={0.1}
          strokeWidth={1}
          name="90th"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
