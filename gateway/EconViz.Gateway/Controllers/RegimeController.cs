// Regime controller — GET /api/regime
// Returns current regime classification, confidence, and transition matrix.

using Microsoft.AspNetCore.Mvc;
using EconViz.Gateway.Services;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RegimeController : ControllerBase
{
    private readonly PythonApiClient _python;
    private readonly CacheService _cache;

    public RegimeController(PythonApiClient python, CacheService cache)
    {
        _python = python;
        _cache = cache;
    }

    /// <summary>
    /// GET /api/regime — returns the current macro regime.
    /// Fetches the first instrument's detail and extracts the Regime field.
    /// Regime is global (not per-instrument) so any ticker works.
    /// </summary>
    /// <returns>200 OK with RegimeResponse, or 404 if no instruments or regime data</returns>
    [HttpGet]
    public async Task<IActionResult> Get()
    {
        // grabs the first instrument from dashboard list
        // fetches its detail and returns the regime
        var instruments = await _cache.GetOrSetAsync("instruments",
            () => _python.GetInstrumentsAsync());

        if (instruments == null || instruments.Count == 0)
            return NotFound();

        var detail = await _cache.GetOrSetAsync($"instrument_{instruments[0].Ticker}",
            () => _python.GetInstrumentAsync(instruments[0].Ticker));

        if (detail?.Regime == null) return NotFound();
        return Ok(detail.Regime);
    }
}
