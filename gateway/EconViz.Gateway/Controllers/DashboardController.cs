// Dashboard controller — GET /api/dashboard
// Aggregates instrument prices, daily changes, and regime info
// from the Python backend into a single response.

using Microsoft.AspNetCore.Mvc;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DashboardController : ControllerBase
{
    // TODO: inject PythonApiClient, CacheService
    // TODO: implement GET /api/dashboard
}
