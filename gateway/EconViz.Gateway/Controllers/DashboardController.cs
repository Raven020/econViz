// Dashboard controller — GET /api/dashboard, GET /api/dashboard/macro
// Aggregates instrument prices and macro indicators from the Python backend.

using Microsoft.AspNetCore.Mvc;
using EconViz.Gateway.Services;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DashboardController : ControllerBase
{
    private readonly PythonApiClient _python;
    private readonly CacheService _cache;

    public DashboardController(PythonApiClient python, CacheService cache)
    {
        _python = python;
        _cache = cache;
    }

    /// <summary>
    /// GET /api/dashboard — returns all instruments with prices, changes, and sparklines.
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> Get()
    {
        var data = await _cache.GetOrSetAsync("instruments",
            () => _python.GetInstrumentsAsync());
        return Ok(data);
    }

    /// <summary>
    /// GET /api/dashboard/macro — returns macro indicator summaries with sparklines.
    /// </summary>
    [HttpGet("macro")]
    public async Task<IActionResult> GetMacro()
    {
        var data = await _cache.GetOrSetAsync("macro",
            () => _python.GetMacroAsync());
        return Ok(data);
    }
}
