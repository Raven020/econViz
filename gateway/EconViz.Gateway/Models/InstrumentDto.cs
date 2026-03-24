// DTOs for instrument detail and chart responses.

namespace EconViz.Gateway.Models;

public record InstrumentDetail(
    string Ticker,
    double Close,
    double Change,
    double ChangePct,
    double High,
    double Low,
    long Volume,
    List<ChartDataPoint> History,
    RegimeResponse? Regime
);