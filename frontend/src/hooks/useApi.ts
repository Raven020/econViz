// REST fetch hooks for the C# gateway API.
// Uses SWR for caching and revalidation.

"use client";

import useSWR from "swr";
import {
    fetchDashboard,
    fetchInstrument,
    fetchChart,
    fetchProjections,
    fetchRegime,
    fetchMacro,
    fetchProjectionChart,
} from "../lib/apiClient";

export function useDashboard() {
    return useSWR("dashboard", fetchDashboard);
}

export function useInstrument(ticker: string | null) {
    return useSWR(ticker ? `instrument-${ticker}` : null, () => fetchInstrument(ticker!));
}

export function useChart(ticker: string | null) {
    return useSWR(ticker ? `chart-${ticker}` : null, () => fetchChart(ticker!));
}

export function useProjections(ticker: string | null) {
    return useSWR(ticker ? `projections-${ticker}` : null, () => fetchProjections(ticker!));
}

export function useRegime() {
    return useSWR("regime", fetchRegime);
}

export function useMacro() {
    return useSWR("macro", fetchMacro);
}

export function useProjectionChart(ticker: string | null) {
    return useSWR(ticker ? `projection-chart-${ticker}` : null, () => fetchProjectionChart(ticker!));
}
