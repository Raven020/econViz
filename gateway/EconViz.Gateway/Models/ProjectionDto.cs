// DTOs for Monte Carlo projection endpoint response.

namespace EconViz.Gateway.Models;

/// <summary>
/// One percentile band of the Monte Carlo projection cone.
/// Constructed in PythonApiClient by flattening day_1..day_30 into a list.
/// </summary>
/// <param name="Percentile">Percentile level (10, 25, 50, 75, or 90)</param>
/// <param name="Values">List of 30 projected prices, one per forward day</param>
public record PercentilePath(
    int Percentile,
    List<double> Values
);
