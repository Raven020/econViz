// Dashboard page — main grid of all instruments with prices,
// daily changes, sparklines, and regime banner.

"use client";

import { Box, Typography, Container, Link, Divider } from "@mui/material";
import { useDashboard, useRegime } from "../hooks/useApi";
import { useSignalR } from "../hooks/useSignalR";
import DashboardGrid from "../components/DashboardGrid";
import RegimeBanner from "../components/RegimeBanner";
import CommandPalette from "../components/CommandPalette";
import RefreshButton from "../components/RefreshButton";
import { useSWRConfig } from "swr";

export default function DashboardPage() {
  const { data: instruments, error, isLoading } = useDashboard();
  const { data: regime } = useRegime();
  const { mutate } = useSWRConfig();

  useSignalR(
    () => {
      mutate("dashboard");
      mutate("regime");
    },
    () => mutate("regime")
  );

  if (isLoading) {
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
        <RefreshButton onComplete={() => mutate("dashboard")} />
      </Box>
      {regime && <RegimeBanner regime={regime} />}
      <DashboardGrid data={instruments} />
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
