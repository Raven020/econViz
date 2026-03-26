// MUI dark theme customization for the dashboard.

"use client";

import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        mode: "dark",
        primary: {
            main: "#90caf9",
        },
        secondary: {
            main: "#f48fb1",
        },
        background: {
            default: "#0a0e17",
            paper: "#111827",
        },
        success: {
            main: "#4caf50",
        },
        error: {
            main: "#f44336",
        },
    },
    typography: {
        fontFamily: "'Inter', 'Roboto', sans-serif",
    },
});

export default theme;