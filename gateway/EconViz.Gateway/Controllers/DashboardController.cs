// Dashboard controller — GET /api/dashboard
// Aggregates instrument prices, daily changes, and regime info
// from the Python backend into a single response.

using Microsoft.AspNetCore.Mvc;

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

      [HttpGet]
      public async Task<IActionResult> Get()
      {
        // retrieves dashboard data
          var data = await _cache.GetOrSetAsync("instruments",
              () => _python.GetInstrumentsAsync());
          return Ok(data);
      }
}
