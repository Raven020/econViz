// Inline sparkline chart rendered inside a DataGrid cell.

"use client";

import { LineChart, Line, ResponsiveContainer } from "recharts";

interface SparklineCellProps {
  data: number[];
}

export default function SparklineCell({ data }: SparklineCellProps) {
  const color = data[data.length - 1] >= data[0] ? "#4caf50" : "#f44336";
  const chartData = data.map((value) => ({ value }));

  return (
    <ResponsiveContainer width="100%" height={40}>
      <LineChart data={chartData}>
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