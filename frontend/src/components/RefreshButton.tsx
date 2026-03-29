// Refresh button — triggers data fetch + HMM retrain.

"use client";

import { useState } from "react";
import { Button, Typography, Box } from "@mui/material";
import { triggerRefresh } from "../lib/apiClient";

interface RefreshButtonProps {
  onComplete?: () => void;
}

export default function RefreshButton({ onComplete }: RefreshButtonProps) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const handleClick = async () => {
    setLoading(true);
    setStatus("Refreshing...");
    try {
      await triggerRefresh();
      setStatus("Refresh complete");
      onComplete?.();
    } catch {
      setStatus("Refresh failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box display="flex" alignItems="center" gap={2}>
      <Button variant="contained" onClick={handleClick} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </Button>
      {status && (
        <Typography variant="body2" color="text.secondary">
          {status}
        </Typography>
      )}
    </Box>
  );
}
