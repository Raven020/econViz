// HTTP client wrapper for the C# gateway.
// Configures base URL, error handling, timeout, and request defaults.

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

if (typeof window !== "undefined" && process.env.NODE_ENV === "development" && !process.env.NEXT_PUBLIC_API_URL) {
    console.warn("NEXT_PUBLIC_API_URL not set — API calls will be relative");
}

export async function apiFetch<T>(path: string): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
        const res = await fetch(`${BASE_URL}${path}`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (!res.ok) {
            let detail = "";
            try { detail = await res.text(); } catch { /* ignore */ }
            throw new Error(`API error ${res.status}: ${detail}`);
        }
        return res.json();
    } catch (err) {
        clearTimeout(timeoutId);
        if (err instanceof DOMException && err.name === "AbortError") {
            throw new Error(`Request to ${path} timed out after 15s`);
        }
        throw err;
    }
}

import type {
    InstrumentSummary,
    InstrumentDetail,
    ChartDataPoint,
    RegimeResponse,
    PercentilePath,
    MacroSummary,
    ProjectionChartRow,
} from "./types";

export const fetchDashboard = () =>
    apiFetch<InstrumentSummary[]>("/api/dashboard");

export const fetchInstrument = (ticker: string) =>
    apiFetch<InstrumentDetail>(`/api/instrument/${encodeURIComponent(ticker)}`);

export const fetchChart = (ticker: string) =>
    apiFetch<ChartDataPoint[]>(`/api/instrument/${encodeURIComponent(ticker)}/chart`);

export const fetchProjections = (ticker: string) =>
    apiFetch<PercentilePath[]>(`/api/instrument/${encodeURIComponent(ticker)}/projections`);

export const fetchRegime = () =>
    apiFetch<RegimeResponse>("/api/regime");

export const fetchMacro = () =>
    apiFetch<MacroSummary[]>("/api/dashboard/macro");

export const fetchProjectionChart = (ticker: string) =>
    apiFetch<ProjectionChartRow[]>(`/api/instrument/${encodeURIComponent(ticker)}/projections/chart`);

export const triggerRefresh = () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);
    return fetch(`${BASE_URL}/api/refresh`, { method: "POST", signal: controller.signal })
        .then(res => {
            if (!res.ok) throw new Error(`Refresh failed: ${res.status}`);
            return res;
        })
        .finally(() => clearTimeout(timeoutId));
};
