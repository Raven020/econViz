# DuckDB storage interface.
# Handles database initialization, schema creation, and all read/write
# operations for cached historical data, latest prices, and model outputs.
# This is the single gateway to the database — no other module touches DuckDB directly.

# Tables - price_history (daily OHLCV for all assets), macro_data(indicator name, data, value)
# regime(timestamp, label, confidence, transition matrix), monte-carlo(instrument, percentile paths)

import json
from datetime import date

import duckdb
import numpy as np
import pandas as pd

from backend.config import market_date as _market_date


def ensure_schema(db_path):
    """One-time schema initialization. Called at app startup, not per-request.

    Creates all tables and indexes if they don't exist.
    """
    conn = duckdb.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            instrument VARCHAR,
            date DATE,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT
        );
        CREATE TABLE IF NOT EXISTS macro_data (
            indicator VARCHAR,
            date DATE,
            value DOUBLE
        );
        CREATE TABLE IF NOT EXISTS regime (
            date DATE,
            label VARCHAR,
            confidence DOUBLE,
            transition_matrix VARCHAR
        );
        CREATE TABLE IF NOT EXISTS montecarlo (
            date DATE,
            instrument VARCHAR,
            percentile INTEGER,
            day_1 DOUBLE, day_2 DOUBLE, day_3 DOUBLE, day_4 DOUBLE, day_5 DOUBLE,
            day_6 DOUBLE, day_7 DOUBLE, day_8 DOUBLE, day_9 DOUBLE, day_10 DOUBLE,
            day_11 DOUBLE, day_12 DOUBLE, day_13 DOUBLE, day_14 DOUBLE, day_15 DOUBLE,
            day_16 DOUBLE, day_17 DOUBLE, day_18 DOUBLE, day_19 DOUBLE, day_20 DOUBLE,
            day_21 DOUBLE, day_22 DOUBLE, day_23 DOUBLE, day_24 DOUBLE, day_25 DOUBLE,
            day_26 DOUBLE, day_27 DOUBLE, day_28 DOUBLE, day_29 DOUBLE, day_30 DOUBLE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ph_inst_date ON price_history(instrument, date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mc_inst_date ON montecarlo(instrument, date)")
    conn.close()


def connect(db_path):
    """Lightweight connection — no DDL. Use for per-request connections."""
    return duckdb.connect(db_path)


# Keep init_db as an alias for tests that use :memory:
def init_db(db_path):
    """Connect and ensure schema. Used by tests with :memory: databases."""
    conn = duckdb.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            instrument VARCHAR, date DATE, open DOUBLE, high DOUBLE,
            low DOUBLE, close DOUBLE, volume BIGINT
        );
        CREATE TABLE IF NOT EXISTS macro_data (
            indicator VARCHAR, date DATE, value DOUBLE
        );
        CREATE TABLE IF NOT EXISTS regime (
            date DATE, label VARCHAR, confidence DOUBLE, transition_matrix VARCHAR
        );
        CREATE TABLE IF NOT EXISTS montecarlo (
            date DATE, instrument VARCHAR, percentile INTEGER,
            day_1 DOUBLE, day_2 DOUBLE, day_3 DOUBLE, day_4 DOUBLE, day_5 DOUBLE,
            day_6 DOUBLE, day_7 DOUBLE, day_8 DOUBLE, day_9 DOUBLE, day_10 DOUBLE,
            day_11 DOUBLE, day_12 DOUBLE, day_13 DOUBLE, day_14 DOUBLE, day_15 DOUBLE,
            day_16 DOUBLE, day_17 DOUBLE, day_18 DOUBLE, day_19 DOUBLE, day_20 DOUBLE,
            day_21 DOUBLE, day_22 DOUBLE, day_23 DOUBLE, day_24 DOUBLE, day_25 DOUBLE,
            day_26 DOUBLE, day_27 DOUBLE, day_28 DOUBLE, day_29 DOUBLE, day_30 DOUBLE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ph_inst_date ON price_history(instrument, date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mc_inst_date ON montecarlo(instrument, date)")
    return conn


def get_latest_date(conn, instrument):
    """Return the most recent date for an instrument, or None if no data."""
    result = conn.execute(
        "SELECT MAX(date) FROM price_history WHERE instrument = ?", [instrument]
    ).fetchone()
    return result[0] if result else None


def get_latest_macro_date(conn, indicator):
    """Return the most recent date for a macro indicator, or None if no data."""
    result = conn.execute(
        "SELECT MAX(date) FROM macro_data WHERE indicator = ?", [indicator]
    ).fetchone()
    return result[0] if result else None


def write_price_data(conn, instrument, df):
    """Insert price data, replacing any existing rows for the same instrument+date range."""
    df = df.copy()
    df["instrument"] = instrument
    df = df[["instrument", "date", "open", "high", "low", "close", "volume"]]
    if df.empty:
        return
    min_date = df["date"].min()
    max_date = df["date"].max()
    conn.execute(
        "DELETE FROM price_history WHERE instrument = ? AND date BETWEEN ? AND ?",
        [instrument, min_date, max_date],
    )
    conn.execute("INSERT INTO price_history SELECT * FROM df")


def read_price_history(conn, instrument, start_date, end_date):
    """Read OHLCV history for one instrument in a date range."""
    return conn.execute(
        """SELECT date, open, high, low, close, volume FROM price_history
        WHERE instrument = ? AND date BETWEEN ? AND ? ORDER BY date""",
        [instrument, start_date, end_date]
    ).fetchdf()


def read_all_returns(conn, start_date, end_date):
    """Read cross-asset daily returns matrix for HMM training.

    Uses forward-fill per instrument before computing pct_change to handle
    instruments with different trading calendars (e.g., crypto vs equities).
    """
    df = conn.execute("""
        SELECT instrument, date, close FROM price_history
        WHERE date BETWEEN ? AND ? ORDER BY date""", [start_date, end_date]
    ).fetchdf()
    pivoted = df.pivot(index="date", columns="instrument", values="close")
    pivoted = pivoted.ffill()
    return pivoted.pct_change().dropna(how="all").dropna()


def read_latest_prices(conn):
    """Read the 2 most recent trading days per instrument and compute daily change."""
    df = conn.execute("""
        SELECT instrument, date, open, high, low, close, volume
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY instrument ORDER BY date DESC) AS rn
            FROM price_history
        )
        WHERE rn <= 2
        ORDER BY instrument, date
    """).fetchdf()

    result = []
    for instrument, group in df.groupby("instrument"):
        group = group.sort_values("date")
        latest = group.iloc[-1]
        prev_close = group.iloc[-2]["close"] if len(group) > 1 else latest["close"]
        change = latest["close"] - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0.0
        result.append({
            "instrument": instrument,
            "close": latest["close"],
            "change": change,
            "change_pct": change_pct,
            "high": latest["high"],
            "low": latest["low"],
            "volume": latest["volume"],
        })
    return pd.DataFrame(result)


def read_sparklines(conn):
    """Fetch the last 30 closing prices for all instruments in a single query."""
    return conn.execute("""
        SELECT instrument, date, close
        FROM price_history
        QUALIFY ROW_NUMBER() OVER (PARTITION BY instrument ORDER BY date DESC) <= 30
        ORDER BY instrument, date
    """).fetchdf()


def read_macro_matrix(conn, start_date, end_date):
    """Read macro indicators as a date-indexed matrix for HMM features.

    Pivots macro_data so each indicator is a column. Forward-fills to handle
    different reporting frequencies (e.g., jobless claims is weekly, fed funds
    is monthly). Computes daily changes to match the returns scale.

    Returns:
        pd.DataFrame: rows indexed by date, one column per indicator with daily changes.
    """
    df = conn.execute("""
        SELECT indicator, date, value FROM macro_data
        WHERE date BETWEEN ? AND ? ORDER BY date
    """, [start_date, end_date]).fetchdf()
    if df.empty:
        return pd.DataFrame()
    pivoted = df.pivot(index="date", columns="indicator", values="value")
    pivoted = pivoted.ffill()
    # Use diff instead of pct_change — macro indicators are levels/rates, not prices
    # Normalize by dividing by the rolling mean to get scale-comparable changes
    changes = pivoted.diff()
    means = pivoted.rolling(window=20, min_periods=1).mean()
    normalized = (changes / means.replace(0, np.nan)).fillna(0)
    return normalized.dropna(how="all").dropna()


def write_macro_data(conn, indicator, df):
    """Insert macro data, replacing any existing rows for the same indicator+date range."""
    df = df.copy()
    df["indicator"] = indicator
    df = df[["indicator", "date", "value"]]
    if df.empty:
        return
    min_date = df["date"].min()
    max_date = df["date"].max()
    conn.execute(
        "DELETE FROM macro_data WHERE indicator = ? AND date BETWEEN ? AND ?",
        [indicator, min_date, max_date],
    )
    conn.execute("INSERT INTO macro_data SELECT * FROM df")


def read_macro_data(conn, indicator, start_date, end_date):
    """Read macro indicator values in a date range."""
    return conn.execute(
        "SELECT date, value FROM macro_data WHERE indicator = ? AND date BETWEEN ? AND ? ORDER BY date",
        [indicator, start_date, end_date]
    ).fetchdf()


def write_regime(conn, regime_label, confidence, transition_matrix):
    """Write regime classification, replacing any existing entry for today."""
    today = _market_date()
    matrix_json = json.dumps(transition_matrix.tolist())
    conn.execute("DELETE FROM regime WHERE date = ?", [today])
    conn.execute(
        "INSERT INTO regime VALUES (?, ?, ?, ?)",
        [today, regime_label, confidence, matrix_json]
    )


def read_regime(conn):
    """Read the most recent regime classification."""
    result = conn.execute(
        "SELECT label, confidence, transition_matrix FROM regime ORDER BY date DESC LIMIT 1"
    ).fetchone()
    if result is None:
        return None
    label, confidence, matrix_json = result
    transition_matrix = np.array(json.loads(matrix_json))
    return (label, confidence, transition_matrix)


def write_montecarlo(conn, instrument, projection_cones):
    """Write Monte Carlo projections, replacing any existing entry for today+instrument."""
    today = _market_date()
    conn.execute(
        "DELETE FROM montecarlo WHERE instrument = ? AND date = ?",
        [instrument, today]
    )
    for percentile, values in projection_cones.items():
        conn.execute(
            "INSERT INTO montecarlo VALUES (?, ?, ?, " + ", ".join(["?"] * 30) + ")",
            [today, instrument, percentile] + values
        )


def read_montecarlo(conn, instrument):
    """Read the latest Monte Carlo projections for an instrument."""
    result = conn.execute("""
        SELECT percentile, day_1, day_2, day_3, day_4, day_5, day_6, day_7, day_8, day_9, day_10,
               day_11, day_12, day_13, day_14, day_15, day_16, day_17, day_18, day_19, day_20,
               day_21, day_22, day_23, day_24, day_25, day_26, day_27, day_28, day_29, day_30
        FROM montecarlo
        WHERE instrument = ? AND date = (SELECT MAX(date) FROM montecarlo WHERE instrument = ?)
        ORDER BY percentile
    """, [instrument, instrument]).fetchdf()
    return result
