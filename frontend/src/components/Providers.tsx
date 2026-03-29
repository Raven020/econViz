// Client-side providers — ThemeProvider, CssBaseline, ErrorBoundary.

"use client";

import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "../theme/theme";
import ErrorBoundary from "./ErrorBoundary";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundary>{children}</ErrorBoundary>
    </ThemeProvider>
  );
}
