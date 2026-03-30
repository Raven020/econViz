// DTOs for Monte Carlo projection endpoint responses.

namespace EconViz.Gateway.Models;

/// <summary>
/// One percentile band of the Monte Carlo projection cone (internal use).
/// </summary>
public record PercentilePath(
    int Percentile,
    List<double> Values
);

/// <summary>
/// Pre-shaped chart row for the projection cone — one row per day.
/// Ready to pass directly to Recharts on the frontend.
/// </summary>
public record ProjectionChartRow(
    int Day,
    double? Actual,
    double? P10,
    double? P25,
    double? P50,
    double? P75,
    double? P90
);
