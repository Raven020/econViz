// DTOs for the dashboard endpoint response.

using System.Text.Json.Serialization;

namespace EconViz.Gateway.Models;

/// <summary>
/// Single instrument row for the dashboard table.
/// </summary>
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

/// <summary>
/// Single macro indicator row for the dashboard.
/// </summary>
public record MacroSummary(
    string Indicator,
    double Value,
    double Change,
    [property: JsonPropertyName("change_pct")] double ChangePct,
    string Date,
    List<double> Sparkline
);
