# Monte Carlo routes — GET /internal/instrument/{ticker}/projections
# Returns percentile projection paths from the latest simulation.

from fastapi import APIRouter, Depends, HTTPException
import duckdb

from backend.api.deps import get_conn
from backend.config import YAHOO_TICKERS, CRYPTO_IDS
from backend.data.store import read_montecarlo

VALID_TICKERS = set(YAHOO_TICKERS.keys()) | set(CRYPTO_IDS.keys())

router = APIRouter(prefix="/internal")


@router.get("/instrument/{ticker}/projections")
def get_projections(ticker: str, conn: duckdb.DuckDBPyConnection = Depends(get_conn)):
    if ticker not in VALID_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown instrument: {ticker}")

    result = read_montecarlo(conn, ticker)

    if result.empty:
        raise HTTPException(status_code=404, detail=f"No projections for {ticker}")

    return result.to_dict(orient="records")
