// Regime controller — GET /api/regime
// Returns current regime classification, confidence, and transition matrix.

using Microsoft.AspNetCore.Mvc;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RegimeController : ControllerBase
{
    // TODO: inject PythonApiClient, CacheService
    // TODO: implement GET /api/regime
}
