// Historical price chart using Recharts LineChart.

"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { ChartDataPoint } from "../lib/types";
import { CHART_COLORS } from "../theme/chartColors";

interface PriceChartProps {
  data: ChartDataPoint[];
}

const PriceChart = React.memo(function PriceChart({ data }: PriceChartProps) {
  const color = data.length >= 2 && data[data.length - 1].close >= data[0].close
    ? CHART_COLORS.positive
    : CHART_COLORS.negative;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis
          dataKey="date"
          stroke="#888"
          tick={{ fontSize: 12 }}
        />
        <YAxis
          stroke="#888"
          tick={{ fontSize: 12 }}
          domain={["auto", "auto"]}
        />
        <Tooltip
          contentStyle={{ backgroundColor: "#111827", border: "1px solid #333" }}
        />
        <Line
          type="monotone"
          dataKey="close"
          stroke={color}
          dot={false}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
});

export default PriceChart;
