// Dashboard page — main grid of all instruments with prices,
// daily changes, sparklines, and regime banner.

"use client";

import { Box, Typography, Container } from "@mui/material";
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
    </Container>
  );
}
