# Dashboard routes — GET /internal/instruments
# Returns all instrument prices, daily changes, and sparkline data.

from fastapi import APIRouter, Depends
import duckdb

from backend.api.deps import get_conn
from backend.data.store import read_latest_prices, read_sparklines

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
