# Regime definitions and parameter extraction.
# Defines the 5 regimes (Bull, Bear, Stagnation, Stagflation, Crisis).
# Extracts regime-conditioned mean return vectors and covariance matrices
# from HMM output to feed into Monte Carlo simulation.

import numpy as np
from hmmlearn.hmm import GaussianHMM

REGIMES = {
    0: "Bull",
    1: "Bear",
    2: "Stagnation",
    3: "Stagflation",
    4: "Crisis",
}


def label_regime(state: int) -> str:
    """Map a numeric state index to its human-readable regime name.

    Args:
        state: Integer regime index (0-4) from HMM decode.

    Returns:
        Regime name string (e.g. "Bull", "Crisis").
    """
    pass


def extract_regime_params(model: GaussianHMM, state: int) -> tuple[np.ndarray, np.ndarray]:
    """Extract the mean return vector and covariance matrix for a given regime.

    Pulls the regime-specific Gaussian parameters directly from the
    trained HMM model for the specified state.

    Args:
        model: Trained GaussianHMM instance containing fitted means_ and covars_.
        state: Integer regime index (0-4) to extract parameters for.

    Returns:
        Tuple of:
            - means: Array of shape (n_features,) with regime-conditioned
              mean returns per asset/indicator.
            - covariance: Array of shape (n_features, n_features) with
              regime-conditioned covariance matrix.
    """
    pass


def blend_regime_params(
    model: GaussianHMM, state_probs: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Compute confidence-weighted mean returns and covariance across all regimes.

    Instead of using only the most likely regime, blends parameters from
    all regimes weighted by their posterior probabilities. This produces
    smoother estimates when the model is uncertain between states.

    Args:
        model: Trained GaussianHMM instance.
        state_probs: Array of shape (n_states,) with posterior probabilities
            for each regime (from decode_regime).

    Returns:
        Tuple of:
            - blended_means: Array of shape (n_features,) with probability-weighted
              mean returns.
            - blended_covariance: Array of shape (n_features, n_features) with
              probability-weighted covariance matrix.
    """
    pass
