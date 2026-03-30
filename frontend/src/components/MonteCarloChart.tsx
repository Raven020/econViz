// Monte Carlo projection cone chart using Recharts ComposedChart.
// Receives pre-shaped data from the gateway — no client-side transposition needed.

"use client";

import React from "react";
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
import { ProjectionChartRow } from "../lib/types";
import { CHART_COLORS, PERCENTILE_COLORS } from "../theme/chartColors";

interface MonteCarloChartProps {
  data: ProjectionChartRow[];
}

const MonteCarloChart = React.memo(function MonteCarloChart({ data }: MonteCarloChartProps) {
  if (data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={data}>
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
