// Inline sparkline chart rendered inside a DataGrid cell.

"use client";

import React, { useMemo } from "react";
import { LineChart, Line, YAxis, ResponsiveContainer } from "recharts";
import { CHART_COLORS } from "../theme/chartColors";

interface SparklineCellProps {
  data: number[];
}

const SparklineCell = React.memo(function SparklineCell({ data }: SparklineCellProps) {
  const { color, chartData, min, max, padding } = useMemo(() => {
    const c = data[data.length - 1] >= data[0] ? CHART_COLORS.positive : CHART_COLORS.negative;
    const cd = data.map((value) => ({ value }));
    const mn = Math.min(...data);
    const mx = Math.max(...data);
    const pd = (mx - mn) * 0.05;
    return { color: c, chartData: cd, min: mn, max: mx, padding: pd };
  }, [data]);

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
});

export default SparklineCell;
