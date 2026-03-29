import json
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from backend.data.store import (
    init_db,
    ensure_schema,
    connect,
    get_latest_date,
    get_latest_macro_date,
    write_price_data,
    read_price_history,
    read_all_returns,
    read_latest_prices,
    read_sparklines,
    write_macro_data,
    read_macro_data,
    read_macro_matrix,
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


class TestSchemaInit:
    def test_ensure_schema_creates_tables(self, tmp_path):
        db_path = str(tmp_path / "test.duckdb")
        ensure_schema(db_path)
        conn = connect(db_path)
        tables = conn.execute("SHOW TABLES").fetchdf()
        table_names = tables["name"].tolist()
        assert "price_history" in table_names
        assert "macro_data" in table_names
        assert "regime" in table_names
        assert "montecarlo" in table_names
        conn.close()

    def test_connect_is_lightweight(self, tmp_path):
        db_path = str(tmp_path / "test.duckdb")
        ensure_schema(db_path)
        conn = connect(db_path)
        # Should be able to query without error
        conn.execute("SELECT 1").fetchone()
        conn.close()


class TestPriceData:
    def test_write_and_read(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_price_history(conn, "SPY", date(2024, 1, 1), date(2024, 1, 3))
        assert len(result) == 3

    def test_write_does_not_mutate_input(self, conn, sample_prices):
        """write_price_data should not modify the caller's DataFrame."""
        original_cols = list(sample_prices.columns)
        write_price_data(conn, "SPY", sample_prices)
        assert list(sample_prices.columns) == original_cols
        assert "instrument" not in sample_prices.columns

    def test_write_deduplicates(self, conn, sample_prices):
        """Writing the same data twice should not create duplicates."""
        write_price_data(conn, "SPY", sample_prices)
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

    def test_read_latest_prices_handles_weekend_gap(self, conn):
        """Change should compare Friday vs Thursday, not fail on weekend gap."""
        df = pd.DataFrame({
            "date": [date(2024, 1, 4), date(2024, 1, 5)],  # Thu, Fri (no Sat/Sun)
            "open": [100.0, 102.0],
            "high": [101.0, 103.0],
            "low": [99.0, 101.0],
            "close": [100.5, 102.5],
            "volume": [1000, 1100],
        })
        write_price_data(conn, "SPY", df)
        result = read_latest_prices(conn)
        assert result.iloc[0]["change_pct"] == pytest.approx(1.99, abs=0.01)

    def test_read_all_returns(self, conn, sample_prices):
        write_price_data(conn, "SPY", sample_prices)
        result = read_all_returns(conn, date(2024, 1, 1), date(2024, 1, 3))
        assert "SPY" in result.columns
        assert len(result) == 2

    def test_read_all_returns_handles_different_calendars(self, conn):
        """ffill should handle instruments with different trading calendars."""
        # SPY trades Mon-Fri, BTC trades every day
        spy_dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        btc_dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)]
        write_price_data(conn, "SPY", pd.DataFrame({
            "date": spy_dates, "open": [100]*3, "high": [101]*3,
            "low": [99]*3, "close": [100, 101, 102], "volume": [1000]*3,
        }))
        write_price_data(conn, "BTC", pd.DataFrame({
            "date": btc_dates, "open": [50000]*4, "high": [51000]*4,
            "low": [49000]*4, "close": [50000, 51000, 52000, 53000], "volume": [500]*4,
        }))
        result = read_all_returns(conn, date(2024, 1, 1), date(2024, 1, 4))
        # Should have rows for all dates, with SPY forward-filled for Jan 4
        assert "SPY" in result.columns
        assert "BTC" in result.columns
        assert not result.isna().any().any()


class TestSparklines:
    def test_returns_last_30_per_instrument(self, conn):
        dates_50 = [date(2024, 1, 1) + timedelta(days=i) for i in range(50)]
        df_spy = pd.DataFrame({
            "date": dates_50, "open": [100.0]*50, "high": [101.0]*50,
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
        write_price_data(conn, "SPY", sample_prices)
        old_sparkline = read_price_history(conn, "SPY", "1900-01-01", "2099-12-31")["close"].tail(30).tolist()
        sparklines = read_sparklines(conn)
        new_sparkline = sparklines[sparklines["instrument"] == "SPY"]["close"].tolist()
        assert old_sparkline == new_sparkline


class TestIndexes:
    def test_indexes_created(self, conn):
        indexes = conn.execute("SELECT index_name FROM duckdb_indexes()").fetchdf()
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

    def test_write_does_not_mutate_input(self, conn):
        df = pd.DataFrame({"date": [date(2024, 1, 1)], "value": [4.5]})
        original_cols = list(df.columns)
        write_macro_data(conn, "FED_FUNDS", df)
        assert list(df.columns) == original_cols

    def test_write_deduplicates(self, conn):
        df = pd.DataFrame({"date": [date(2024, 1, 1)], "value": [4.5]})
        write_macro_data(conn, "FED_FUNDS", df)
        write_macro_data(conn, "FED_FUNDS", df)
        result = read_macro_data(conn, "FED_FUNDS", date(2024, 1, 1), date(2024, 1, 1))
        assert len(result) == 1

    def test_get_latest_macro_date_empty(self, conn):
        assert get_latest_macro_date(conn, "FED_FUNDS") is None

    def test_get_latest_macro_date(self, conn):
        df = pd.DataFrame({"date": [date(2024, 1, 1), date(2024, 1, 2)], "value": [4.5, 4.6]})
        write_macro_data(conn, "FED_FUNDS", df)
        assert get_latest_macro_date(conn, "FED_FUNDS") == date(2024, 1, 2)


class TestMacroMatrix:
    def test_empty_returns_empty(self, conn):
        result = read_macro_matrix(conn, date(2024, 1, 1), date(2024, 12, 31))
        assert result.empty

    def test_returns_pivoted_indicators(self, conn):
        for d in range(1, 22):
            df = pd.DataFrame({"date": [date(2024, 1, d)], "value": [4.0 + d * 0.01]})
            write_macro_data(conn, "FED_FUNDS", df)
            df2 = pd.DataFrame({"date": [date(2024, 1, d)], "value": [2.0 + d * 0.02]})
            write_macro_data(conn, "INFLATION_5Y", df2)

        result = read_macro_matrix(conn, date(2024, 1, 1), date(2024, 1, 21))
        assert "FED_FUNDS" in result.columns
        assert "INFLATION_5Y" in result.columns
        assert not result.empty
        # Values should be normalized changes, not raw levels
        assert result["FED_FUNDS"].abs().max() < 1.0

    def test_aligned_to_returns(self, conn):
        """Macro matrix can be aligned to returns index."""
        # Write price and macro data
        for d in range(1, 22):
            dt = date(2024, 1, d)
            write_price_data(conn, "SPY", pd.DataFrame({
                "date": [dt], "open": [100.0], "high": [101.0],
                "low": [99.0], "close": [100.0 + d * 0.5], "volume": [1000],
            }))
            write_macro_data(conn, "FED_FUNDS", pd.DataFrame({
                "date": [dt], "value": [4.0 + d * 0.01],
            }))

        returns_df = read_all_returns(conn, date(2024, 1, 1), date(2024, 1, 21))
        macro_df = read_macro_matrix(conn, date(2024, 1, 1), date(2024, 1, 21))

        # Align macro to returns dates
        macro_aligned = macro_df.reindex(returns_df.index).ffill().fillna(0)
        assert len(macro_aligned) == len(returns_df)
        assert not macro_aligned.isna().any().any()


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

    def test_write_replaces_same_day(self, conn):
        """Multiple writes on same day should not create duplicates."""
        write_regime(conn, "Bull", 0.85, np.eye(5))
        write_regime(conn, "Bear", 0.70, np.eye(5))
        count = conn.execute("SELECT COUNT(*) FROM regime").fetchone()[0]
        # Should be 1 (replaced), not 2
        assert count == 1
        label, _, _ = read_regime(conn)
        assert label == "Bear"


class TestMonteCarlo:
    def test_read_empty_returns_dataframe(self, conn):
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

    def test_write_replaces_same_day(self, conn):
        """Multiple writes on same day should not create duplicates."""
        cones = {10: [float(i) for i in range(30)], 50: [float(i) for i in range(30)]}
        write_montecarlo(conn, "SPY", cones)
        write_montecarlo(conn, "SPY", cones)
        count = conn.execute("SELECT COUNT(*) FROM montecarlo WHERE instrument = 'SPY'").fetchone()[0]
        assert count == 2  # 2 percentiles, not 4
