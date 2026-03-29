import numpy as np
import pytest

from backend.models.hmm import build_feature_matrix, train_hmm, decode_regime, get_transition_matrix


class TestBuildFeatureMatrix:
    def test_shape(self):
        returns = np.random.randn(100, 3)
        macro = np.random.randn(100, 2)
        result = build_feature_matrix(returns, macro)
        assert result.shape == (100, 5)

    def test_combines_columns(self):
        returns = np.ones((10, 2))
        macro = np.zeros((10, 1))
        result = build_feature_matrix(returns, macro)
        assert result[0, 0] == 1.0
        assert result[0, 2] == 0.0


class TestTrainHmm:
    def test_fits_without_error(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=2, n_iter=10)
        assert model is not None

    def test_n_states(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10)
        assert model.n_components == 3

    def test_custom_random_state(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10, random_state=99)
        assert model is not None

    def test_reproducibility_with_same_seed(self):
        features = np.random.RandomState(0).randn(200, 3)
        model1 = train_hmm(features, n_states=3, n_iter=10, random_state=42)
        model2 = train_hmm(features, n_states=3, n_iter=10, random_state=42)
        state1, _ = decode_regime(model1, features)
        state2, _ = decode_regime(model2, features)
        assert state1 == state2


class TestDecodeRegime:
    def test_returns_valid_state(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10)
        state, probs = decode_regime(model, features)
        assert 0 <= state < 3

    def test_probs_sum_to_one(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10)
        _, probs = decode_regime(model, features)
        np.testing.assert_allclose(probs.sum(), 1.0, atol=1e-6)

    def test_probs_shape(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=4, n_iter=10)
        _, probs = decode_regime(model, features)
        assert probs.shape == (4,)

    def test_empty_features_raises_valueerror(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10)

        empty = np.empty((0, 3))
        with pytest.raises(ValueError, match="empty feature matrix"):
            decode_regime(model, empty)

    def test_single_observation(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10)

        single = np.random.randn(1, 3)
        state, probs = decode_regime(model, single)
        assert 0 <= state < 3
        np.testing.assert_allclose(probs.sum(), 1.0, atol=1e-6)


class TestGetTransitionMatrix:
    def test_shape(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10)
        matrix = get_transition_matrix(model)
        assert matrix.shape == (3, 3)

    def test_rows_sum_to_one(self):
        np.random.seed(42)
        features = np.random.randn(200, 3)
        model = train_hmm(features, n_states=3, n_iter=10)
        matrix = get_transition_matrix(model)
        for row in matrix:
            np.testing.assert_allclose(row.sum(), 1.0, atol=1e-6)
