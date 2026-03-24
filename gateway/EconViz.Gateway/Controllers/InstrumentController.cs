// Instrument controller — GET /api/instrument/{ticker}
// Proxies and caches instrument detail, chart data, and projections.

using Microsoft.AspNetCore.Mvc;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class InstrumentController : ControllerBase
{
    // TODO: inject PythonApiClient, CacheService
    // TODO: implement GET /api/instrument/{ticker}
    // TODO: implement GET /api/instrument/{ticker}/chart
    // TODO: implement GET /api/instrument/{ticker}/projections
}
