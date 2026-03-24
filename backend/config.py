# Configuration — instrument lists, API keys, DB path, constants.

import os

# --- Database ---
DB_PATH = os.getenv("ECON_VIZ_DB_PATH", "data/econ_viz.duckdb")

# --- API Keys ---
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

# --- Instruments ---
YAHOO_TICKERS = {
    "SPY": "SPY",
    "IWM": "IWM",
    "QQQ": "QQQ",
    "DIA": "DIA",
    "CRUDE_OIL": "CL=F",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "NATURAL_GAS": "NG=F",
    "COPPER": "HG=F",
    "WHEAT": "ZW=F",
    "VIX": "^VIX",
    "DXY": "DX-Y.NYB",
}

CRYPTO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
}

FRED_SERIES = {
    "FED_FUNDS": "FEDFUNDS",
    "INFLATION_5Y": "T5YIE",
    "JOBLESS_CLAIMS": "ICSA",
    "YIELD_SPREAD_2S10S": "T10Y2Y",
}

# --- Model Parameters ---
HMM_LOOKBACK_YEARS = 5
HMM_N_STATES = 5
MC_N_PATHS = 10_000
MC_HORIZON_DAYS = 30

# --- Server ---
PYTHON_API_PORT = 8000
