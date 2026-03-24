# Monte Carlo routes — GET /internal/instrument/{ticker}/projections
# Returns percentile projection paths from the latest simulation.

from fastapi import APIRouter, HTTPException

from backend.config import DB_PATH
from backend.data.store import init_db, read_montecarlo

router = APIRouter(prefix="/internal")


@router.get("/instrument/{ticker}/projections")
def get_projections(ticker: str):
    conn = init_db(DB_PATH)
    result = read_montecarlo(conn, ticker)
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail=f"No projections for {ticker}")

    return result.to_dict(orient="records")
