# Drilldown routes — GET /internal/instrument/{ticker}
# Returns price detail and historical OHLCV for a single instrument.

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
import duckdb

from backend.api.deps import get_conn
from backend.config import YAHOO_TICKERS, CRYPTO_IDS
from backend.data.store import read_latest_prices, read_price_history, read_regime

VALID_TICKERS = set(YAHOO_TICKERS.keys()) | set(CRYPTO_IDS.keys())

router = APIRouter(prefix="/internal")


@router.get("/instrument/{ticker}")
def get_instrument(ticker: str, conn: duckdb.DuckDBPyConnection = Depends(get_conn)):
    if ticker not in VALID_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown instrument: {ticker}")

    latest = read_latest_prices(conn)
    row = latest[latest["instrument"] == ticker]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Instrument {ticker} not found")
    row = row.iloc[0]

    end = date.today()
    start = end - timedelta(days=730)
    history = read_price_history(conn, ticker, start, end)
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
