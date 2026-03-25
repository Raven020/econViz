// Instrument controller — GET /api/instrument/{ticker}
// Proxies and caches instrument detail, chart data, and projections.

using Microsoft.AspNetCore.Mvc;
using EconViz.Gateway.Services;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class InstrumentController : ControllerBase
{
    private readonly PythonApiClient _python;
    private readonly CacheService _cache;

    public InstrumentController(PythonApiClient python, CacheService cache)
    {
        _python = python;
        _cache = cache;
    }

    /// <summary>
    /// GET /api/instrument/{ticker} — returns full instrument detail with OHLCV history and regime.
    /// Caches with the price TTL (60s) using key "instrument_{ticker}".
    /// </summary>
    /// <param name="ticker">Instrument identifier (e.g. "SPY")</param>
    /// <returns>200 OK with InstrumentDetail, or 404 if not found</returns>
    [HttpGet("{ticker}")]
    public async Task<IActionResult> GetDetail(string ticker)
    {
        // retrieves Details for a ticker
        var data = await _cache.GetOrSetAsync($"instrument_{ticker}",
            () => _python.GetInstrumentAsync(ticker));
        if (data == null) return NotFound();
        return Ok(data);
    }

    /// <summary>
    /// GET /api/instrument/{ticker}/chart — returns just the OHLCV history for charting.
    /// Reuses the instrument detail cache, returns only the History property.
    /// </summary>
    /// <param name="ticker">Instrument identifier (e.g. "SPY")</param>
    /// <returns>200 OK with List of ChartDataPoint, or 404 if not found</returns>
    [HttpGet("{ticker}/chart")]
    public async Task<IActionResult> GetChart(string ticker)
    {
        // retrieves chart for a ticker
        var data = await _cache.GetOrSetAsync($"chart_{ticker}",
            () => _python.GetInstrumentAsync(ticker));

        if (data == null) return NotFound();
        return Ok(data.History);
    }

    /// <summary>
    /// GET /api/instrument/{ticker}/projections — returns Monte Carlo projection cone.
    /// Caches with the projection TTL (300s) using key "projections_{ticker}".
    /// </summary>
    /// <param name="ticker">Instrument identifier (e.g. "SPY")</param>
    /// <returns>200 OK with List of PercentilePath, or 404 if not found</returns>
    [HttpGet("{ticker}/projections")]
    public async Task<IActionResult> GetProjection(string ticker)
    {
        // retrieves projection for ticker
        var data = await _cache.GetOrSetAsync($"projections_{ticker}",
            () => _python.GetProjectionsAsync(ticker), isProjection: true);

        if (data == null) return NotFound();
        return Ok(data);
    }
}
