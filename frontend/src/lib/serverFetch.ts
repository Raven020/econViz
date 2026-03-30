// Server-side fetch functions for SSR data loading.
// Uses INTERNAL_API_URL (non-public env var) to call the gateway directly.
// Returns null on failure for graceful degradation to client-side SWR.

import type { InstrumentSummary, RegimeResponse, MacroSummary } from "./types";

const INTERNAL_URL = process.env.INTERNAL_API_URL || "http://localhost:5000";

async function serverFetch<T>(path: string): Promise<T | null> {
    try {
        const res = await fetch(`${INTERNAL_URL}${path}`, {
            next: { revalidate: 60 },
        });
        if (!res.ok) return null;
        return res.json();
    } catch {
        return null;
    }
}

export const fetchDashboardSSR = () =>
    serverFetch<InstrumentSummary[]>("/api/dashboard");

export const fetchRegimeSSR = () =>
    serverFetch<RegimeResponse>("/api/regime");

export const fetchMacroSSR = () =>
    serverFetch<MacroSummary[]>("/api/dashboard/macro");
