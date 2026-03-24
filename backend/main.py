# Entry point — starts the FastAPI server via uvicorn.
# Usage: python -m backend.main

import uvicorn
from fastapi import FastAPI

from backend.api import routes_dashboard, routes_drilldown, routes_montecarlo, routes_refresh

app = FastAPI(title="EconViz Analytics Backend")

app.include_router(routes_dashboard.router)
app.include_router(routes_drilldown.router)
app.include_router(routes_montecarlo.router)
app.include_router(routes_refresh.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
