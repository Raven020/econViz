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
    /// Invalidates all caches, then pre-warms with fresh data.
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> Post()
    {
        var result = await _python.RefreshAsync();

        // Invalidate dashboard cache
        _cache.Invalidate("instruments");

        // Pre-warm dashboard and get instrument list
        var instruments = await _cache.GetOrSetAsync("instruments",
            () => _python.GetInstrumentsAsync());

        // Invalidate and pre-warm per-instrument caches
        foreach (var inst in instruments)
        {
            _cache.Invalidate($"instrument_{inst.Ticker}");
            _cache.Invalidate($"chart_{inst.Ticker}");
            _cache.Invalidate($"projections_{inst.Ticker}");

            await _cache.GetOrSetAsync($"instrument_{inst.Ticker}",
                () => _python.GetInstrumentAsync(inst.Ticker));
            await _cache.GetOrSetAsync($"projections_{inst.Ticker}",
                () => _python.GetProjectionsAsync(inst.Ticker), isProjection: true);
        }

        return Ok(result);
    }
}
