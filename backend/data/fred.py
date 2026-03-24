# FRED API data fetcher.
# Pulls Fed Funds Rate, inflation expectations (T5YIE),
# initial jobless claims, and yield curve spread (T10Y2Y).

from fredapi import Fred
import pandas as pd
from backend.config import FRED_API_KEY


def fetch(series_id, start_date, end_date):
    """
    Args:
        series_id (str): FRED series ID (e.g. "FEDFUNDS", "T5YIE", "ICSA", "T10Y2Y")
        start_date (str or datetime.date): start of date range
        end_date (str or datetime.date): end of date range

    Process:
        Initializes a Fred client with the API key from config.
        Calls get_series() to pull the data for the given range.
        FRED returns a pandas Series indexed by date — converts it to a
        DataFrame with date and value columns. Drops any NaN rows
        (FRED sometimes has gaps on holidays/weekends).

    Returns:
        pd.DataFrame: columns — date, value
    """
    fred = Fred(api_key=FRED_API_KEY)
    series = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)

    df = series.reset_index()
    df.columns = ["date", "value"]
    df = df.dropna(subset=["value"])

    return df
