import json
from datetime import date

import numpy as np
import pandas as pd
import pytest

from backend.data.store import (
    init_db,
    get_latest_date,
    write_price_data,
    read_price_history,
    read_all_returns,
    read_latest_prices,
    write_macro_data,
    read_macro_data,
    write_regime,
    read_regime,
    write_montecarlo,
    read_montecarlo,
)


@pytest.fixture
def conn():
    db = init_db(":memory:")
    yield db
    db.close()


@pytest.fixture
def sample_prices():
    return pd.DataFrame({
        "date": [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
        "open": [100.0, 101.0, 102.0],
        "high": [101.0, 102.0, 103.0],
        "low": [99.0, 100.0, 101.0],
        "close": [100.5, 101.5, 102.5],
        "volume": [1000, 1100, 1200],
    })


class TestPriceData:
    def test_write_and_read(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_price_history(conn, "SPY", date(2024, 1, 1), date(2024, 1, 3))
        assert len(result) == 3

    def test_get_latest_date_empty(self, conn):
        result = get_latest_date(conn, "SPY")
        assert result is None

    def test_get_latest_date(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = get_latest_date(conn, "SPY")
        assert result == date(2024, 1, 3)

    def test_read_latest_prices(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_latest_prices(conn)
        assert len(result) == 1
        assert result.iloc[0]["instrument"] == "SPY"
        assert result.iloc[0]["close"] == 102.5

    def test_read_all_returns(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_all_returns(conn, date(2024, 1, 1), date(2024, 1, 3))
        assert "SPY" in result.columns
        assert len(result) == 2  # pct_change drops first row


class TestMacroData:
    def test_write_and_read(self, conn):
        df = pd.DataFrame({
            "date": [date(2024, 1, 1), date(2024, 1, 2)],
            "value": [4.5, 4.6],
        })
        write_macro_data(conn, "FED_FUNDS", df)
        result = read_macro_data(conn, "FED_FUNDS", date(2024, 1, 1), date(2024, 1, 2))
        assert len(result) == 2


class TestRegime:
    def test_read_empty(self, conn):
        result = read_regime(conn)
        assert result is None

    def test_write_and_read(self, conn):
        matrix = np.eye(5)
        write_regime(conn, "Bull", 0.85, matrix)
        label, confidence, result_matrix = read_regime(conn)
        assert label == "Bull"
        assert confidence == 0.85
        np.testing.assert_array_equal(result_matrix, matrix)


class TestMonteCarlo:
    def test_read_empty(self, conn):
        result = read_montecarlo(conn, "SPY")
        assert result is None

    def test_write_and_read(self, conn):
        cones = {
            10: [float(i) for i in range(30)],
            50: [float(i + 10) for i in range(30)],
            90: [float(i + 20) for i in range(30)],
        }
        write_montecarlo(conn, "SPY", cones)
        result = read_montecarlo(conn, "SPY")
        assert len(result) == 3
        assert set(result["percentile"].tolist()) == {10, 50, 90}
