import numpy as np
import pytest
from unittest.mock import MagicMock

from backend.models.regime import label_regime, extract_regime_params, blend_regime_params


class TestLabelRegime:
    def test_all_labels(self):
        assert label_regime(0) == "Bull"
        assert label_regime(1) == "Bear"
        assert label_regime(2) == "Stagnation"
        assert label_regime(3) == "Stagflation"
        assert label_regime(4) == "Crisis"

    def test_unknown_state_returns_fallback(self):
        result = label_regime(5)
        assert "Unknown" in result
        assert "5" in result

    def test_negative_state_returns_fallback(self):
        result = label_regime(-1)
        assert "Unknown" in result


class TestExtractRegimeParams:
    def test_returns_correct_state(self):
        model = MagicMock()
        model.means_ = np.array([[0.01, 0.02], [0.03, 0.04], [-0.01, -0.02], [0.0, 0.0], [-0.05, -0.05]])
        model.covars_ = np.array([np.eye(2) * i for i in range(1, 6)])

        means, cov = extract_regime_params(model, 1)
        np.testing.assert_array_equal(means, np.array([0.03, 0.04]))
        np.testing.assert_array_equal(cov, np.eye(2) * 2)


class TestBlendRegimeParams:
    def test_uniform_probs_give_average(self):
        model = MagicMock()
        model.means_ = np.array([[1.0], [3.0]])
        model.covars_ = np.array([[[2.0]], [[4.0]]])

        probs = np.array([0.5, 0.5])
        means, cov = blend_regime_params(model, probs)
        np.testing.assert_allclose(means, [2.0])
        np.testing.assert_allclose(cov, [[3.0]])

    def test_single_state_dominant(self):
        model = MagicMock()
        model.means_ = np.array([[10.0], [0.0]])
        model.covars_ = np.array([[[5.0]], [[1.0]]])

        probs = np.array([1.0, 0.0])
        means, cov = blend_regime_params(model, probs)
        np.testing.assert_allclose(means, [10.0])
        np.testing.assert_allclose(cov, [[5.0]])

    def test_probabilities_sum_to_one(self):
        model = MagicMock()
        model.means_ = np.array([[1.0], [2.0], [3.0]])
        model.covars_ = np.array([[[1.0]], [[2.0]], [[3.0]]])

        probs = np.array([0.2, 0.3, 0.5])
        means, cov = blend_regime_params(model, probs)
        expected_mean = 0.2 * 1.0 + 0.3 * 2.0 + 0.5 * 3.0
        np.testing.assert_allclose(means, [expected_mean])
