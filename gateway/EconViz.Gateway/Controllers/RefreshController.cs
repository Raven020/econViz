// Refresh controller — POST /api/refresh
// Triggers data fetch and HMM retrain via Python backend.
// Pushes completion notification via SignalR.

using Microsoft.AspNetCore.Mvc;

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

    [HttpPost]
    public async Task<IActionResult> Post()
    {
        var result = await _python.RefreshAsync();
        _cache.Invalidate("instruments");
        return Ok(result);
    }

}
