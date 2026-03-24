# Drilldown routes — GET /internal/instrument/{ticker}
# Returns price detail and historical OHLCV for a single instrument.

from fastapi import APIRouter, HTTPException

from backend.config import DB_PATH
from backend.data.store import init_db, read_latest_prices, read_price_history, read_regime

router = APIRouter(prefix="/internal")


@router.get("/instrument/{ticker}")
def get_instrument(ticker: str):
    conn = init_db(DB_PATH)

    latest = read_latest_prices(conn)
    row = latest[latest["instrument"] == ticker]
    if row.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Instrument {ticker} not found")
    row = row.iloc[0]

    history = read_price_history(conn, ticker, "1900-01-01", "2099-12-31")
    ohlcv = history.to_dict(orient="records")

    regime_data = read_regime(conn)
    regime = None
    if regime_data:
        label, confidence, transition_matrix = regime_data
        regime = {
            "label": label,
            "confidence": confidence,
            "transition_matrix": transition_matrix.tolist(),
        }

    conn.close()
    return {
        "ticker": ticker,
        "close": row["close"],
        "change": row["change"],
        "change_pct": row["change_pct"],
        "high": row["high"],
        "low": row["low"],
        "volume": int(row["volume"]),
        "history": ohlcv,
        "regime": regime,
    }
