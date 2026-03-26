// Root layout — MUI ThemeProvider, global styles, metadata.

"use client";

import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "../theme/theme";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}