// Refresh controller — POST /api/refresh
// Triggers data fetch and HMM retrain via Python backend.
// Pushes completion notification via SignalR.

using Microsoft.AspNetCore.Mvc;

namespace EconViz.Gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RefreshController : ControllerBase
{
    // TODO: inject PythonApiClient, CacheService, IHubContext<MarketHub>
    // TODO: implement POST /api/refresh
}
