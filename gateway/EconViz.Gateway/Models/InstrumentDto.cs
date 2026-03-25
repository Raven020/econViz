// DTOs for instrument detail and chart responses.

using System.Text.Json.Serialization;

namespace EconViz.Gateway.Models;

/// <summary>
/// Single OHLCV data point for chart rendering.
/// Fields map to each row in the "history" array from Python GET /internal/instrument/{ticker}.
/// </summary>
/// <param name="Date">Trading date</param>
/// <param name="Open">Opening price</param>
/// <param name="High">Day's high price</param>
/// <param name="Low">Day's low price</param>
/// <param name="Close">Closing price</param>
/// <param name="Volume">Trading volume</param>
public record ChartDataPoint(
    string Date,
    double Open,
    double High,
    double Low,
    double Close,
    long Volume
);

/// <summary>
/// Full instrument detail for the drilldown view.
/// Fields map to the JSON returned by Python GET /internal/instrument/{ticker}.
/// </summary>
/// <param name="Ticker">Instrument identifier (e.g. "SPY")</param>
/// <param name="Close">Most recent closing price</param>
/// <param name="Change">Absolute price change from previous close</param>
/// <param name="ChangePct">Percentage price change from previous close</param>
/// <param name="High">Day's high price</param>
/// <param name="Low">Day's low price</param>
/// <param name="Volume">Trading volume</param>
/// <param name="History">Full OHLCV history as a list of ChartDataPoints</param>
/// <param name="Regime">Current regime classification, or null if no regime data exists</param>
public record InstrumentDetail(
    string Ticker,
    double Close,
    double Change,
    [property: JsonPropertyName("change_pct")] double ChangePct,
    double High,
    double Low,
    long Volume,
    List<ChartDataPoint> History,
    RegimeResponse? Regime
);
