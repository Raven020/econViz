// DTOs for regime endpoint response.

using System.Text.Json.Serialization;

namespace EconViz.Gateway.Models;

/// <summary>
/// Current macro regime classification from the HMM model.
/// Fields map to the regime object in Python's instrument detail response.
/// </summary>
/// <param name="Label">Regime name: "Bull", "Bear", "Stagnation", "Stagflation", or "Crisis"</param>
/// <param name="Confidence">Posterior probability of being in this regime (0.0 to 1.0)</param>
/// <param name="TransitionMatrix">5x5 matrix of 30-day transition probabilities between regimes</param>
public record RegimeResponse(
    string Label,
    double Confidence,
    [property: JsonPropertyName("transition_matrix")] List<List<double>> TransitionMatrix
);
