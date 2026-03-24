# Entry point — starts the FastAPI server via uvicorn.
# Usage: python -m backend.main

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="EconViz Analytics Backend")

# TODO: register route modules
# from backend.api import routes_dashboard, routes_drilldown, routes_montecarlo, routes_refresh

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
