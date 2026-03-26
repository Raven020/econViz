// HTTP client wrapper for the C# gateway.
// Configures base URL, error handling, and request defaults.

// Base URL — point at the C# gateway on port 5000:
const BASE_URL = "http://localhost:5000";

//Generic fetch helper — handles the URL prefix, JSON parsing, and error checking in one place so you don't repeat it in
//every hook:
export async function apiFetch<T>(path: string): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
}

//Typed endpoint functions — one per gateway route, returning the correct type:
import type {
    InstrumentSummary,
    InstrumentDetail,
    ChartDataPoint,
    RegimeResponse,
    PercentilePath,
} from "./types";

export const fetchDashboard = () =>
    apiFetch<InstrumentSummary[]>("/api/dashboard");

export const fetchInstrument = (ticker: string) =>
    apiFetch<InstrumentDetail>(`/api/instrument/${ticker}`);

export const fetchChart = (ticker: string) =>
    apiFetch<ChartDataPoint[]>(`/api/instrument/${ticker}/chart`);

export const fetchProjections = (ticker: string) =>
    apiFetch<PercentilePath[]>(`/api/instrument/${ticker}/projections`);

export const fetchRegime = () =>
    apiFetch<RegimeResponse>("/api/regime");

export const triggerRefresh = () =>
    fetch(`${BASE_URL}/api/refresh`, { method: "POST" });