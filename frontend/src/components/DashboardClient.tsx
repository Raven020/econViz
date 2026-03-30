// Client-side dashboard — receives SSR data as fallback, uses SWR for revalidation.

"use client";

import { Box, Typography, Container, Link, Divider } from "@mui/material";
import useSWR from "swr";
import {
  fetchDashboard,
  fetchRegime,
  fetchMacro,
} from "../lib/apiClient";
import type { InstrumentSummary, RegimeResponse, MacroSummary } from "../lib/types";
import { useSignalR } from "../hooks/useSignalR";
import DashboardGrid from "./DashboardGrid";
import RegimeBanner from "./RegimeBanner";
import CommandPalette from "./CommandPalette";
import RefreshButton from "./RefreshButton";
import { useSWRConfig } from "swr";

interface DashboardClientProps {
  initialInstruments: InstrumentSummary[];
  initialRegime: RegimeResponse | null;
  initialMacro: MacroSummary[];
}

export default function DashboardClient({
  initialInstruments,
  initialRegime,
  initialMacro,
}: DashboardClientProps) {
  const { data: instruments, error, isLoading } = useSWR("dashboard", fetchDashboard, {
    fallbackData: initialInstruments.length > 0 ? initialInstruments : undefined,
  });
  const { data: regime } = useSWR("regime", fetchRegime, {
    fallbackData: initialRegime ?? undefined,
  });
  const { data: macro } = useSWR("macro", fetchMacro, {
    fallbackData: initialMacro.length > 0 ? initialMacro : undefined,
  });
  const { mutate } = useSWRConfig();

  useSignalR(
    () => {
      mutate("dashboard");
      mutate("regime");
      mutate("macro");
    },
    () => mutate("regime")
  );

  if (isLoading && !instruments) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography>Loading dashboard...</Typography>
      </Container>
    );
  }

  if (error || !instruments) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography color="error">Failed to load dashboard.</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">EconViz Dashboard</Typography>
        <RefreshButton onComplete={() => { mutate("dashboard"); mutate("macro"); }} />
      </Box>
      {regime && <RegimeBanner regime={regime} />}
      <DashboardGrid data={instruments} macro={macro} />
      <CommandPalette instruments={instruments} />

      <Divider sx={{ mt: 6, mb: 3, borderColor: "rgba(255,255,255,0.08)" }} />
      <Box sx={{ textAlign: "center", pb: 4 }}>
        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 600, mx: "auto", mb: 2 }}>
          Economic indicator dashboard using Hidden Markov Models to predict market regime.
          Click on any asset to see a Monte Carlo simulation that predicts likely price
          outcomes over the next 30 days.
        </Typography>
        <Box display="flex" justifyContent="center" gap={3}>
          <Link
            href="https://github.com/Raven020"
            target="_blank"
            rel="noopener"
            color="text.secondary"
            underline="hover"
            variant="body2"
          >
            GitHub
          </Link>
          <Link
            href="https://www.linkedin.com/in/raven-clodd"
            target="_blank"
            rel="noopener"
            color="text.secondary"
            underline="hover"
            variant="body2"
          >
            LinkedIn
          </Link>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: "block" }}>
          Built by Raven Clodd
        </Typography>
      </Box>
    </Container>
  );
}
