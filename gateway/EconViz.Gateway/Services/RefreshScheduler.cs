// Background service for optional periodic data refresh.
// Implements IHostedService to trigger refresh on a configurable interval.

using Microsoft.AspNetCore.SignalR;
using EconViz.Gateway.Hubs;

namespace EconViz.Gateway.Services;

public class RefreshScheduler : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly IHubContext<MarketHub> _hub;
    private readonly TimeSpan _interval = TimeSpan.FromMinutes(15);

    /// <summary>
    /// Constructor — receives DI services for creating scoped PythonApiClient instances
    /// and the SignalR hub context for broadcasting updates.
    /// Uses IServiceScopeFactory because BackgroundService is a singleton
    /// but PythonApiClient is scoped (tied to HttpClient lifetime).
    /// </summary>
    /// <param name="scopeFactory">Factory for creating DI scopes to resolve PythonApiClient</param>
    /// <param name="hub">SignalR hub context for pushing updates to connected clients</param>
    public RefreshScheduler(IServiceScopeFactory scopeFactory, IHubContext<MarketHub> hub)
    {
        _scopeFactory = scopeFactory;
        _hub = hub;
    }

    /// <summary>
    /// Main loop — runs every 15 minutes until the app shuts down.
    /// Each iteration: calls PythonApiClient.RefreshAsync(), then pushes
    /// a "MarketDataUpdated" event via SignalR to notify connected frontends.
    /// </summary>
    /// <param name="stoppingToken">Cancellation token triggered on app shutdown</param>
    /// <returns>Task that runs for the lifetime of the application</returns>
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(_interval, stoppingToken);

            try
            {
                using var scope = _scopeFactory.CreateScope();
                var client = scope.ServiceProvider.GetRequiredService<PythonApiClient>();
                await client.RefreshAsync();
                await _hub.Clients.All.SendAsync("MarketDataUpdated", cancellationToken: stoppingToken);
            }
            catch (Exception)
            {
                // Swallow so one failed refresh doesn't kill the background loop
            }
        }
    }
}
