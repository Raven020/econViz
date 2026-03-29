// Centralized color constants for charts, regimes, and data visualizations.
// These match the MUI theme palette where applicable.

export const CHART_COLORS = {
  positive: "#4caf50",
  negative: "#f44336",
  warning: "#ff9800",
  median: "#90caf9",
  actual: "#ffffff",
} as const;

export const REGIME_COLORS: Record<string, string> = {
  Bull: "#4caf50",
  Bear: "#f44336",
  Stagnation: "#ff9800",
  Stagflation: "#e91e63",
  Crisis: "#9c27b0",
};

export const PERCENTILE_COLORS: Record<number, string> = {
  10: "#f44336",
  25: "#ff9800",
  50: "#90caf9",
  75: "#ff9800",
  90: "#4caf50",
};
