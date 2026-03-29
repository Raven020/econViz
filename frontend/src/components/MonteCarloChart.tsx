// Monte Carlo projection cone chart using Recharts ComposedChart.
// Renders percentile bands (10/25/50/75/90) with memoized data transforms.

"use client";

import React, { useMemo } from "react";
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
import { CHART_COLORS, PERCENTILE_COLORS } from "../theme/chartColors";

interface MonteCarloChartProps {
  paths: PercentilePath[];
  history?: ChartDataPoint[];
}

const MonteCarloChart = React.memo(function MonteCarloChart({ paths, history }: MonteCarloChartProps) {
  const chartData = useMemo(() => {
    if (paths.length === 0) return null;

    const days = paths[0].values.length;

    const histSlice = history ? history.slice(-30) : [];
    const histData = histSlice.map((point, i) => {
      const row: Record<string, number | undefined> = { day: i - histSlice.length };
      row.actual = point.close;
      return row;
    });

    const projData = Array.from({ length: days }, (_, i) => {
      const row: Record<string, number | undefined> = { day: i + 1 };
      for (const path of paths) {
        row[`p${path.percentile}`] = path.values[i];
      }
      return row;
    });

    const bridgeRow: Record<string, number | undefined> = { day: 0 };
    if (histSlice.length > 0) {
      bridgeRow.actual = histSlice[histSlice.length - 1].close;
      for (const path of paths) {
        bridgeRow[`p${path.percentile}`] = histSlice[histSlice.length - 1].close;
      }
    }

    return [...histData, bridgeRow, ...projData];
  }, [paths, history]);

  if (!chartData) return null;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis
          dataKey="day"
          stroke="#888"
          tick={{ fontSize: 12 }}
          label={{ value: "Days (\u2190 Past | Future \u2192)", position: "insideBottom", offset: -5, fill: "#888" }}
        />
        <YAxis stroke="#888" tick={{ fontSize: 12 }} domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{ backgroundColor: "#111827", border: "1px solid #333" }}
        />
        <Line
          type="monotone"
          dataKey="actual"
          stroke={CHART_COLORS.actual}
          strokeWidth={2}
          strokeDasharray="4 4"
          dot={false}
          name="Actual Price"
        />
        <Area type="monotone" dataKey="p10" stroke={PERCENTILE_COLORS[10]} fill={PERCENTILE_COLORS[10]} fillOpacity={0.1} strokeWidth={1} name="10th" />
        <Area type="monotone" dataKey="p25" stroke={PERCENTILE_COLORS[25]} fill={PERCENTILE_COLORS[25]} fillOpacity={0.15} strokeWidth={1} name="25th" />
        <Area type="monotone" dataKey="p50" stroke={PERCENTILE_COLORS[50]} fill={PERCENTILE_COLORS[50]} fillOpacity={0.2} strokeWidth={2} name="50th (Median)" />
        <Area type="monotone" dataKey="p75" stroke={PERCENTILE_COLORS[75]} fill={PERCENTILE_COLORS[75]} fillOpacity={0.15} strokeWidth={1} name="75th" />
        <Area type="monotone" dataKey="p90" stroke={PERCENTILE_COLORS[90]} fill={PERCENTILE_COLORS[90]} fillOpacity={0.1} strokeWidth={1} name="90th" />
      </ComposedChart>
    </ResponsiveContainer>
  );
});

export default MonteCarloChart;
