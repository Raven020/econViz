// Regime controller — GET /api/regime
// Returns current regime classification, confidence, and transition matrix.

using Microsoft.AspNetCore.Mvc;

namespace EconViz.Gateway.Controllers;

using EconViz.Gateway.Services;
[ApiController]
[Route("api/[controller]")]
public class RegimeController : ControllerBase
{
    public RegimeController(PythonApiClient python, CacheService cache)
    {
        _python = python;
        _cache = cache;
    }

    [HttpGet]
    public async Task<IActionResult> Get()
    {
        // grabs the first instrument from dashbaord list
        //  fetches its ddetail and returns
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
