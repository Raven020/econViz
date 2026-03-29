# Entry point — starts the FastAPI server via uvicorn.
# Usage: python -m backend.main

import logging

import uvicorn
from fastapi import FastAPI, HTTPException

from backend.api import routes_dashboard, routes_drilldown, routes_montecarlo, routes_refresh
from backend.config import DB_PATH
from backend.data.store import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="EconViz Analytics Backend")

app.include_router(routes_dashboard.router)
app.include_router(routes_drilldown.router)
app.include_router(routes_montecarlo.router)
app.include_router(routes_refresh.router)


@app.get("/health")
def health():
    try:
        conn = init_db(DB_PATH)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"unhealthy: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
