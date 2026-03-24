# Multivariate Monte Carlo simulation engine.
# Takes regime-conditioned mean returns and covariance matrix,
# simulates 10,000 correlated return paths over a 30-day horizon
# using Student's t-distribution for fat tails.
# Produces per-asset projection cones (10/25/50/75/90 percentiles).

import numpy as np
from scipy.stats import t as students_t


def simulate_paths(
    means: np.ndarray,
    covariance: np.ndarray,
    n_paths: int = 10_000,
    horizon: int = 30,
    df: int = 5,
) -> np.ndarray:
    """Simulate correlated multi-asset return paths using Student's t-distribution.

    Generates correlated random draws via Cholesky decomposition of the
    covariance matrix, scaled by Student's t samples for fat tails.
    Each path is a sequence of daily returns over the forward horizon.

    Args:
        means: Array of shape (n_assets,) with regime-conditioned daily
            mean returns per asset.
        covariance: Array of shape (n_assets, n_assets) with regime-conditioned
            covariance matrix.
        n_paths: Number of simulation paths (default 10,000).
        horizon: Number of forward days to simulate (default 30).
        df: Degrees of freedom for Student's t-distribution (default 5).
            Lower values produce fatter tails.

    Returns:
        Array of shape (n_paths, horizon, n_assets) with simulated daily
        return paths.
    """
    n_assets = means.shape[0]
    cholesky_decom = np.linalg.cholesky(covariance)
    z = np.random.standard_normal((n_paths, horizon, n_assets))
    fat_tails = students_t.rvs(df, size=(n_paths, horizon, 1))
    correlated = z @ cholesky_decom.T
    scaled = correlated * fat_tails
    return scaled + means


def returns_to_prices(
    current_prices: np.ndarray, return_paths: np.ndarray
) -> np.ndarray:
    """Convert simulated return paths to price paths starting from current prices.

    Compounds daily returns forward from each asset's current price
    to produce simulated price trajectories.

    Args:
        current_prices: Array of shape (n_assets,) with today's prices.
        return_paths: Array of shape (n_paths, horizon, n_assets) with
            simulated daily returns from simulate_paths.

    Returns:
        Array of shape (n_paths, horizon, n_assets) with simulated price
        levels at each day.
    """
    price_paths = current_prices * np.cumprod(1 + return_paths, axis=1)
    return price_paths


def compute_percentiles(
    price_paths: np.ndarray,
    percentiles: list[int] = [10, 25, 50, 75, 90],
) -> dict[int, np.ndarray]:
    """Compute projection cone percentiles from simulated price paths.

    Calculates the specified percentiles across all simulation paths
    at each time step, producing the bands for the projection cone.

    Args:
        price_paths: Array of shape (n_paths, horizon, n_assets) with
            simulated price paths from returns_to_prices.
        percentiles: List of percentile values to compute (default
            [10, 25, 50, 75, 90]).

    Returns:
        Dict mapping each percentile int to an array of shape
        (horizon, n_assets) with that percentile's value at each day.
    """
    results = np.percentile(price_paths, percentiles, axis=0)
    return {p: results[i] for i, p in enumerate(percentiles)}


def compute_tail_risk(
    price_paths: np.ndarray, current_prices: np.ndarray
) -> dict[str, np.ndarray]:
    """Compute tail risk metrics from simulated price paths.

    Calculates Value-at-Risk (VaR) and Expected Shortfall (CVaR) at the
    5th percentile for each asset over the simulation horizon.

    Args:
        price_paths: Array of shape (n_paths, horizon, n_assets) with
            simulated price paths.
        current_prices: Array of shape (n_assets,) with today's prices,
            used to express risk as percentage drawdown.

    Returns:
        Dict with:
            - "var_5": Array of shape (n_assets,) with 5th percentile
              max drawdown per asset (Value-at-Risk).
            - "cvar_5": Array of shape (n_assets,) with mean drawdown
              below the 5th percentile per asset (Expected Shortfall).
    """ 
    n_assets = current_prices.shape[0] 
    terminal_prices = price_paths[:, -1, :]  # shape (n_paths, n_assets)
    drawdowns = (terminal_prices - current_prices) / current_prices
    #Then compute VaR at the 5th percentile:
    var_5 = np.percentile(drawdowns, 5, axis=0) 
    #And CVaR (mean of everything below that threshold):
    cvar_5 = np.zeros(n_assets)
    for i in range(n_assets):
        mask = drawdowns[:, i] <= var_5[i]
        cvar_5[i] = np.mean(drawdowns[mask, i])

    return {"var_5": var_5, "cvar_5": cvar_5}
