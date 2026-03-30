// HTTP client for communicating with the Python FastAPI backend.
// Wraps all /internal/* endpoint calls.

using System.Net.Http.Json;
using System.Text.Json;
using EconViz.Gateway.Models;

namespace EconViz.Gateway.Services;

public class PythonApiClient
{
    private readonly HttpClient _http;
    private static readonly JsonSerializerOptions _jsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
    };

    /// <summary>
    /// Constructor — receives an HttpClient with BaseAddress pre-configured
    /// from appsettings.json ("PythonBackend:BaseUrl").
    /// ASP.NET DI injects this automatically via AddHttpClient.
    /// </summary>
    /// <param name="http">HttpClient configured with Python backend base URL</param>
    public PythonApiClient(HttpClient http)
    {
        _http = http;
    }

    /// <summary>
    /// Fetches all instruments with latest prices, changes, and sparkline data.
    /// Calls: GET /internal/instruments
    /// </summary>
    /// <returns>List of InstrumentSummary, one per tracked instrument</returns>
    public async Task<List<InstrumentSummary>> GetInstrumentsAsync()
    {
        // Retrieves summary of all instruments
        return await _http.GetFromJsonAsync<List<InstrumentSummary>>("/internal/instruments", _jsonOptions);
    }

    /// <summary>
    /// Fetches macro indicator summaries (fed funds, inflation, jobless claims, yield spread).
    /// Calls: GET /internal/macro
    /// </summary>
    public async Task<List<MacroSummary>> GetMacroAsync()
    {
        return await _http.GetFromJsonAsync<List<MacroSummary>>("/internal/macro", _jsonOptions);
    }

    /// <summary>
    /// Fetches full detail for a single instrument including OHLCV history and regime.
    /// Calls: GET /internal/instrument/{ticker}
    /// </summary>
    /// <param name="ticker">Instrument identifier (e.g. "SPY", "BTC")</param>
    /// <returns>InstrumentDetail with history and regime, or null if not found</returns>
    public async Task<InstrumentDetail?> GetInstrumentAsync(string ticker)
    {
        // Retrieves details for 1 ticker
        return await _http.GetFromJsonAsync<InstrumentDetail>($"/internal/instrument/{ticker}", _jsonOptions);
    }

    /// <summary>
    /// Triggers a full data refresh: fetch prices, retrain HMM, run Monte Carlo.
    /// Calls: POST /internal/refresh (no request body)
    /// </summary>
    /// <returns>Raw JsonElement with status and regime info from Python</returns>
    public async Task<JsonElement> RefreshAsync()
    {
        // Refreshes summary
        var response = await _http.PostAsync("/internal/refresh", null);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>(_jsonOptions);
    }

    /// <summary>
    /// Fetches Monte Carlo projection cone for a single instrument.
    /// Calls: GET /internal/instrument/{ticker}/projections
    /// Flattens day_1..day_30 fields from each JSON row into a List of double Values.
    /// </summary>
    /// <param name="ticker">Instrument identifier (e.g. "SPY", "BTC")</param>
    /// <returns>List of PercentilePath (one per percentile: 10, 25, 50, 75, 90)</returns>
    public async Task<List<PercentilePath>> GetProjectionsAsync(string ticker)
    {
        // Retrieves and parses 30 day projection from Monte Carlo
        var response = await _http.GetFromJsonAsync<List<JsonElement>>($"/internal/instrument/{ticker}/projections", _jsonOptions);

        var paths = new List<PercentilePath>();
        foreach (var row in response)
        {
            int percentile = row.GetProperty("percentile").GetInt32();
            var values = new List<double>();
            for (int d = 1; d <= 30; d++)
                values.Add(row.GetProperty($"day_{d}").GetDouble());
            paths.Add(new PercentilePath(percentile, values));
        }
        return paths;
    }

    /// <summary>
    /// Returns pre-shaped chart data: history (last 30 days) + bridge + projections (30 days).
    /// Each row has day, actual, p10, p25, p50, p75, p90 — ready for Recharts.
    /// </summary>
    public async Task<List<ProjectionChartRow>> GetProjectionChartAsync(string ticker)
    {
        var paths = await GetProjectionsAsync(ticker);
        var detail = await GetInstrumentAsync(ticker);

        var chart = new List<ProjectionChartRow>();

        // History (last 30 days, negative day numbers)
        if (detail?.History != null)
        {
            var histSlice = detail.History.TakeLast(30).ToList();
            for (int i = 0; i < histSlice.Count; i++)
            {
                chart.Add(new ProjectionChartRow(
                    Day: i - histSlice.Count,
                    Actual: histSlice[i].Close,
                    P10: null, P25: null, P50: null, P75: null, P90: null
                ));
            }

            // Bridge row (day 0) — connects history to projections
            var lastClose = histSlice.Last().Close;
            chart.Add(new ProjectionChartRow(
                Day: 0,
                Actual: lastClose,
                P10: lastClose, P25: lastClose, P50: lastClose, P75: lastClose, P90: lastClose
            ));
        }

        // Projection rows (days 1-30)
        if (paths.Count > 0)
        {
            var pathMap = paths.ToDictionary(p => p.Percentile, p => p.Values);
            int days = paths[0].Values.Count;
            for (int d = 0; d < days; d++)
            {
                chart.Add(new ProjectionChartRow(
                    Day: d + 1,
                    Actual: null,
                    P10: pathMap.GetValueOrDefault(10)?[d],
                    P25: pathMap.GetValueOrDefault(25)?[d],
                    P50: pathMap.GetValueOrDefault(50)?[d],
                    P75: pathMap.GetValueOrDefault(75)?[d],
                    P90: pathMap.GetValueOrDefault(90)?[d]
                ));
            }
        }

        return chart;
    }
}
