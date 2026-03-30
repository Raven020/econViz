# Dashboard routes — GET /internal/instruments, GET /internal/macro
# Returns all instrument prices, daily changes, sparkline data, and macro indicators.

from fastapi import APIRouter, Depends
import duckdb

from backend.api.deps import get_conn
from backend.data.store import read_latest_prices, read_sparklines, read_latest_macro, read_macro_sparklines

router = APIRouter(prefix="/internal")


@router.get("/instruments")
def get_instruments(conn: duckdb.DuckDBPyConnection = Depends(get_conn)):
    latest = read_latest_prices(conn)

    sparklines = read_sparklines(conn)
    sparkline_map = {}
    for instrument, group in sparklines.groupby("instrument"):
        sparkline_map[instrument] = group.sort_values("date")["close"].tolist()

    instruments = []
    for _, row in latest.iterrows():
        ticker = row["instrument"]
        instruments.append({
            "ticker": ticker,
            "close": row["close"],
            "change": row["change"],
            "change_pct": row["change_pct"],
            "high": row["high"],
            "low": row["low"],
            "volume": int(row["volume"]),
            "sparkline": sparkline_map.get(ticker, []),
        })

    return instruments


@router.get("/macro")
def get_macro(conn: duckdb.DuckDBPyConnection = Depends(get_conn)):
    latest = read_latest_macro(conn)

    sparklines = read_macro_sparklines(conn)
    sparkline_map = {}
    for indicator, group in sparklines.groupby("indicator"):
        sparkline_map[indicator] = group.sort_values("date")["value"].tolist()

    indicators = []
    for _, row in latest.iterrows():
        name = row["indicator"]
        indicators.append({
            "indicator": name,
            "value": row["value"],
            "change": row["change"],
            "change_pct": row["change_pct"],
            "date": row["date"],
            "sparkline": sparkline_map.get(name, []),
        })

    return indicators
