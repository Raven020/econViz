# Dashboard routes — GET /internal/instruments
# Returns all instrument prices, daily changes, and sparkline data.

from fastapi import APIRouter

from backend.config import DB_PATH
from backend.data.store import init_db, read_latest_prices, read_price_history

router = APIRouter(prefix="/internal")


@router.get("/instruments")
def get_instruments():
    conn = init_db(DB_PATH)
    latest = read_latest_prices(conn)

    instruments = []
    for _, row in latest.iterrows():
        ticker = row["instrument"]
        history = read_price_history(conn, ticker, "1900-01-01", "2099-12-31")
        sparkline = history["close"].tail(30).tolist()

        instruments.append({
            "ticker": ticker,
            "close": row["close"],
            "change": row["change"],
            "change_pct": row["change_pct"],
            "high": row["high"],
            "low": row["low"],
            "volume": int(row["volume"]),
            "sparkline": sparkline,
        })

    conn.close()
    return instruments
