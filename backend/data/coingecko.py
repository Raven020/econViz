# CoinGecko API data fetcher.
# Pulls price, volume, and 24h volume change for BTC, ETH, and SOL.

import requests
import pandas as pd
from backend.config import COINGECKO_API_KEY


COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


def fetch(coin_id, start_date, end_date):
    """
    Args:
        coin_id (str): CoinGecko coin ID (e.g. "bitcoin", "ethereum", "solana")
        start_date (str or datetime.date): start of date range
        end_date (str or datetime.date): end of date range

    Process:
        Converts start/end dates to unix timestamps.
        Calls CoinGecko /coins/{id}/market_chart/range endpoint to get
        daily price and volume data for the given range.
        Parses the JSON response into a DataFrame with date, open, high, low,
        close, volume columns. CoinGecko returns aggregated daily data so
        open/high/low are set equal to the daily price point.

    Returns:
        pd.DataFrame: columns — date, open, high, low, close, volume
    """
    start_ts = int(pd.Timestamp(start_date).timestamp())
    end_ts = int((pd.Timestamp(end_date) + pd.Timedelta(days=1)).timestamp())

    headers = {}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY

    response = requests.get(
        f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart/range",
        params={"vs_currency": "usd", "from": start_ts, "to": end_ts},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(f"CoinGecko returned unexpected format: {type(data)}")
    if "prices" not in data or "total_volumes" not in data:
        raise ValueError(f"CoinGecko response missing required fields. Keys: {list(data.keys())}")

    prices = data["prices"]
    volumes = data["total_volumes"]

    if not prices:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

    df = pd.DataFrame(prices, columns=["timestamp", "close"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
    df["open"] = df["close"]
    df["high"] = df["close"]
    df["low"] = df["close"]

    vol_df = pd.DataFrame(volumes, columns=["timestamp", "volume"])
    vol_df["date"] = pd.to_datetime(vol_df["timestamp"], unit="ms").dt.date

    df = df.merge(vol_df[["date", "volume"]], on="date", how="left")
    df = df.drop_duplicates(subset="date", keep="last")

    return df[["date", "open", "high", "low", "close", "volume"]]
