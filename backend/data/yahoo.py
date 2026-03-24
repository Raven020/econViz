# Yahoo Finance data fetcher via yfinance.
# Pulls price, volume, daily high/low for equities (SPY, IWM, QQQ, DIA),
# commodities (CL=F, GC=F, SI=F, NG=F, HG=F, ZW=F), VIX (^VIX),
# and DXY (DX-Y.NYB).

import yfinance as yf
import pandas as pd


def fetch(ticker, start_date, end_date):
    """
    Args:
        ticker (str): Yahoo Finance ticker symbol (e.g. "SPY", "GC=F", "^VIX")
        start_date (str or datetime.date): start of date range (inclusive)
        end_date (str or datetime.date): end of date range (inclusive)

    Process:
        Calls yfinance Ticker.history() to pull OHLCV data for the given range.
        Resets the index so date becomes a regular column instead of the index.
        Renames columns to lowercase to match the DB schema.

    Returns:
        pd.DataFrame: columns — date, open, high, low, close, volume
    """
    df = yf.Ticker(ticker).history(start=start_date, end=end_date)
    df = df.reset_index()
    df = df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })
    return df[["date", "open", "high", "low", "close", "volume"]]
