// HTTP client for communicating with the Python FastAPI backend.
// Wraps all /internal/* endpoint calls.

namespace EconViz.Gateway.Services;

public class PythonApiClient
{
    private readonly HttpClient _http;

    public PythonApiClient(HttpClient http)
    {
        _http = http;
    }

    public async Task<List<InstrumentSummary>> GetInstrumentsAsync()
    {
        // Retrieves summary of all instruments
        return await _http.GetFromJsonAsync<List<InstrumentSummary>>("/internal/instruments");
    }

    public async Task<InstrumentDetail>GetInstrumentAsync(string ticker)
    {
        // Retrieves details for 1 ticker
        return await _http.GetFromJsonAsync<InstrumentDetail>($"/internal/instrument/{ticker}");
    }

    public async Task<JsonElement>RefreshAsync()
    {
        // Refreshes summary
        var response = await _http.PostAsync("/internal/refresh", null);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<JsonElement>();
    }

    public async Task<List<PercentilePath>>GetProjectionsAsync(string ticker)
    {
        // Retrieves and parses 30 dayt projection from Monte Carlo 
        var response = await _http.GetFromJsonAsync<List<JsonElement>>($"/internal/intsrument/{ticker}/projections");
        
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
   