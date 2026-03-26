// Command palette for quick instrument navigation (Ctrl+K).
// Uses MUI Autocomplete with instrument search.

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Autocomplete, TextField, Dialog } from "@mui/material";
import { InstrumentSummary } from "../lib/types";

interface CommandPaletteProps {
  instruments: InstrumentSummary[];
}

export default function CommandPalette({ instruments }: CommandPaletteProps) {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === "Escape") {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
      <Autocomplete
        autoFocus
        openOnFocus
        options={instruments}
        getOptionLabel={(option) => option.ticker}
        onChange={(_, value) => {
          if (value) {
            router.push(`/instrument/${value.ticker}`);
            setOpen(false);
          }
        }}
        renderInput={(params) => (
          <TextField
            {...params}
            placeholder="Search instruments..."
            variant="outlined"
            sx={{ m: 2 }}
          />
        )}
      />
    </Dialog>
  );
}
