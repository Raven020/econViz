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
}
