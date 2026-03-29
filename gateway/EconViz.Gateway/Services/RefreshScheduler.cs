// Background service for periodic data refresh.
// Triggers refresh, invalidates cache, and notifies clients via SignalR.

using Microsoft.AspNetCore.SignalR;
using EconViz.Gateway.Hubs;

namespace EconViz.Gateway.Services;

public class RefreshScheduler : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly IHubContext<MarketHub> _hub;
    private readonly CacheService _cache;
    private readonly TimeSpan _interval = TimeSpan.FromMinutes(15);

    public RefreshScheduler(IServiceScopeFactory scopeFactory, IHubContext<MarketHub> hub, CacheService cache)
    {
        _scopeFactory = scopeFactory;
        _hub = hub;
        _cache = cache;
    }

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

                // Invalidate and pre-warm cache
                _cache.Invalidate("instruments");
                var instruments = await _cache.GetOrSetAsync("instruments",
                    () => client.GetInstrumentsAsync());

                foreach (var inst in instruments)
                {
                    _cache.Invalidate($"instrument_{inst.Ticker}");
                    _cache.Invalidate($"chart_{inst.Ticker}");
                    _cache.Invalidate($"projections_{inst.Ticker}");
                }

                await _hub.Clients.All.SendAsync("MarketDataUpdated", cancellationToken: stoppingToken);
            }
            catch (Exception)
            {
                // Swallow so one failed refresh doesn't kill the background loop
            }
        }
    }
}
