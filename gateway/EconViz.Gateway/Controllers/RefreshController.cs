// Refresh controller — POST /api/refresh
// Triggers data fetch and HMM retrain via Python backend.
// Pushes completion notification via SignalR.

using Microsoft.AspNetCore.Mvc;
using EconViz.Gateway.Services;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RefreshController : ControllerBase
{
    private readonly PythonApiClient _python;
    private readonly CacheService _cache;

    public RefreshController(PythonApiClient python, CacheService cache)
    {
        _python = python;
        _cache = cache;
    }

    /// <summary>
    /// POST /api/refresh — triggers full data pipeline refresh.
    /// Calls Python backend to fetch prices, retrain HMM, run Monte Carlo.
    /// Invalidates the instruments cache so next request gets fresh data.
    /// </summary>
    /// <returns>200 OK with status and regime info from Python</returns>
    [HttpPost]
    public async Task<IActionResult> Post()
    {
        var result = await _python.RefreshAsync();
        _cache.Invalidate("instruments");

        // Pre-warm cache: fetch instruments, then pre-fetch detail + projections for each
        var instruments = await _cache.GetOrSetAsync("instruments",
            () => _python.GetInstrumentsAsync());

        foreach (var inst in instruments)
        {
            await _cache.GetOrSetAsync($"instrument_{inst.Ticker}",
                () => _python.GetInstrumentAsync(inst.Ticker));
            await _cache.GetOrSetAsync($"projections_{inst.Ticker}",
                () => _python.GetProjectionsAsync(inst.Ticker), isProjection: true);
        }

        return Ok(result);
    }
}
