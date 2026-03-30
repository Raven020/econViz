// Inline sparkline chart using SVG polyline — lightweight, SSR-safe.

"use client";

import React, { useMemo } from "react";
import { CHART_COLORS } from "../theme/chartColors";

interface SparklineCellProps {
  data: number[];
}

const SparklineCell = React.memo(function SparklineCell({ data }: SparklineCellProps) {
  const { color, points } = useMemo(() => {
    const c = data[data.length - 1] >= data[0] ? CHART_COLORS.positive : CHART_COLORS.negative;
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min;
    const padding = range * 0.05 || 0.5;

    const pts = data
      .map((value, i) => {
        const x = data.length > 1 ? (i / (data.length - 1)) * 100 : 50;
        const y = 40 - ((value - min + padding) / (range + 2 * padding)) * 40;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");

    return { color: c, points: pts };
  }, [data]);

  return (
    <svg viewBox="0 0 100 40" preserveAspectRatio="none" width="100%" height={40}>
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
});

export default SparklineCell;
