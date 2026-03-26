// REST fetch hooks for the C# gateway API.
// Uses SWR or React Query for caching and revalidation.

"use client";

import useSWR from "swr";
import {
    fetchDashboard,
    fetchInstrument,
    fetchChart,
    fetchProjections,
    fetchRegime,
} from "../lib/apiClient";

export function useDashboard() {
    return useSWR("dashboard", fetchDashboard);
}

export function useInstrument(ticker: string) {
    return useSWR(`instrument-${ticker}`, () => fetchInstrument(ticker));
}

export function useChart(ticker: string) {
    return useSWR(`chart-${ticker}`, () => fetchChart(ticker));
}

export function useProjections(ticker: string) {
    return useSWR(`projections-${ticker}`, () => fetchProjections(ticker));
}

export function useRegime() {
    return useSWR("regime", fetchRegime);
}