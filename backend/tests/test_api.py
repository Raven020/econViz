from datetime import date
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _mock_conn():
    return MagicMock()


def _sample_latest_prices():
    return pd.DataFrame({
        "instrument": ["SPY", "BTC"],
        "close": [450.0, 60000.0],
        "change": [2.5, -500.0],
        "change_pct": [0.56, -0.83],
        "high": [451.0, 61000.0],
        "low": [448.0, 59000.0],
        "volume": [65000000, 1200000],
    })


def _sample_history():
    dates = [date(2024, 1, i) for i in range(1, 31)]
    return pd.DataFrame({
        "date": dates,
        "open": [100.0 + i for i in range(30)],
        "high": [101.0 + i for i in range(30)],
        "low": [99.0 + i for i in range(30)],
        "close": [100.5 + i for i in range(30)],
        "volume": [1000 + i * 10 for i in range(30)],
    })


class TestDashboardRoute:
    @patch("backend.api.routes_dashboard.read_price_history")
    @patch("backend.api.routes_dashboard.read_latest_prices")
    @patch("backend.api.routes_dashboard.init_db")
    def test_get_instruments(self, mock_init, mock_latest, mock_history):
        mock_init.return_value = _mock_conn()
        mock_latest.return_value = _sample_latest_prices()
        mock_history.return_value = _sample_history()

        response = client.get("/internal/instruments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["ticker"] == "SPY"
        assert "sparkline" in data[0]
        assert "close" in data[0]
        assert "change_pct" in data[0]

    @patch("backend.api.routes_dashboard.read_price_history")
    @patch("backend.api.routes_dashboard.read_latest_prices")
    @patch("backend.api.routes_dashboard.init_db")
    def test_empty_instruments(self, mock_init, mock_latest, mock_history):
        mock_init.return_value = _mock_conn()
        mock_latest.return_value = pd.DataFrame(columns=["instrument", "close", "change", "change_pct", "high", "low", "volume"])

        response = client.get("/internal/instruments")
        assert response.status_code == 200
        assert response.json() == []


class TestDrilldownRoute:
    @patch("backend.api.routes_drilldown.read_regime")
    @patch("backend.api.routes_drilldown.read_price_history")
    @patch("backend.api.routes_drilldown.read_latest_prices")
    @patch("backend.api.routes_drilldown.init_db")
    def test_get_instrument(self, mock_init, mock_latest, mock_history, mock_regime):
        mock_init.return_value = _mock_conn()
        mock_latest.return_value = _sample_latest_prices()
        mock_history.return_value = _sample_history()
        mock_regime.return_value = ("Bull", 0.85, np.eye(5))

        response = client.get("/internal/instrument/SPY")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "SPY"
        assert data["close"] == 450.0
        assert len(data["history"]) == 30
        assert data["regime"]["label"] == "Bull"

    @patch("backend.api.routes_drilldown.read_latest_prices")
    @patch("backend.api.routes_drilldown.init_db")
    def test_instrument_not_found(self, mock_init, mock_latest):
        mock_init.return_value = _mock_conn()
        mock_latest.return_value = _sample_latest_prices()

        response = client.get("/internal/instrument/FAKE")
        assert response.status_code == 404

    @patch("backend.api.routes_drilldown.read_regime")
    @patch("backend.api.routes_drilldown.read_price_history")
    @patch("backend.api.routes_drilldown.read_latest_prices")
    @patch("backend.api.routes_drilldown.init_db")
    def test_no_regime(self, mock_init, mock_latest, mock_history, mock_regime):
        mock_init.return_value = _mock_conn()
        mock_latest.return_value = _sample_latest_prices()
        mock_history.return_value = _sample_history()
        mock_regime.return_value = None

        response = client.get("/internal/instrument/SPY")
        assert response.status_code == 200
        assert response.json()["regime"] is None


class TestProjectionsRoute:
    @patch("backend.api.routes_montecarlo.read_montecarlo")
    @patch("backend.api.routes_montecarlo.init_db")
    def test_get_projections(self, mock_init, mock_mc):
        mock_init.return_value = _mock_conn()
        mock_mc.return_value = pd.DataFrame({
            "percentile": [10, 50, 90],
            **{f"day_{i}": [100.0 + i, 110.0 + i, 120.0 + i] for i in range(1, 31)},
        })

        response = client.get("/internal/instrument/SPY/projections")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["percentile"] == 10

    @patch("backend.api.routes_montecarlo.read_montecarlo")
    @patch("backend.api.routes_montecarlo.init_db")
    def test_projections_not_found(self, mock_init, mock_mc):
        mock_init.return_value = _mock_conn()
        mock_mc.return_value = None

        response = client.get("/internal/instrument/FAKE/projections")
        assert response.status_code == 404


class TestRefreshRoute:
    @patch("backend.api.routes_refresh.write_montecarlo")
    @patch("backend.api.routes_refresh.read_latest_prices")
    @patch("backend.api.routes_refresh.blend_regime_params")
    @patch("backend.api.routes_refresh.write_regime")
    @patch("backend.api.routes_refresh.get_transition_matrix")
    @patch("backend.api.routes_refresh.decode_regime")
    @patch("backend.api.routes_refresh.train_hmm")
    @patch("backend.api.routes_refresh.build_feature_matrix")
    @patch("backend.api.routes_refresh.read_all_returns")
    @patch("backend.api.routes_refresh.write_macro_data")
    @patch("backend.api.routes_refresh.fred")
    @patch("backend.api.routes_refresh.write_price_data")
    @patch("backend.api.routes_refresh.get_latest_date")
    @patch("backend.api.routes_refresh.coingecko")
    @patch("backend.api.routes_refresh.yahoo")
    @patch("backend.api.routes_refresh.init_db")
    def test_refresh_success(
        self, mock_init, mock_yahoo, mock_coingecko, mock_latest_date,
        mock_write_price, mock_fred, mock_write_macro, mock_returns,
        mock_features, mock_train, mock_decode, mock_trans,
        mock_write_regime, mock_blend, mock_latest_prices, mock_write_mc,
    ):
        mock_init.return_value = _mock_conn()
        mock_latest_date.return_value = None
        mock_yahoo.fetch.return_value = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        mock_coingecko.fetch.return_value = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        mock_fred.fetch.return_value = pd.DataFrame(columns=["date", "value"])

        returns_df = pd.DataFrame(
            {"SPY": [0.01, 0.02, -0.01], "BTC": [0.02, -0.01, 0.03]},
            index=[date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
        )
        mock_returns.return_value = returns_df
        mock_features.return_value = np.random.randn(3, 3)

        model = MagicMock()
        mock_train.return_value = model
        mock_decode.return_value = (0, np.array([0.8, 0.1, 0.05, 0.03, 0.02]))
        mock_trans.return_value = np.eye(5)
        mock_blend.return_value = (np.zeros(3), np.eye(3))
        mock_latest_prices.return_value = pd.DataFrame({
            "instrument": ["SPY"],
            "close": [450.0],
        })

        response = client.post("/internal/refresh")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "refreshed"
        assert data["regime"]["label"] == "Bull"
