# DuckDB storage interface.
# Handles database initialization, schema creation, and all read/write
# operations for cached historical data, latest prices, and model outputs.
# This is the single gateway to the database — no other module touches DuckDB directly.

# Tables - price_history (daily OHLCV for all  assests), macro_data(indicator name, data, value)
# regime(timestamp, label, confidence, trasition matrix), monte-carlo(instrument, percentile paths)

import json
from datetime import date

import duckdb
import numpy as np
import pandas as pd


def init_db(db_path):
    """
    Args:
        db_path (str): file path to the DuckDB database file (e.g. "data/econ_desk.duckdb")

    Process:
        Connects to DuckDB at the given path (creates the file if it doesn't exist).
        Runs CREATE TABLE IF NOT EXISTS for all four tables: price_history, macro_data,
        regime, montecarlo. Safe to call on every app start.

    Returns:
        conn (duckdb.DuckDBPyConnection): the database connection used by all other functions
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
    return conn



def get_latest_date(conn, instrument):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        instrument (str): ticker/identifier for the instrument (e.g. "SPY", "BTC", "GC=F")

    Process:
        Queries price_history for the MAX(date) where instrument matches.
        Uses parameterized query to safely pass instrument name.

    Returns:
        datetime.date: the most recent date stored for this instrument,
        or None if no data exists (signals full 5-year backfill needed)
    """
    result = (conn.execute("""
	SELECT MAX(date) from price_history WHERE instrument = ?""", [instrument]).fetchone())
    return result[0] if result else None

def write_price_data(conn, instrument, df):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        instrument (str): ticker/identifier (e.g. "SPY", "BTC")
        df (pd.DataFrame): price data from a fetcher with columns: date, open, high, low, close, volume

    Process:
        Adds an 'instrument' column to the DataFrame with the given identifier.
        Inserts the full DataFrame into the price_history table using DuckDB's
        direct DataFrame ingestion (INSERT INTO ... SELECT * FROM df).

    Returns:
        None
    """
    df["instrument"] = instrument
    df = df[["instrument", "date", "open", "high", "low", "close", "volume"]]
    conn.execute("INSERT INTO price_history SELECT * FROM df")



def read_price_history(conn, instrument, start_date, end_date):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        instrument (str): ticker/identifier (e.g. "SPY")
        start_date (str or datetime.date): beginning of date range
        end_date (str or datetime.date): end of date range

    Process:
        Queries price_history for all rows matching the instrument and date range.
        Uses .fetchdf() to return results as a pandas DataFrame.

    Returns:
        pd.DataFrame: rows with columns date, open, high, low, close, volume
    """
    return conn.execute(
        """SELECT date, open, high, low, close, volume FROM price_history 
	WHERE instrument = ? AND date BETWEEN ? AND ? ORDER BY date""",
        [instrument, start_date, end_date]
    ).fetchdf()


def read_all_returns(conn, start_date, end_date):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        start_date (str or datetime.date): beginning of date range
        end_date (str or datetime.date): end of date range

    Process:
        Queries price_history for all instruments in the date range.
        Computes daily percentage returns from close prices.
        Pivots the data so each instrument is a column, each row is a date.
        Used by the HMM — it needs the full cross-asset return matrix.

    Returns:
        pd.DataFrame: rows indexed by date, one column per instrument containing daily returns
    """
    df = conn.execute("""
	SELECT instrument, date, close from price_history 
        WHERE date BETWEEN ? AND ? ORDER BY date""", [start_date, end_date]).fetchdf()
    return(df.pivot(index="date", columns="instrument", values="close").pct_change().dropna())

def read_latest_prices(conn):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()

    Process:
        Queries price_history for the most recent date's data for each instrument.
        Calculates daily change (absolute and percentage) by comparing to the
        previous day's close. Used by the dashboard for the main price table.

    Returns:
        pd.DataFrame: one row per instrument with columns: instrument, close, change,
        change_pct, high, low, volume
    """
    df = conn.execute("""
        WITH latest AS (
            SELECT instrument, MAX(date) AS max_date
            FROM price_history
            GROUP BY instrument
        )
        SELECT p.instrument, p.date, p.open, p.high, p.low, p.close, p.volume
        FROM price_history p
        JOIN latest l ON p.instrument = l.instrument AND p.date >= l.max_date - INTERVAL 1 DAY
        ORDER BY p.instrument, p.date
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


def write_macro_data(conn, indicator, df):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        indicator (str): macro indicator name (e.g. "T10Y2Y", "JOBLESS_CLAIMS", "FED_FUNDS")
        df (pd.DataFrame): data from FRED or Treasury fetcher with columns: date, value

    Process:
        Adds an 'indicator' column to the DataFrame with the given identifier.
        Inserts the full DataFrame into the macro_data table.

    Returns:
        None
    """
    df["indicator"] = indicator
    df = df[["indicator", "date", "value"]]
    conn.execute("INSERT INTO macro_data SELECT * FROM df")


def read_macro_data(conn, indicator, start_date, end_date):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        indicator (str): macro indicator name (e.g. "T10Y2Y", "JOBLESS_CLAIMS")
        start_date (str or datetime.date): beginning of date range
        end_date (str or datetime.date): end of date range

    Process:
        Queries macro_data for all rows matching the indicator and date range.
        Uses .fetchdf() to return results as a pandas DataFrame.

    Returns:
        pd.DataFrame: rows with columns: date, value
    """
    return conn.execute(
        "SELECT date, value FROM macro_data WHERE indicator = ? AND date BETWEEN ? AND ? ORDER BY date",
        [indicator, start_date, end_date]
    ).fetchdf()


def write_regime(conn, regime_label, confidence, transition_matrix):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        regime_label (str): current regime name (e.g. "BULL", "CRISIS")
        confidence (float): probability of being in the identified regime (0.0 to 1.0)
        transition_matrix (np.ndarray): 5x5 matrix of transition probabilities between regimes

    Process:
        Serializes the transition_matrix to a JSON string.
        Inserts a row into the regime table with today's date, label, confidence,
        and the serialized matrix.

    Returns:
        None
    """
    matrix_json = json.dumps(transition_matrix.tolist())
    conn.execute(
        "INSERT INTO regime VALUES (?, ?, ?, ?)",
        [date.today(), regime_label, confidence, matrix_json]
    )


def read_regime(conn):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()

    Process:
        Queries the regime table for the most recent row (by date).
        Deserializes the transition_matrix from JSON string back to a numpy array.

    Returns:
        tuple: (label: str, confidence: float, transition_matrix: np.ndarray)
        or None if no regime data exists yet
    """
    result = conn.execute(
        "SELECT label, confidence, transition_matrix FROM regime ORDER BY date DESC LIMIT 1"
    ).fetchone()
    if result is None:
        return None
    label, confidence, matrix_json = result
    transition_matrix = np.array(json.loads(matrix_json))
    return (label, confidence, transition_matrix)


def write_montecarlo(conn, instrument, projection_cones):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        instrument (str): ticker/identifier (e.g. "SPY", "BTC")
        projection_cones (dict): maps percentile (int) to a list of 30 projected values
            e.g. {10: [540.1, 538.2, ...], 25: [...], 50: [...], 75: [...], 90: [...]}

    Process:
        Inserts one row per percentile into the montecarlo table with today's date,
        instrument name, percentile level, and the 30 daily projected values (day_1 through day_30).

    Returns:
        None
    """
    today = date.today()
    for percentile, values in projection_cones.items():
        conn.execute(
            "INSERT INTO montecarlo VALUES (?, ?, ?, " + ", ".join(["?"] * 30) + ")",
            [today, instrument, percentile] + values
        )


def read_montecarlo(conn, instrument):
    """
    Args:
        conn (duckdb.DuckDBPyConnection): database connection from init_db()
        instrument (str): ticker/identifier (e.g. "SPY", "BTC")

    Process:
        Queries the montecarlo table for the most recent date's projections
        for the given instrument. Returns all 5 percentile rows (10/25/50/75/90).
        Used by the drilldown view to render projection cone charts.

    Returns:
        pd.DataFrame: rows with columns: percentile, day_1 through day_30
        or None if no projection data exists for this instrument
    """
    result = conn.execute("""
        SELECT percentile, day_1, day_2, day_3, day_4, day_5, day_6, day_7, day_8, day_9, day_10,
               day_11, day_12, day_13, day_14, day_15, day_16, day_17, day_18, day_19, day_20,
               day_21, day_22, day_23, day_24, day_25, day_26, day_27, day_28, day_29, day_30
        FROM montecarlo
        WHERE instrument = ? AND date = (SELECT MAX(date) FROM montecarlo WHERE instrument = ?)
        ORDER BY percentile
    """, [instrument, instrument]).fetchdf()
    return result if len(result) > 0 else None
