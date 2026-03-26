// MUI DataGrid displaying all instruments with prices, changes, and sparklines.

"use client";

import { useRouter } from "next/navigation";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { Box } from "@mui/material";
import { InstrumentSummary } from "../lib/types";
import SparklineCell from "./SparklineCell";

interface DashboardGridProps {
  data: InstrumentSummary[];
}

const columns: GridColDef[] = [
  { field: "ticker", headerName: "Ticker", flex: 1 },
  {
    field: "close",
    headerName: "Price",
    flex: 1,
    valueFormatter: (value: number) => value.toFixed(2),
  },
  {
    field: "change",
    headerName: "Change",
    flex: 1,
    valueFormatter: (value: number) => value.toFixed(2),
    cellClassName: (params) => (params.value >= 0 ? "positive" : "negative"),
  },
  {
    field: "change_pct",
    headerName: "Change %",
    flex: 1,
    valueFormatter: (value: number) => `${value.toFixed(2)}%`,
    cellClassName: (params) => (params.value >= 0 ? "positive" : "negative"),
  },
  {
    field: "volume",
    headerName: "Volume",
    flex: 1,
    valueFormatter: (value: number) => value.toLocaleString(),
  },
  {
    field: "sparkline",
    headerName: "30D Trend",
    flex: 1.5,
    sortable: false,
    renderCell: (params) => <SparklineCell data={params.value} />,
  },
];

export default function DashboardGrid({ data }: DashboardGridProps) {
  const router = useRouter();

  return (
    <Box
      sx={{
        "& .positive": { color: "#4caf50" },
        "& .negative": { color: "#f44336" },
      }}
    >
      <DataGrid
        rows={data}
        columns={columns}
        getRowId={(row) => row.ticker}
        onRowClick={(params) => router.push(`/instrument/${params.row.ticker}`)}
        disableRowSelectionOnClick
        autoHeight
      />
    </Box>
  );
}
