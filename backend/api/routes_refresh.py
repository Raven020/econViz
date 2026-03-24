# Refresh routes — POST /internal/refresh
# Triggers data fetch, HMM retrain, and Monte Carlo simulation.

from datetime import date, timedelta

import numpy as np
from fastapi import APIRouter

from backend.config import (
    CRYPTO_IDS,
    DB_PATH,
    FRED_SERIES,
    HMM_LOOKBACK_YEARS,
    HMM_N_STATES,
    MC_HORIZON_DAYS,
    MC_N_PATHS,
    YAHOO_TICKERS,
)
from backend.data import coingecko, fred, yahoo
from backend.data.store import (
    init_db,
    get_latest_date,
    write_price_data,
    write_macro_data,
    read_all_returns,
    read_latest_prices,
    write_regime,
    write_montecarlo,
)
from backend.models.hmm import build_feature_matrix, train_hmm, decode_regime, get_transition_matrix
from backend.models.montecarlo import simulate_paths, returns_to_prices, compute_percentiles
from backend.models.regime import label_regime, blend_regime_params

router = APIRouter(prefix="/internal")


@router.post("/refresh")
def refresh():
    conn = init_db(DB_PATH)
    today = date.today()
    lookback_start = today - timedelta(days=365 * HMM_LOOKBACK_YEARS)

    # Fetch Yahoo data
    for name, ticker in YAHOO_TICKERS.items():
        latest = get_latest_date(conn, name)
        start = (latest + timedelta(days=1)) if latest else lookback_start
        if start <= today:
            df = yahoo.fetch(ticker, start, today)
            if not df.empty:
                write_price_data(conn, name, df)

    # Fetch crypto data
    for name, coin_id in CRYPTO_IDS.items():
        latest = get_latest_date(conn, name)
        start = (latest + timedelta(days=1)) if latest else lookback_start
        if start <= today:
            df = coingecko.fetch(coin_id, start, today)
            if not df.empty:
                write_price_data(conn, name, df)

    # Fetch FRED macro data
    for name, series_id in FRED_SERIES.items():
        df = fred.fetch(series_id, lookback_start, today)
        if not df.empty:
            write_macro_data(conn, name, df)

    # Train HMM and detect regime
    returns_df = read_all_returns(conn, lookback_start, today)
    if returns_df.empty:
        conn.close()
        return {"status": "refreshed", "regime": None}

    returns_matrix = returns_df.values
    macro_placeholder = np.zeros((returns_matrix.shape[0], 1))
    features = build_feature_matrix(returns_matrix, macro_placeholder)

    model = train_hmm(features, n_states=HMM_N_STATES)
    current_state, state_probs = decode_regime(model, features)
    regime_label = label_regime(current_state)
    confidence = float(state_probs[current_state])
    transition_matrix = get_transition_matrix(model)

    write_regime(conn, regime_label, confidence, transition_matrix)

    # Run Monte Carlo per instrument
    blended_means, blended_cov = blend_regime_params(model, state_probs)
    latest_prices_df = read_latest_prices(conn)

    for _, row in latest_prices_df.iterrows():
        ticker = row["instrument"]
        col_idx = returns_df.columns.get_loc(ticker) if ticker in returns_df.columns else None
        if col_idx is None:
            continue

        asset_mean = np.array([blended_means[col_idx]])
        asset_cov = np.array([[blended_cov[col_idx, col_idx]]])
        current_price = np.array([row["close"]])

        return_paths = simulate_paths(asset_mean, asset_cov, n_paths=MC_N_PATHS, horizon=MC_HORIZON_DAYS)
        price_paths = returns_to_prices(current_price, return_paths)
        cones = compute_percentiles(price_paths)

        projection_dict = {p: vals[:, 0].tolist() for p, vals in cones.items()}
        write_montecarlo(conn, ticker, projection_dict)

    conn.close()
    return {
        "status": "refreshed",
        "regime": {
            "label": regime_label,
            "confidence": confidence,
        },
    }
