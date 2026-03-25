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

    [HttpGet("{ticker}")]
    public async Task<IActionResult> GetDetail(string ticker)
    {
        // retrieves Details for a ticker
        var data = await _cache.GetOrSetAsync($"instrument_{ticker}",
            () => _python.GetInstrumentAsync(ticker));
        if (data == null) return NotFound();
        return Ok(data);
    }
    [HttpGet("{ticker}/chart")]
    public async Task<IActionResult> GetChart(string ticker)
    {
        // retrieves chart for a ticker
        var data = await _cache.GetOrSetAsync($"chart_{ticker}",
        () => _python.GetInstrumentAsync(ticker));

        if (data == null) return NotFound();
        return Ok(data.History);
    }

    [HttpGet("{ticker}/projections")]

    public async Task<IActionResult> GetProjection(string ticker)
    {
        // retrieves projection for ticker
        var data = await _cache.GetOrSetAsync($"projections_{ticker}",
        () => _python.GetProjectionsAsync(ticker), isProjection: true);

        if(data == null) return NotFound();
        return Ok(data);
    }

}
