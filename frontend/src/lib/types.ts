// TypeScript type definitions matching the C# gateway DTOs.

//InstrumentSummary(from DashboardDto.cs) — one row in the dashboard grid:
export interface InstrumentSummary {
    ticker: string;
    close: number;
    change: number;
    change_pct: number;
    high: number;
    low: number;
    volume: number;
    sparkline: number[];
}

//ChartDataPoint(from InstrumentDto.cs) — one OHLCV bar for charts:
export interface ChartDataPoint {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

//RegimeResponse(from RegimeDto.cs) — HMM regime state:
export interface RegimeResponse {
    label: string;
    confidence: number;
    transition_matrix: number[][];
}

//InstrumentDetail(from InstrumentDto.cs) — drill - down view:
export interface InstrumentDetail {
    ticker: string;
    close: number;
    change: number;
    change_pct: number;
    high: number;
    low: number;
    volume: number;
    history: ChartDataPoint[];
    regime: RegimeResponse | null;
}

//PercentilePath(from ProjectionDto.cs) — one band of the Monte Carlo cone:
export interface PercentilePath {
    percentile: number;
    values: number[];
}