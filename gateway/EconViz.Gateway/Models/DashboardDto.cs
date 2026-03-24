// DTOs for the dashboard endpoint response.

namespace EconViz.Gateway.Models;

public record InstrumentSummary(
    string Ticker,
    double Close,
    double Change,
    double ChangePct,
    double High,
    double Low,
    long Volume,
    List<double> Sparkline
);