// Inline sparkline chart rendered inside a DataGrid cell.

"use client";

import { LineChart, Line, YAxis, ResponsiveContainer } from "recharts";

interface SparklineCellProps {
  data: number[];
}

export default function SparklineCell({ data }: SparklineCellProps) {
  const color = data[data.length - 1] >= data[0] ? "#4caf50" : "#f44336";
  const chartData = data.map((value) => ({ value }));

  const min = Math.min(...data);
  const max = Math.max(...data);
  const padding = (max - min) * 0.05;

  return (
    <ResponsiveContainer width="100%" height={40}>
      <LineChart data={chartData}>
        <YAxis domain={[min - padding, max + padding]} hide />
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          dot={false}
          strokeWidth={1.5}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}