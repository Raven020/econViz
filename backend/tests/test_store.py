import json
from datetime import date, timedelta

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
    read_sparklines,
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

    def test_read_latest_prices_single_day(self, conn):
        """When only one day of data exists, change should be 0."""
        df = pd.DataFrame({
            "date": [date(2024, 1, 1)],
            "open": [100.0], "high": [101.0], "low": [99.0],
            "close": [100.5], "volume": [1000],
        })
        write_price_data(conn, "SPY", df)
        result = read_latest_prices(conn)
        assert len(result) == 1
        assert result.iloc[0]["change"] == 0.0

    def test_read_latest_prices_empty(self, conn):
        result = read_latest_prices(conn)
        assert result.empty

    def test_read_all_returns(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_all_returns(conn, date(2024, 1, 1), date(2024, 1, 3))
        assert "SPY" in result.columns
        assert len(result) == 2  # pct_change drops first row


class TestSparklines:
    def test_returns_last_30_per_instrument(self, conn):
        dates_50 = [date(2024, 1, 1) + timedelta(days=i) for i in range(50)]
        df_spy = pd.DataFrame({
            "date": dates_50,
            "open": [100.0]*50, "high": [101.0]*50,
            "low": [99.0]*50, "close": [100.0 + i for i in range(50)],
            "volume": [1000]*50,
        })
        write_price_data(conn, "SPY", df_spy)

        result = read_sparklines(conn)
        spy_rows = result[result["instrument"] == "SPY"]
        assert len(spy_rows) == 30

    def test_fewer_than_30(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_sparklines(conn)
        spy_rows = result[result["instrument"] == "SPY"]
        assert len(spy_rows) == 3

    def test_empty_table(self, conn):
        result = read_sparklines(conn)
        assert result.empty

    def test_matches_old_behavior(self, conn, sample_prices):
        """Verify new sparkline query produces same results as reading full history."""
        write_price_data(conn, "SPY", sample_prices)
        old_sparkline = read_price_history(conn, "SPY", "1900-01-01", "2099-12-31")["close"].tail(30).tolist()
        sparklines = read_sparklines(conn)
        new_sparkline = sparklines[sparklines["instrument"] == "SPY"]["close"].tolist()
        assert old_sparkline == new_sparkline


class TestIndexes:
    def test_indexes_created(self, conn):
        indexes = conn.execute(
            "SELECT index_name FROM duckdb_indexes()"
        ).fetchdf()
        index_names = indexes["index_name"].tolist()
        assert "idx_ph_inst_date" in index_names
        assert "idx_mc_inst_date" in index_names

    def test_queries_correct_with_indexes(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_price_history(conn, "SPY", date(2024, 1, 1), date(2024, 1, 3))
        assert len(result) == 3
        assert result.iloc[0]["close"] == 100.5


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
    def test_read_empty_returns_dataframe(self, conn):
        """read_montecarlo should return an empty DataFrame, not None."""
        result = read_montecarlo(conn, "SPY")
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_write_and_read(self, conn):
        cones = {
            10: [float(i) for i in range(30)],
            50: [float(i + 10) for i in range(30)],
            90: [float(i + 20) for i in range(30)],
        }
        write_montecarlo(conn, "SPY", cones)
        result = read_montecarlo(conn, "SPY")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert set(result["percentile"].tolist()) == {10, 50, 90}
