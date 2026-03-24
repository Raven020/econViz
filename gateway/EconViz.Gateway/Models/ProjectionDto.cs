// DTOs for Monte Carlo projection endpoint response.

namespace EconViz.Gateway.Models;

public record PercentilePath(
    int Percentile,
    List<double> Values
);