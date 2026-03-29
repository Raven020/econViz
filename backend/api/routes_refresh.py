# Refresh routes — POST /internal/refresh
# Triggers data fetch, HMM retrain, and Monte Carlo simulation.

import logging
from datetime import timedelta

import numpy as np
import requests
from fastapi import APIRouter, Depends
import duckdb

from backend.api.deps import get_write_conn
from backend.config import (
    CRYPTO_IDS,
    market_date,
    FRED_SERIES,
    HMM_LOOKBACK_YEARS,
    HMM_N_STATES,
    MC_HORIZON_DAYS,
    MC_N_PATHS,
    YAHOO_TICKERS,
)
from backend.data import coingecko, fred, yahoo
from backend.data.store import (
    get_latest_date,
    get_latest_macro_date,
    write_price_data,
    write_macro_data,
    read_all_returns,
    read_macro_matrix,
    read_latest_prices,
    write_regime,
    write_montecarlo,
)
from backend.models.hmm import build_feature_matrix, train_hmm, decode_regime, get_transition_matrix
from backend.models.montecarlo import simulate_paths, returns_to_prices, compute_percentiles
from backend.models.regime import label_regime, blend_regime_params

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal")


def _fetch_and_store_prices(conn, tickers, fetch_fn, lookback_start, today):
    """Common pattern for Yahoo and CoinGecko price fetching."""
    for name, identifier in tickers.items():
        try:
            latest = get_latest_date(conn, name)
            start = (latest + timedelta(days=1)) if latest else lookback_start
            if start <= today:
                df = fetch_fn(identifier, start, today)
                if not df.empty:
                    write_price_data(conn, name, df)
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning("Fetch failed for %s: %s", name, e)


def _fetch_and_store_macro(conn, series_map, lookback_start, today):
    """Common pattern for FRED macro data fetching with incremental dates."""
    for name, series_id in series_map.items():
        try:
            latest = get_latest_macro_date(conn, name)
            start = (latest + timedelta(days=1)) if latest else lookback_start
            if start <= today:
                df = fred.fetch(series_id, start, today)
                if not df.empty:
                    write_macro_data(conn, name, df)
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning("FRED fetch failed for %s: %s", name, e)


@router.post("/refresh")
def refresh(conn: duckdb.DuckDBPyConnection = Depends(get_write_conn)):
    today = market_date()
    lookback_start = today - timedelta(days=365 * HMM_LOOKBACK_YEARS)

    _fetch_and_store_prices(conn, YAHOO_TICKERS, yahoo.fetch, lookback_start, today)
    _fetch_and_store_prices(conn, CRYPTO_IDS, coingecko.fetch, lookback_start, today)
    _fetch_and_store_macro(conn, FRED_SERIES, lookback_start, today)

    # Train HMM and detect regime
    returns_df = read_all_returns(conn, lookback_start, today)
    if returns_df.empty:
        return {"status": "refreshed", "regime": None}

    n_assets = len(returns_df.columns)

    # Build macro feature matrix aligned to returns dates
    macro_df = read_macro_matrix(conn, lookback_start, today)
    if not macro_df.empty:
        # Align macro data to the same date index as returns, forward-fill gaps
        macro_aligned = macro_df.reindex(returns_df.index).ffill().fillna(0)
        macro_matrix = macro_aligned.values
    else:
        # Fallback to zeros if no macro data available
        macro_matrix = np.zeros((len(returns_df), 1))

    features = build_feature_matrix(returns_df.values, macro_matrix)

    model = train_hmm(features, n_states=HMM_N_STATES)
    current_state, state_probs = decode_regime(model, features)
    regime_label = label_regime(current_state)
    confidence = float(state_probs[current_state])
    transition_matrix = get_transition_matrix(model)

    write_regime(conn, regime_label, confidence, transition_matrix)

    # Run Monte Carlo per instrument — use only the asset columns from blended params
    blended_means, blended_cov = blend_regime_params(model, state_probs)
    latest_prices_df = read_latest_prices(conn)

    for _, row in latest_prices_df.iterrows():
        ticker = row["instrument"]
        col_idx = returns_df.columns.get_loc(ticker) if ticker in returns_df.columns else None
        if col_idx is None:
            continue

        # Extract only the asset's mean and variance (skip macro columns)
        asset_mean = np.array([blended_means[col_idx]])
        asset_cov = np.array([[blended_cov[col_idx, col_idx]]])
        current_price = np.array([row["close"]])

        return_paths = simulate_paths(asset_mean, asset_cov, n_paths=MC_N_PATHS, horizon=MC_HORIZON_DAYS)
        price_paths = returns_to_prices(current_price, return_paths)
        cones = compute_percentiles(price_paths)

        projection_dict = {p: vals[:, 0].tolist() for p, vals in cones.items()}
        write_montecarlo(conn, ticker, projection_dict)

    return {
        "status": "refreshed",
        "regime": {
            "label": regime_label,
            "confidence": confidence,
        },
    }
