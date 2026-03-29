// SignalR hub for real-time market data push.
// Events: MarketDataUpdated, RegimeChanged, RefreshProgress

using Microsoft.AspNetCore.SignalR;

namespace EconViz.Gateway.Hubs;

public class MarketHub : Hub
{
    /// <summary>
    /// Pushes updated instrument prices to all connected clients.
    /// Called by RefreshScheduler after a successful data refresh.
    /// </summary>
    /// <param name="data">Serialized instrument summary JSON to broadcast</param>
    /// <returns>Task</returns>
    public async Task SendMarketDataUpdated(object data)
    {
        // TODO: call Clients.All.SendAsync("MarketDataUpdated", data)
        await Clients.All.SendAsync("MarketDataUpdated", data);
    }

    /// <summary>
    /// Pushes a regime change notification to all connected clients.
    /// Called when the HMM detects a different regime than the previous run.
    /// </summary>
    /// <param name="regime">Serialized regime response JSON to broadcast</param>
    /// <returns>Task</returns>
    public async Task SendRegimeChanged(object regime)
    {
        await Clients.All.SendAsync("RegimeChanged", regime);
    }

    /// <summary>
    /// Pushes refresh progress updates to all connected clients.
    /// Called during a refresh to indicate current step (e.g. "Fetching prices", "Training HMM").
    /// </summary>
    /// <param name="message">Progress message string</param>
    /// <returns>Task</returns>
    public async Task SendRefreshProgress(string message)
    {
        await Clients.All.SendAsync("RefreshProgress", message);
    }
}
