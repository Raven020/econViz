import numpy as np
import pytest

from backend.models.montecarlo import (
    compute_percentiles,
    compute_tail_risk,
    returns_to_prices,
    simulate_paths,
)


class TestSimulatePaths:
    def test_output_shape(self):
        means = np.array([0.001, 0.002])
        cov = np.array([[0.0004, 0.0001], [0.0001, 0.0009]])
        result = simulate_paths(means, cov, n_paths=100, horizon=10)
        assert result.shape == (100, 10, 2)

    def test_single_asset(self):
        means = np.array([0.0])
        cov = np.array([[0.0001]])
        result = simulate_paths(means, cov, n_paths=50, horizon=5)
        assert result.shape == (50, 5, 1)

    def test_returns_are_finite(self):
        means = np.array([0.001, -0.001, 0.0])
        cov = np.eye(3) * 0.0004
        result = simulate_paths(means, cov, n_paths=200, horizon=30)
        assert np.all(np.isfinite(result))

    def test_mean_direction(self):
        means = np.array([0.05])
        cov = np.array([[0.0001]])
        result = simulate_paths(means, cov, n_paths=5000, horizon=1)
        assert result.mean() > 0

    def test_semi_definite_matrix_does_not_crash(self):
        """Cholesky should not crash on a near-singular covariance matrix."""
        means = np.array([0.001, 0.001])
        # Singular matrix (rows are identical) - would fail without ridge
        cov = np.array([[0.0004, 0.0004], [0.0004, 0.0004]])
        result = simulate_paths(means, cov, n_paths=10, horizon=5)
        assert result.shape == (10, 5, 2)
        assert np.all(np.isfinite(result))


class TestReturnsToPrices:
    def test_output_shape(self):
        prices = np.array([100.0, 200.0])
        returns = np.zeros((10, 5, 2))
        result = returns_to_prices(prices, returns)
        assert result.shape == (10, 5, 2)

    def test_zero_returns_give_current_price(self):
        prices = np.array([100.0])
        returns = np.zeros((1, 5, 1))
        result = returns_to_prices(prices, returns)
        np.testing.assert_allclose(result, 100.0)

    def test_positive_return_increases_price(self):
        prices = np.array([100.0])
        returns = np.array([[[0.10]]])  # 10% return
        result = returns_to_prices(prices, returns)
        np.testing.assert_allclose(result[0, 0, 0], 110.0)

    def test_compounding(self):
        prices = np.array([100.0])
        returns = np.array([[[0.10], [0.10]]])  # 10% each day
        result = returns_to_prices(prices, returns)
        np.testing.assert_allclose(result[0, 0, 0], 110.0)
        np.testing.assert_allclose(result[0, 1, 0], 121.0)


class TestComputePercentiles:
    def test_returns_correct_keys(self):
        paths = np.random.randn(100, 5, 2)
        result = compute_percentiles(paths)
        assert set(result.keys()) == {10, 25, 50, 75, 90}

    def test_custom_percentiles(self):
        paths = np.random.randn(100, 5, 2)
        result = compute_percentiles(paths, percentiles=[5, 95])
        assert set(result.keys()) == {5, 95}

    def test_output_shapes(self):
        paths = np.random.randn(100, 5, 2)
        result = compute_percentiles(paths)
        for p, arr in result.items():
            assert arr.shape == (5, 2)

    def test_ordering(self):
        paths = np.random.randn(1000, 10, 1)
        result = compute_percentiles(paths)
        for day in range(10):
            assert result[10][day, 0] <= result[50][day, 0] <= result[90][day, 0]


class TestComputeTailRisk:
    def test_output_keys(self):
        paths = np.random.randn(1000, 5, 2) + 100
        prices = np.array([100.0, 100.0])
        result = compute_tail_risk(paths, prices)
        assert "var_5" in result
        assert "cvar_5" in result

    def test_output_shapes(self):
        paths = np.random.randn(1000, 5, 3) + 100
        prices = np.array([100.0, 100.0, 100.0])
        result = compute_tail_risk(paths, prices)
        assert result["var_5"].shape == (3,)
        assert result["cvar_5"].shape == (3,)

    def test_cvar_worse_than_var(self):
        np.random.seed(42)
        paths = np.random.randn(5000, 5, 2) * 10 + 100
        prices = np.array([100.0, 100.0])
        result = compute_tail_risk(paths, prices)
        for i in range(2):
            assert result["cvar_5"][i] <= result["var_5"][i]
