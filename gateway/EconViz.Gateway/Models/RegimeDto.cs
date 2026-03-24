// DTOs for regime endpoint response.

namespace EconViz.Gateway.Models;

public record RegimeResponse(
    string Label,
    double Confidence,
    List<List<double>> TransitionMatrix
);