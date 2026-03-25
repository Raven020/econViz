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
        // TODO: loop while !stoppingToken.IsCancellationRequested
        // TODO: await Task.Delay(_interval, stoppingToken) to wait between runs
        // TODO: create a scope via _scopeFactory.CreateScope()
        // TODO: resolve PythonApiClient from the scope
        // TODO: call RefreshAsync()
        // TODO: push "MarketDataUpdated" via _hub.Clients.All.SendAsync()
        // TODO: wrap in try/catch to prevent crashes from killing the background service
        throw new NotImplementedException();
    }
}
