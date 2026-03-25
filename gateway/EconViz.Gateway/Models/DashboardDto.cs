// DTOs for the dashboard endpoint response.

using System.Text.Json.Serialization;

namespace EconViz.Gateway.Models;

/// <summary>
/// Single instrument row for the dashboard table.
/// Fields map to the JSON returned by Python GET /internal/instruments.
/// </summary>
/// <param name="Ticker">Instrument identifier (e.g. "SPY", "BTC")</param>
/// <param name="Close">Most recent closing price</param>
/// <param name="Change">Absolute price change from previous close</param>
/// <param name="ChangePct">Percentage price change from previous close</param>
/// <param name="High">Day's high price</param>
/// <param name="Low">Day's low price</param>
/// <param name="Volume">Trading volume</param>
/// <param name="Sparkline">Last 30 closing prices for the sparkline chart</param>
public record InstrumentSummary(
    string Ticker,
    double Close,
    double Change,
    [property: JsonPropertyName("change_pct")] double ChangePct,
    double High,
    double Low,
    long Volume,
    List<double> Sparkline
);
